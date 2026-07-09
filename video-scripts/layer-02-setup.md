# 第二层：安装与环境

# 安装 Claude Code

`npm install -g @anthropic-ai/claude-code`

在安装 Claude Code 之前，必须安装最新的 Node.js，官网推荐的原生安装方式，国内安装有问题。安装好后，执行 `claude install` 命令来安装原生的。如果你没有代理，不知道怎么设置代理环境变量，那就不用原生的安装方式，npm 安装的方式也能用，只是会有警告提示而已。

**Win10 用户特别注意**：Win10 自带的终端有兼容问题，Win10 用户不要安装最新版本的 Windows Terminal 和 PowerShell 7，有 BUG 会闪退、无法安装。推荐使用以下指定版本：

- **Windows Terminal 1.23.12371.0**：[下载 msixbundle](https://github.com/microsoft/terminal/releases/download/v1.23.12371.0/Microsoft.WindowsTerminal_1.23.12371.0_8wekyb3d8bbwe.msixbundle)
- **PowerShell 7.4.13**：[下载 msi](https://github.com/PowerShell/PowerShell/releases/download/v7.4.13/PowerShell-7.4.13-win-x64.msi)

Win11 自带终端没有这种问题，Win11 只需要安装 PowerShell 7 最新版本就行。

## Windows 踩坑一：PowerShell 脚本执行策略

Windows 默认禁止运行未签名脚本（执行策略 Restricted）。`claude install` 依赖 npm 脚本，需先以普通用户权限在 PowerShell 7 中运行：

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

只影响当前用户，无需管理员权限，不降低系统安全性。

## Windows 踩坑二：PowerShell UTF-8 乱码

Claude Code 的 TUI 使用 Unicode 绘制边框，默认代码页 GBK 会导致乱码。两步解决：

**临时（当前会话）：**

```powershell
chcp 65001
$OutputEncoding = [System.Text.Encoding]::UTF8
```

**永久（写入 PowerShell Profile）：**

```powershell
# 查看 Profile 路径
echo $PROFILE

# 追加到 Profile（没有 Profile 先创建）
Add-Content $PROFILE "`nchcp 65001"
Add-Content $PROFILE "`n`$OutputEncoding = [System.Text.Encoding]::UTF8"
```

**注意**：不含 API Key，用户自行配置 `ANTHROPIC_API_KEY` 环境变量（System → 高级系统设置 → 环境变量）。

## Windows 踩坑三：安装目录未加入 PATH

`claude install` 原生安装时，如果安装目录没有自动加入系统 PATH 环境变量，后续执行 `claude` 命令会报"找不到命令"。

**典型情况：**
- 安装过程中勾选了"不修改 PATH"
- 安装程序权限不足，无法修改系统环境变量
- 使用便携版/绿色版安装

**解决方法：**

手动将 Claude Code 安装目录加入 PATH：

1. 找到安装目录（默认是 `%USERPROFILE%\.claude\bin` 或 `%LOCALAPPDATA%\claude`）
2. 打开"系统属性" → "高级" → "环境变量"
3. 在"用户变量"中找到 `Path`，点击"编辑"
4. 点击"新建"，添加 Claude Code 的安装目录
5. **重启终端**（关闭 PowerShell 再重新打开，环境变量才会生效）

**验证：**

```powershell
# 检查 claude 是否在 PATH 中
Get-Command claude

# 或者直接查看 PATH
$env:PATH -split ';' | Where-Object { $_ -like '*claude*' }
```

如果输出显示了 claude 的路径，说明配置成功。

# IDE 安装 Claude Code

选择你合适的 IDE，IDEA、VSCode、Cursor 等等里面都有对应的 Claude Code 插件，可以直接在这里运行，更改对应的环境变量，也可以和终端联动。安装好后，在 IDE 中选中某行，看右下角会出现 xx lines selected，如果没有，输入 `/config` 把 IDE-auto-connect 打开。如果还没有，检查下版本是否一致，并且你这个当前的窗口是当前项目路径第一个打开的，同一个项目路径有多个窗口，只有一个第一个 Claude Code 能和 IDE 联动。

如果还不行，输入 `/ide` 确保连接上了，重启 IDE。

连接成功后，在 IDE 中选中代码，Claude Code 即可获取上下文进行对话。

# 启动前设置

如果你不是 Claude 订阅用户（订阅用户也要设置代理输入 /login 才能登录使用），那你只能用国内的模型，或者 OpenRouter 这种。下面就是智谱的环境变量设置，如果嫌环境变量每次都要设置很麻烦，可以直接在 `~/.claude/settings.json` 文件中设置。注意，这里的 API_KEY 需要替换成你自己的 API_KEY。

```json
{
  "env": {
    "ANTHROPIC_BASE_URL": "https://open.bigmodel.cn/api/anthropic",
    "ANTHROPIC_AUTH_TOKEN": "your-zhipu-api-key-here"
  }
}
```

**PowerShell:**
```powershell
# API 配置（请替换为你的实际值）
$env:ANTHROPIC_BASE_URL="https://open.bigmodel.cn/api/anthropic"
$env:ANTHROPIC_AUTH_TOKEN="your-zhipu-api-key-here"

# API 超时设置（毫秒）
$env:API_TIMEOUT_MS="3000000"

# 禁用非必要流量（推荐）
$env:CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC="1"

# 模型映射
$env:ANTHROPIC_MODEL="glm-5"
$env:ANTHROPIC_SMALL_FAST_MODEL="glm-5"
$env:ANTHROPIC_DEFAULT_SONNET_MODEL="glm-5"
$env:ANTHROPIC_DEFAULT_OPUS_MODEL="glm-5"
$env:ANTHROPIC_DEFAULT_HAIKU_MODEL="glm-5"
```

**Bash/Zsh (类 Unix 系统):**
```bash
# API 配置（请替换为你的实际值）
export ANTHROPIC_BASE_URL="https://open.bigmodel.cn/api/anthropic"
export ANTHROPIC_AUTH_TOKEN="your-zhipu-api-key-here"

# API 超时设置（毫秒）
export API_TIMEOUT_MS="3000000"

# 禁用非必要流量（推荐）
export CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC="1"

# 模型映射
export ANTHROPIC_MODEL="glm-5"
export ANTHROPIC_SMALL_FAST_MODEL="glm-5"
export ANTHROPIC_DEFAULT_SONNET_MODEL="glm-5"
export ANTHROPIC_DEFAULT_OPUS_MODEL="glm-5"
export ANTHROPIC_DEFAULT_HAIKU_MODEL="glm-5"
```

# /init —— 让 Claude 认识你的项目

安装好 Claude Code 后，第一件事就是让它理解你的项目。`/init` 命令会扫描整个 codebase，自动生成一份 CLAUDE.md 文件。

**用法：**

```bash
# 进入项目根目录
cd /path/to/your/project

# 启动 Claude Code
claude

# 运行 /init
/init
```

**`/init` 会做什么：**

1. **扫描项目结构**：分析目录树、文件类型、依赖配置（package.json、go.mod、pom.xml 等）
2. **识别技术栈**：检测你用的框架、语言、构建工具
3. **生成 CLAUDE.md**：自动写一份包含项目概述、技术栈、目录结构、开发约定的初始文件
4. **建议改进**：如果你已经有 CLAUDE.md，`/init` 会审查现有内容并提出改进建议

**典型输出示例：**

```markdown
# Project: mybatis-boost

## Overview
TypeScript-based MyBatis SQL formatter and language support for VSCode.

## Tech Stack
- TypeScript
- VSCode Extension API
- Tree-sitter for SQL parsing

## Key Directories
- `src/formatter/` - SQL formatting logic
- `src/mcp/` - MCP server integration
- `src/test/` - Test suites

## Build Commands
- `npm run build` - Build extension
- `npm test` - Run tests
- `npm run package` - Package for distribution
```

**什么时候该用 `/init`：**

- 刚拿到一个不熟悉的项目，想让 Claude 快速了解全貌
- 项目还没有 CLAUDE.md，懒得手动写
- 已有 CLAUDE.md 但很久没更新，想让 Claude 根据当前代码重新生成

**注意事项：**
- `/init` 生成的是**初稿**，建议你审核并补充项目特有的坑和约定
- 大型项目（几万个文件）扫描会花点时间，耐心等待
- 如果你有明确的 CLAUDE.md 风格偏好，先手动创建一个，再用 `/init` 让 Claude 帮你完善

## IDE 和终端联动

在你习惯的 IDE 中，下载 Claude Code 插件（最新版本），然后在终端中输入 `/config` 搜索 IDE，把 Auto-Connect to IDE 打开。在 IDE 中选中你的代码，Claude Code 终端会显示已经被选中的代码行数，或者被选中的代码文件。

## 允许所有权限（生产勿用）

**警告**：生产环境禁用此选项。如果通过 Fetch 访问恶意网站遭遇提示词注入，攻击者可能诱导 Claude 执行 `rm -rf /` 等危险命令，导致系统文件被删除。

有两种方式配置允许所有权限，一种是 `claude --dangerously-skip-permissions` 启动会话，一种是 .claude 文件夹下，设置 `settings.local.json` 或者 `settings.json` 文件中，设置下面这样的内容来允许所有权限。

```json
{
  "permissions": {
    "defaultMode": "bypassPermissions"
  }
}
```

## 中转

假设你有 Gemini Pro、Stepfun 阶跃星辰的 Code Plan（他们后续会推出）、ChatGPT 的订阅，但是它们都不支持 Anthropic 协议，他们只支持兼容 OpenAI 格式的协议。这个时候分两种情况，

1. Gemini Pro、ChatGPT 订阅等，需要先通过 Claude Relay Service，将 Access Token 获取到，并且绑定到这里。具体怎么绑定，我建议直接问 AI。
2. 只提供了 OpenAI 格式协议的，例如 Stepfun，上面第一步获取到的都是自家的格式，都可以通过 Claude Code Router 来中转，把请求转换成 OpenAI 格式，再发送到对应的 API 地址。

还有一种就是 Gemini Pro 通过 Antigravity 来使用 Claude Opus 4.6 或者 Gemini 3 Pro 模型，想直接通过 Claude Code 使用，可以下载 Antigravity Tools 这个开源的工具 `https://github.com/lbjlaq/Antigravity-Manager`，如何使用，直接问 AI。

## 模型切换和费用监控

**`/model`**：在对话中随时切换模型。比如用 Opus 做规划和复杂推理，用 Sonnet 做简单的代码修改和格式调整。不同模型价格差异很大，合理切换能省不少钱。

**`/cost`**：查看当前会话的 Token 消耗和费用。配合第三方工具 `ccusage` 可以看到更详细的历史消费数据。养成习惯，复杂任务做完看一眼 /cost，对消耗有个概念。
