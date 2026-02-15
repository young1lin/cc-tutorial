# Skill: keybindings-help

## 概述

`keybindings-help` 是用于定制 Claude Code 键盘快捷键的 Skill。当你需要修改键盘绑定、添加和弦快捷键（chord bindings）或修改 `~/.claude/keybindings.json` 时使用。

**核心能力**:
- 查看当前键盘快捷键配置
- 修改现有快捷键绑定
- 添加新的快捷键
- 配置和弦快捷键（两键组合）
- 恢复默认配置

---

## 触发方式

### 斜杠命令

```bash
/keybindings-help
```

### 自然语言触发

```
"修改 Claude Code 的快捷键"
"将提交键改为 Ctrl+Enter"
"添加一个快捷键"
"如何定制键盘绑定"
"我想改变快捷键设置"
```

---

## keybindings.json 文件位置

```
~/.claude/keybindings.json        # 用户级别（全局）
C:\Users\用户名\.claude\keybindings.json  # Windows
/Users/用户名/.claude/keybindings.json    # macOS
/home/用户名/.claude/keybindings.json     # Linux
```

---

## 默认快捷键

Claude Code 的默认快捷键配置：

| 操作 | 默认快捷键 | 说明 |
|------|-----------|------|
| 提交输入 | Enter | 发送消息 |
| 换行 | Shift+Enter | 在输入框中换行 |
| 切换 Plan Mode | Shift+Tab (两次) | 进入/退出规划模式 |
| 中断操作 | Escape | 停止当前 AI 响应 |
| 粘贴图片 | Alt+V | 粘贴剪贴板图片 |
| 清空上下文 | /clear | 清除对话历史 |

---

## 实际演示

### 示例 1: 将提交键改为 Ctrl+Enter

**用户请求**:
```
我习惯用 Ctrl+Enter 提交，而不是 Enter，
请帮我修改快捷键配置
```

**Claude 的操作**:

首先读取当前配置：

```json
// ~/.claude/keybindings.json（默认为空或不存在）
{}
```

生成新配置：

```json
// ~/.claude/keybindings.json
{
  "submit": "ctrl+enter",
  "newline": "enter"
}
```

**解释**:
- `submit`: 将提交操作绑定到 Ctrl+Enter
- `newline`: 将普通 Enter 改为换行（而非提交）

---

### 示例 2: 添加和弦快捷键

**和弦快捷键（Chord Bindings）**: 先按一个键，再按另一个键，两步组合触发操作。

**用户请求**:
```
我想添加一个和弦快捷键：
先按 Ctrl+K，再按 Ctrl+C 来清除上下文
```

**Claude 的配置**:

```json
// ~/.claude/keybindings.json
{
  "chords": {
    "ctrl+k ctrl+c": "/clear",
    "ctrl+k ctrl+r": "/reset"
  }
}
```

---

### 示例 3: 完整自定义配置

**用户请求**:
```
帮我设置一套适合 VS Code 用户的快捷键配置
```

**Claude 生成的配置**:

```json
// ~/.claude/keybindings.json
{
  "_comment": "VS Code 风格快捷键配置",

  // 提交和换行
  "submit": "ctrl+enter",
  "newline": "enter",

  // 和弦快捷键（Ctrl+K 前缀）
  "chords": {
    "ctrl+k ctrl+c": "/clear",
    "ctrl+k ctrl+p": "/plan",
    "ctrl+k ctrl+h": "/help",
    "ctrl+k ctrl+r": "/reset"
  }
}
```

**说明**:
- 使用 `Ctrl+Enter` 提交（与 VS Code Terminal 一致）
- 使用 `Ctrl+K` 前缀的和弦快捷键访问常用命令
- 纯 `Enter` 用于换行

---

## keybindings.json 格式说明

### 基本结构

```json
{
  "submit": "键名",          // 提交/发送消息的快捷键
  "newline": "键名",         // 在输入框中插入换行
  "chords": {
    "触发组合1": "命令或操作",
    "触发组合2": "命令或操作"
  }
}
```

### 支持的按键名称

**修饰键**:

| 名称 | 说明 |
|------|------|
| `ctrl` | Ctrl 键 |
| `alt` | Alt 键（macOS 上是 Option） |
| `shift` | Shift 键 |
| `meta` | Windows 键（macOS 上是 Cmd） |

**组合写法**: `ctrl+shift+enter`（用 `+` 连接）

**常用按键**:

