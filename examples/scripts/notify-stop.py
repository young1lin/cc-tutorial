#!/usr/bin/env python3
"""
Claude Code Stop-hook notification script.

Sends a desktop notification when Claude Code finishes a turn (the Stop
event). Zero dependencies - uses only OS built-in commands: a PowerShell
toast on Windows, osascript on macOS, notify-send on Linux.

The toast shows: project name, finish time, elapsed time since your last
message, the model(s) used, and the last user input (truncated to 80 chars).

Register it as a Stop hook in ~/.claude/settings.json:

    {
      "hooks": {
        "Stop": [
          {
            "hooks": [
              {
                "type": "command",
                "command": "python C:/path/to/notify-stop.py",
                "timeout": 45
              }
            ]
          }
        ]
      }
    }
"""

import sys
import json
import os
import subprocess
from pathlib import Path
from datetime import datetime


class NotificationMessage:
    def __init__(self, project: str, model: str = "",
                 last_user_input: str = "", elapsed: str = ""):
        self.project = project
        self.model = model
        self.last_user_input = last_user_input
        self.elapsed = elapsed


def extract_project_name(cwd: str, transcript_path: str = None) -> str:
    """Extract the project name from cwd, falling back to the transcript name."""
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
    """Extract the last user input from the transcript tail in one reverse scan."""
    info = {
        "last_user_input": "",
        "last_user_input_time": "",
        "model": "",
    }

    if not transcript_path:
        return info

    try:
        f = Path(transcript_path)
        if not f.exists():
            return info

        # Read only the last 512KB instead of loading the whole file.
        tail_size = 512 * 1024
        file_size = f.stat().st_size

        with open(f, 'r', encoding='utf-8', errors='ignore') as fh:
            if file_size > tail_size:
                fh.seek(file_size - tail_size)
                fh.readline()  # skip the possibly truncated first line
            lines = fh.readlines()

        _skip = (
            '<local-command-', '<command-name>', '<local-command-stdout',
            '[Request interrupted by user]', '[System]',
            'This session is being continued',
        )
        models = set()

        for line in reversed(lines):
            if not line.strip():
                continue
            try:
                data = json.loads(line)
            except (json.JSONDecodeError, KeyError):
                continue

            t = data.get('type', '')

            # User input: prefer last-prompt entries, fall back to plain-string user messages.
            # Note: last-prompt entries carry no timestamp, so when the most recent
            # input is a last-prompt, elapsed stays empty (no reliable time source).
            if not info['last_user_input']:
                if t == 'last-prompt':
                    p = data.get('lastPrompt', '').strip()
                    if p:
                        info['last_user_input'] = p[:80] + '...' if len(p) > 80 else p
                elif t == 'user':
                    c = data.get('message', {}).get('content', '')
                    if isinstance(c, str) and c.strip() and not c.strip().startswith(_skip):
                        info['last_user_input'] = c[:80] + '...' if len(c) > 80 else c

            # Timestamp of the last user message (used to compute elapsed time).
            if not info['last_user_input_time'] and t == 'user':
                ts = data.get('timestamp', '')
                if ts:
                    info['last_user_input_time'] = ts

            # Collect model names along the way (negligible cost).
            if t == 'assistant':
                m = data.get('message', {}).get('model', '')
                if m:
                    models.add(m)

            # Stop scanning once the user input is found.
            if info['last_user_input']:
                break

        info['model'] = ', '.join(models) if models else ''

    except Exception:
        # A notification hook must never fail the session; degrade silently.
        pass

    return info


def find_latest_transcript(cwd: str) -> str:
    """Locate the most recent transcript file for cwd when stdin is empty."""
    if not cwd:
        cwd = os.getcwd()
    # Convert cwd to the claude projects directory-name format: D:\path -> D--path
    dir_name = cwd.replace(":", "-").replace("\\", "-").replace("/", "-")
    projects_dir = Path.home() / ".claude" / "projects" / dir_name
    if not projects_dir.exists():
        return ""
    # Pick the most recently modified .jsonl file (excluding the subagents subdirectory).
    candidates = [f for f in projects_dir.glob("*.jsonl") if "subagents" not in str(f)]
    if not candidates:
        return ""
    latest = max(candidates, key=lambda f: f.stat().st_mtime)
    return str(latest)


