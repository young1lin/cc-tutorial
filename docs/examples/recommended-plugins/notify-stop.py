#!/usr/bin/env python3
"""
Claude Code StopHook 通知脚本
当 Claude Code 会话停止时发送系统桌面通知
零依赖 - 仅使用系统自带命令
"""

import sys
import json
import os
import subprocess
from pathlib import Path
from datetime import datetime


class NotificationMessage:
    def __init__(self, session_id: str, project: str, reason: str, terminal: str,
                 session_start: str = "", session_duration: str = "",
                 last_task: str = "", model: str = "", slug: str = "",
                 last_tool: str = "", last_file: str = "", last_user_input: str = ""):
        self.session_id = session_id
        self.project = project
        self.reason = reason
        self.terminal = terminal
        self.session_start = session_start
        self.session_duration = session_duration
        self.last_task = last_task
        self.model = model
        self.slug = slug
        self.last_tool = last_tool
        self.last_file = last_file
        self.last_user_input = last_user_input


def detect_terminal() -> str:
    """检测当前终端类型"""
    terminal = "Unknown"
    if os.environ.get('WT_SESSION'):
        terminal = "Windows Terminal"
    elif os.environ.get('TERM_PROGRAM'):
        term_prog = os.environ.get('TERM_PROGRAM', '')
        if 'vscode' in term_prog.lower():
            terminal = "VS Code"
        else:
            terminal = term_prog
    shell = os.environ.get('SHELL', '')
    if terminal == "Unknown":
        if 'powershell' in shell.lower():
            terminal = "PowerShell"
        elif 'bash' in shell.lower():
            terminal = "Bash"
    return terminal


def extract_project_name(cwd: str, transcript_path: str = None) -> str:
    """从 cwd 提取项目名称"""
    if cwd:
        project = Path(cwd).name
        if project and project != str(Path(cwd)):
            return project
    if transcript_path:
        transcript_name = Path(transcript_path).stem
        if transcript_name:
            return transcript_name
    return "Unknown"