| 名称 | 说明 |
|------|------|
| `enter` | Enter/回车键 |
| `escape` | Esc 键 |
| `tab` | Tab 键 |
| `backspace` | 退格键 |
| `delete` | Delete 键 |
| `up`/`down`/`left`/`right` | 方向键 |
| `pageup`/`pagedown` | 翻页键 |
| `home`/`end` | Home/End 键 |
| `a`-`z` | 字母键 |
| `0`-`9` | 数字键 |
| `f1`-`f12` | 功能键 |

### 可绑定的命令

```json
{
  "chords": {
    "ctrl+k ctrl+c": "/clear",      // 清除上下文
    "ctrl+k ctrl+h": "/help",       // 显示帮助
    "ctrl+k ctrl+p": "/plan",       // 切换 Plan Mode（等同于 Shift+Tab 两次）
    "ctrl+k ctrl+r": "/reset",      // 重置会话
    "ctrl+k ctrl+i": "/info"        // 显示当前会话信息
  }
}
```

---

## 常见配置场景

### 场景 1: 习惯终端开发者

```json
{
  "submit": "ctrl+j",      // Ctrl+J 在很多终端中是 Enter
  "newline": "enter"
}
```

### 场景 2: Vim 用户

```json
{
  "submit": "ctrl+enter",
  "newline": "enter",
  "chords": {
    "ctrl+[ ctrl+[": "/clear",      // 双 Esc（终端友好）
    "space space": "/help"
  }
}
```

### 场景 3: macOS 用户

```json
{
  "submit": "meta+enter",    // Cmd+Enter
  "newline": "enter",
  "chords": {
    "meta+k meta+c": "/clear",
    "meta+k meta+r": "/reset"
  }
}
```

### 场景 4: 笔记本用户（避免误触）

```json
{
  // 需要明确的组合键才能提交，避免误按 Enter
  "submit": "ctrl+shift+enter",
  "newline": "enter"
}
```

---

## 如何应用配置

### 方法 1: 手动编辑

```bash
# 创建/编辑配置文件
# macOS/Linux
nano ~/.claude/keybindings.json

# Windows（PowerShell）
notepad $env:USERPROFILE\.claude\keybindings.json
```

### 方法 2: 让 Claude 帮你编辑

```bash
> 修改我的 Claude Code 快捷键，把提交键改为 Ctrl+Enter
```

Claude 会：
1. 读取当前的 `keybindings.json`
2. 应用你的修改
3. 写入更新后的配置

### 方法 3: 查看当前配置

```bash
> 显示我当前的 Claude Code 快捷键配置
```

---

## 验证配置是否生效

修改配置后，重启 Claude Code：

```bash
# 关闭当前 Claude Code 实例
# 重新打开
claude
```

然后测试新的快捷键是否有效。

---

## 重置为默认配置

```bash
# 删除配置文件恢复默认
rm ~/.claude/keybindings.json

# 或者让 Claude 帮你重置
> 重置 Claude Code 快捷键为默认配置
```

---

## 常见问题

### Q1: 修改配置后快捷键不生效怎么办？

**A**: 检查以下步骤：

1. 确认文件路径正确（`~/.claude/keybindings.json`）
2. 确认 JSON 格式正确（无语法错误）
3. 重启 Claude Code

```bash
# 验证 JSON 格式
cat ~/.claude/keybindings.json | python -m json.tool
```

### Q2: 和弦快捷键的等待时间是多少？

**A**: 默认约 500ms。按下第一个键后，需要在此时间内按下第二个键。

### Q3: 能绑定到功能键（F1-F12）吗？

**A**: 可以：

```json
{
  "chords": {
    "f1": "/help",
    "f2": "/clear"
  }
}
```

注意：某些终端可能会拦截功能键。

### Q4: Windows 上 Ctrl 和 meta 有什么区别？

**A**: 在 Windows 上：
- `ctrl`: Ctrl 键
- `meta`: Windows 键（⊞）
- `alt`: Alt 键

建议 Windows 用户主要使用 `ctrl` 和 `alt`，避免使用 `meta`（Windows 键有系统级拦截）。

### Q5: 如何配置只在特定项目生效的快捷键？

**A**: 目前 keybindings.json 是全局配置，不支持项目级别。可以通过 `CLAUDE.md` 中的提示词来模拟特定项目的工作流。

---

## 相关资源

- [Layer 01 - 理论基础](../../../video-scripts/layer-01-theory.md)
- [CLAUDE.md 配置指南](../../../CLAUDE.md)

---

**Skill 版本**: 内置
**最后更新**: 2026-02-10