def _oneline(text: str) -> str:
    """Collapse newlines and whitespace runs to single spaces.

    Notification fields are single-line display strings built from
    user-controlled transcript content. Stripping newlines closes two
    injection paths: a newline followed by ``'@`` can no longer start a line
    and terminate the Windows PowerShell here-string early, and multi-line
    content cannot smuggle a second AppleScript or notify-send statement.
    """
    return " ".join(text.split()) if text else ""


def _applescript_escape(text: str) -> str:
    """Escape a string for embedding in an AppleScript double-quoted literal."""
    return text.replace("\\", "\\\\").replace('"', '\\"')


def build_notification(data: dict) -> NotificationMessage:
    """Build the NotificationMessage from the hook's stdin payload."""
    transcript_path = data.get("transcript_path", "")
    cwd = data.get("cwd", "")

    # Auto-discover the transcript when stdin was empty.
    if not transcript_path:
        transcript_path = find_latest_transcript(cwd)

    project = extract_project_name(cwd, transcript_path)
    transcript_info = extract_transcript_info(transcript_path)

    # Elapsed time from the user's last message to the Stop trigger.
    elapsed = ""
    user_msg_time = transcript_info.get("last_user_input_time", "")
    if user_msg_time:
        try:
            start = datetime.fromisoformat(user_msg_time.replace('Z', '+00:00'))
            total_seconds = int((datetime.now(start.tzinfo) - start).total_seconds())
            if total_seconds < 60:
                elapsed = f"{total_seconds}s"
            elif total_seconds < 3600:
                elapsed = f"{total_seconds // 60}m{total_seconds % 60}s"
            else:
                elapsed = f"{total_seconds // 3600}h{(total_seconds % 3600) // 60}m"
        except Exception:
            pass

    return NotificationMessage(
        project=_oneline(project),
        model=_oneline(transcript_info.get("model", "")),
        last_user_input=_oneline(transcript_info.get("last_user_input", "")),
        elapsed=elapsed
    )


def notify_windows(notification: NotificationMessage) -> bool:
    """Windows 10 Toast Notification - sends to notification center."""
    from datetime import datetime as _dt

    # Build the body text lines
    body_lines = []
    now_str = _dt.now().strftime("%H:%M:%S")
    if notification.elapsed:
        body_lines.append(f"Done: {now_str} ({notification.elapsed})")
    else:
        body_lines.append(f"Done: {now_str}")
    if notification.model:
        body_lines.append(f"Model: {notification.model}")
    if notification.last_user_input:
        body_lines.append(f"Input: {notification.last_user_input}")

    # Escape XML special characters for PowerShell here-string
    def esc(s):
        return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', '&quot;')

    title = esc("Claude Code - " + notification.project)
    # Each line as a separate <text> element for proper line breaks in toast
    text_elements = "\n".join(f"        <text>{esc(line)}</text>" for line in body_lines)

    # Toast XML template (ToastGeneric works on Win10 1607+)
    toast_xml = f"""<toast duration="short">
  <visual>
    <binding template="ToastGeneric">
      <text>{title}</text>
{text_elements}
    </binding>
  </visual>
  <audio src="ms-winsoundevent:Notification.Default"/>
</toast>"""

    # PowerShell: load WinRT types, auto-detect AUMID from registry, send toast
    ps_script = r'''
$ErrorActionPreference = "SilentlyContinue"

# Load WinRT types needed for toast notifications
[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
[Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom, ContentType = WindowsRuntime] | Out-Null

# Auto-detect AUMID from registry (works for PowerShell, VS Code, Windows Terminal, etc.)
$appId = ""
$regPath = "HKCU:\Software\Microsoft\Windows\CurrentVersion\\Notifications\Settings"
if (Test-Path $regPath) {
    # Prefer Windows Terminal, then PowerShell 7, then Windows PowerShell
    $priority = @("Microsoft.WindowsTerminal", "Microsoft.PowerShell", "Microsoft.PowerShellPreview")
    foreach ($p in $priority) {
        $match = Get-ChildItem $regPath -ErrorAction SilentlyContinue |
                 Where-Object { $_.PSChildName -like "$p*" } |
                 Select-Object -First 1
        if ($match) {
            $appId = $match.PSChildName
            # Check if it has an AppUserModelId subkey with a valid value
            $aumidPath = Join-Path $regPath $appId
            $aumidVal = (Get-ItemProperty -Path $aumidPath -Name "AppUserModelId" -ErrorAction SilentlyContinue).AppUserModelId
            if ($aumidVal) {
                $appId = $aumidVal
            }
            break
        }
    }
}

# Fallback AUMIDs to try if registry lookup failed
if (-not $appId) {
    $candidates = @(
        "Microsoft.WindowsTerminal_8wekyb3d8bbwe!App",
        "{1AC14E77-02E7-4E5D-B744-2EB1AE5198B7}\WindowsPowerShell\v1.0\powershell.exe"
    )
    $appId = $candidates[0]
}

# Parse the toast XML. Single-quoted here-string (@'...'@) so the XML content
# is literal -- a double-quoted @"..."@ would interpolate $variables and let
# user-controlled input (project name, last prompt) execute as PowerShell.
$xmlContent = @'
TOAST_XML_PLACEHOLDER
'@

$xml = New-Object Windows.Data.Xml.Dom.XmlDocument
$xml.LoadXml($xmlContent)

# Try detected AUMID first, then fallbacks
$notifier = $null
$allIds = @($appId) + @(
    "Microsoft.WindowsTerminal_8wekyb3d8bbwe!App",
    "{1AC14E77-02E7-4E5D-B744-2EB1AE5198B7}\WindowsPowerShell\v1.0\powershell.exe"
) | Select-Object -Unique

foreach ($id in $allIds) {
    try {
        $notifier = [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier($id)
        # Verify it can actually create a notification (some AUMIDs silently succeed but don't display)
        if ($notifier) {
            $toast = [Windows.UI.Notifications.ToastNotification]::new($xml)
            $notifier.Show($toast)
            exit 0
        }
    } catch {
        continue
    }
}

# All AUMIDs failed - use msg as last resort
msg * /TIME:10 "Claude Code session complete"
exit 0
'''.replace("TOAST_XML_PLACEHOLDER", toast_xml)

    try:
        subprocess.run(
            ["powershell.exe", "-NoProfile", "-Command", ps_script],
            capture_output=True,
            text=True,
            timeout=15
        )
        return True
    except subprocess.TimeoutExpired:
        return True
    except Exception as e:
        print(f"[StopHook] Exception: {e}", file=sys.stderr)
        return False