def extract_transcript_info(transcript_path: str) -> dict:
    """从 transcript 文件提取有用信息"""
    info = {
        "session_start": "",
        "session_duration": "",
        "last_task": "",
        "model": "",
        "slug": "",
        "last_user_input": "",
        "last_tool": "",
        "last_file": ""
    }

    if not transcript_path:
        return info

    try:
        transcript_file = Path(transcript_path)
        if not transcript_file.exists():
            return info

        with open(transcript_file, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()

        first_timestamp = None
        last_timestamp = None
        last_user_content = ""
        models = set()

        # 从最后往前读取，获取最后一条 assistant 消息的内容（Claude 的回复）
        for line in reversed(lines):
            if not line.strip():
                continue
            try:
                data = json.loads(line)
                msg_type = data.get("type", "")

                # 查找最后一条 assistant 消息
                if msg_type == "assistant":
                    message = data.get("message", {})
                    content = message.get("content", [])

                    # content 是列表格式
                    if content and isinstance(content, list):
                        for item in content:
                            if item.get("type") == "text":
                                text = item.get("text", "").strip()
                                if text:
                                    # 取前30个字符作为任务描述
                                    last_user_content = text[:30] + "..." if len(text) > 30 else text
                                    break
                    if last_user_content:
                        break  # 找到了，退出循环
            except (json.JSONDecodeError, KeyError):
                pass


        # 新增：提取用户输入、工具名、文件名
        # 从后往前提取最后一条用户输入
        for line in reversed(lines):
            if not line.strip():
                continue
            try:
                data = json.loads(line)
                if data.get('type') == 'user':
                    content = data.get('message', {}).get('content', '')
                    if isinstance(content, str) and content.strip():
                        # 跳过系统消息
                        if content.strip() not in ['[Request interrupted by user]', '[System]']:
                            info["last_user_input"] = content[:50] + "..." if len(content) > 50 else content
                            break
            except (json.JSONDecodeError, KeyError):
                pass

        # 从后往前提取最后使用的工具和文件
        for line in reversed(lines):
            if not line.strip():
                continue
            try:
                data = json.loads(line)
                if data.get('type') == 'assistant':
                    content = data.get('message', {}).get('content', [])
                    for item in reversed(content):
                        if item.get('type') == 'tool_use':
                            info["last_tool"] = item.get('name', '')
                            input_data = item.get('input', {})
                            # 提取文件路径
                            for key in ['file_path', 'path', 'filePath']:
                                if key in input_data and input_data[key]:
                                    info["last_file"] = Path(input_data[key]).name
                            break
                    if info["last_tool"]:
                        break
            except (json.JSONDecodeError, KeyError):
                pass

        # 第二遍遍历：获取时间戳和模型信息
        for line in lines:
            if not line.strip():
                continue
            try:
                data = json.loads(line)
                timestamp = data.get("timestamp", "")
                if timestamp:
                    if not first_timestamp:
                        first_timestamp = timestamp
                    last_timestamp = timestamp
                slug = data.get("slug", "")
                if slug and not info["slug"]:
                    info["slug"] = slug
                msg_type = data.get("type", "")
                if msg_type == "assistant":
                    message = data.get("message", {})
                    model = message.get("model", "")
                    if model:
                        models.add(model)
            except (json.JSONDecodeError, KeyError):
                continue

        if first_timestamp and last_timestamp:
            try:
                start = datetime.fromisoformat(first_timestamp.replace('Z', '+00:00'))
                end = datetime.fromisoformat(last_timestamp.replace('Z', '+00:00'))
                duration = end - start
                total_seconds = int(duration.total_seconds())
                if total_seconds < 60:
                    duration_str = f"{total_seconds}s"
                elif total_seconds < 3600:
                    minutes = total_seconds // 60
                    duration_str = f"{minutes}m"
                else:
                    hours = total_seconds // 3600
                    minutes = (total_seconds % 3600) // 60
                    duration_str = f"{hours}h{minutes}m" if minutes > 0 else f"{hours}h"
                info["session_duration"] = duration_str
                info["session_start"] = start.strftime("%H:%M")
            except:
                pass

        info["last_task"] = last_user_content
        info["model"] = ", ".join(models) if models else ""

    except Exception:
        pass

    return info


def build_notification(data: dict) -> NotificationMessage:
    """构建 NotificationMessage 对象"""
    session_id = data.get("session_id", "unknown")
    transcript_path = data.get("transcript_path", "")
    cwd = data.get("cwd", "")
    reason = data.get("reason", "Session stopped")

    # 尝试获取用户输入：prompt 或 user_prompt
    user_input = data.get("prompt") or data.get("user_prompt") or ""

    project = extract_project_name(cwd, transcript_path)
    terminal = detect_terminal()
    transcript_info = extract_transcript_info(transcript_path)

    # 如果有当前用户输入，优先使用；否则用历史的 last_task
    last_task = user_input if user_input else transcript_info.get("last_task", "")

    return NotificationMessage(
        session_id=session_id,
        project=project,
        reason=reason,
        terminal=terminal,
        session_start=transcript_info.get("session_start", ""),
        session_duration=transcript_info.get("session_duration", ""),
        last_task=last_task,
        model=transcript_info.get("model", ""),
        slug=transcript_info.get("slug", ""),
        last_tool=transcript_info.get("last_tool", ""),
        last_file=transcript_info.get("last_file", ""),
        last_user_input=transcript_info.get("last_user_input", "")
    )


def escape_ps_string(s: str) -> str:
    """转义 PowerShell 字符串中的特殊字符"""
    return s.replace('\\', '\\\\').replace('"', '`"').replace('$', '`$').replace('`', '``')

def notify_windows(notification: NotificationMessage) -> bool:
    """Windows 平台通知 - 使用环境变量传递数据"""
    import base64
    import textwrap

    # 准备数据并转义特殊字符
    title_text = escape_ps_string(notification.project + " - Session Complete")

    info_lines = []
    if notification.session_start and notification.session_duration:
        info_lines.append(f"Time:  {notification.session_start} - {notification.session_duration}")
    if notification.model:
        info_lines.append(f"Model: {notification.model}")

    # 智能优先级显示：用户输入 > 工具+文件 > Assistant文本
    # 优先级 1: 用户输入
    if notification.last_user_input:
        info_lines.append(f"Input: {notification.last_user_input}")
    # 优先级 2: 工具 + 文件
    elif notification.last_tool:
        tool_info = f"Action: {notification.last_tool}"
        if notification.last_file:
            tool_info += f" -> {notification.last_file}"
        info_lines.append(tool_info)
    # 优先级 3: Assistant 文本（后备）
    elif notification.last_task:
        info_lines.append(f"Last: {notification.last_task}")

    info_text = escape_ps_string("\r\n".join(info_lines))  # CRLF for Windows

    # 根据行数调整信息框高度
    line_count = len(info_lines)
    info_height = 25 + line_count * 22  # 每行22px，基础25px
    btn_y = 55 + info_height + 15  # 按钮在信息框下方15px

    # Windows窗体标题栏约38px，按钮高度38px，底部留25px
    form_height = btn_y + 38 + 25 + 38  # 按钮Y + 按钮高度 + 底部边距 + 标题栏

    # 使用 Base64 编码整个脚本
    raw_script = f'''
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

$form = New-Object System.Windows.Forms.Form
$form.Text = "Claude Code"
$form.Size = New-Object System.Drawing.Size(520, {form_height})
$form.StartPosition = "CenterScreen"
$form.FormBorderStyle = "FixedDialog"
$form.TopMost = $true
$form.BackColor = [System.Drawing.Color]::FromArgb(28, 28, 36)
$form.ShowInTaskbar = $false

$title = New-Object System.Windows.Forms.Label
$title.Text = "{title_text}"
$title.Location = "30, 15"
$title.Size = "460, 28"
$title.Font = New-Object System.Drawing.Font("Segoe UI", 11, [System.Drawing.FontStyle]::Bold)
$title.ForeColor = [System.Drawing.Color]::FromArgb(100, 180, 255)
$form.Controls.Add($title)

$info = New-Object System.Windows.Forms.TextBox
$info.Text = "{info_text}"
$info.Location = "40, 55"
$info.Size = "440, {info_height}"
$info.Font = New-Object System.Drawing.Font("Consolas", 9)
$info.ForeColor = [System.Drawing.Color]::FromArgb(200, 200, 200)
$info.BackColor = [System.Drawing.Color]::FromArgb(38, 38, 48)
$info.Multiline = $true
$info.ReadOnly = $true
$info.BorderStyle = "None"
$form.Controls.Add($info)

$btn = New-Object System.Windows.Forms.Button
$btn.Text = "Close 30s"
$btn.Location = "170, {btn_y}"
$btn.Size = "180, 38"
$btn.Font = New-Object System.Drawing.Font("Segoe UI", 9)
$btn.TextAlign = "MiddleCenter"
$btn.Padding = 0
$btn.BackColor = [System.Drawing.Color]::FromArgb(70, 140, 220)
$btn.ForeColor = [System.Drawing.Color]::White
$btn.FlatStyle = "Standard"
$btn.Add_Click({{ $form.Close() }})
$form.Controls.Add($btn)

$countdown = 30
$timer = New-Object System.Windows.Forms.Timer
$timer.Interval = 1000
$timer.Add_Tick({{
    $cd = Get-Variable -Name countdown -Scope 1 -ValueOnly
    $cd--
    Set-Variable -Name countdown -Scope 1 -Value $cd
    if ($cd -le 0) {{
        $form.Close()
    }} else {{
        $btn.Text = "Close $cd"
    }}
}})
$timer.Start()

$form.ShowDialog() | Out-Null
exit 0
'''

    # Base64 编码
    encoded = base64.b64encode(raw_script.encode('utf-16-le')).decode('ascii')

    try:
        subprocess.run(
            ["powershell.exe", "-NoProfile", "-EncodedCommand", encoded],
            capture_output=True,
            text=True,
            timeout=40
        )
        return True
    except subprocess.TimeoutExpired:
        return True
    except Exception as e:
        print(f"[StopHook] Exception: {e}", file=sys.stderr)
        return False


def notify_macos(notification: NotificationMessage) -> bool:
    """macOS 平台通知"""
    # 智能优先级显示：用户输入 > 工具+文件 > Assistant文本
    display_text = notification.last_user_input or notification.last_task
    if notification.last_tool and not notification.last_user_input:
        display_text = f"{notification.last_tool}"
        if notification.last_file:
            display_text += f" -> {notification.last_file}"

    # 截断过长的文本
    if display_text and len(display_text) > 50:
        display_text = display_text[:50] + "..."

    notification_text = f"{notification.project}"
    if display_text:
        notification_text += f": {display_text}"
    elif notification.session_duration:
        notification_text += f" - {notification.session_duration}"

    script = f'display notification "{notification_text}" with title "Claude Code" sound name "Glass"'
    try:
        subprocess.run(["osascript", "-e", script], capture_output=True, text=True, timeout=5)
        return True
    except Exception:
        print(f"[Claude Code] {notification.project} session complete", file=sys.stderr)
        return True


def notify_linux(notification: NotificationMessage) -> bool:
    """Linux 平台通知"""
    # 智能优先级显示：用户输入 > 工具+文件 > Assistant文本
    display_text = notification.last_user_input or notification.last_task
    if notification.last_tool and not notification.last_user_input:
        display_text = f"{notification.last_tool}"
        if notification.last_file:
            display_text += f" -> {notification.last_file}"

    # 截断过长的文本
    if display_text and len(display_text) > 50:
        display_text = display_text[:50] + "..."

    body_text = f"{notification.project}"
    if display_text:
        body_text += f": {display_text}"
    elif notification.session_duration:
        body_text += f" ({notification.session_duration})"

    try:
        subprocess.run([
            "notify-send", "--icon=dialog-info", "--app-name=Claude Code",
            "Session Complete", body_text
        ], capture_output=True, text=True, timeout=5)
        return True
    except Exception:
        print(f"[Claude Code] {notification.project} session complete", file=sys.stderr)
        return True


def send_notification(notification: NotificationMessage) -> bool:
    """根据平台发送通知"""
    platform = sys.platform
    if platform == "win32":
        return notify_windows(notification)
    elif platform == "darwin":
        return notify_macos(notification)
    elif platform.startswith("linux"):
        return notify_linux(notification)
    return False


def main():
    """主函数 - 始终返回 0 以避免 hook 执行失败"""
    try:
        data = read_stdin_json() if 'read_stdin_json' in globals() else {}
        notification = build_notification(data)
        send_notification(notification)
    except Exception as e:
        # 即使出错也打印错误但返回 0，避免 hook 链失败
        print(f"[StopHook] Error: {e}", file=sys.stderr)
    return 0


def read_stdin_json() -> dict:
    """从 stdin 读取 JSON 数据"""
    try:
        data = sys.stdin.read()
        if not data:
            return {}
        return json.loads(data)
    except json.JSONDecodeError:
        return {}


if __name__ == "__main__":
    sys.exit(main())