def notify_macos(notification: NotificationMessage) -> bool:
    """Send a macOS notification via osascript."""
    display_text = notification.last_user_input
    if display_text and len(display_text) > 50:
        display_text = display_text[:50] + "..."

    notification_text = f"{notification.project}"
    if display_text:
        notification_text += f": {display_text}"
    elif notification.elapsed:
        notification_text += f" - {notification.elapsed}"

    # Escape for the AppleScript string literal so a stray double quote in
    # user-controlled content cannot break out and inject AppleScript.
    safe_text = _applescript_escape(notification_text)
    script = f'display notification "{safe_text}" with title "Claude Code" sound name "Glass"'
    try:
        subprocess.run(["osascript", "-e", script], capture_output=True, text=True, timeout=5)
        return True
    except Exception:
        print(f"[Claude Code] {notification.project} session complete", file=sys.stderr)
        return True


def notify_linux(notification: NotificationMessage) -> bool:
    """Send a Linux notification via notify-send."""
    display_text = notification.last_user_input
    if display_text and len(display_text) > 50:
        display_text = display_text[:50] + "..."

    body_text = f"{notification.project}"
    if display_text:
        body_text += f": {display_text}"
    elif notification.elapsed:
        body_text += f" ({notification.elapsed})"

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
    """Dispatch the notification for the current platform."""
    platform = sys.platform
    if platform == "win32":
        return notify_windows(notification)
    elif platform == "darwin":
        return notify_macos(notification)
    elif platform.startswith("linux"):
        return notify_linux(notification)
    return False


def read_stdin_json() -> dict:
    """Read the hook's JSON payload from stdin."""
    try:
        data = sys.stdin.read()
        if not data:
            return {}
        return json.loads(data)
    except json.JSONDecodeError:
        return {}


def main():
    """Entry point - always return 0 so the hook never blocks the session."""
    try:
        data = read_stdin_json()
        notification = build_notification(data)
        send_notification(notification)
    except Exception as e:
        print(f"[StopHook] Error: {e}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
