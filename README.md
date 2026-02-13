# Claude Code 教程

> 全面掌握 Claude Code - Anthropic 出品的 AI 编程助手

## 简介

本项目包含 **10 个模块（39+ 章节）**的教程内容、视频脚本、示例代码和研究资料，旨在帮助开发者有效使用 Claude Code。课程内容从入门到进阶，基于官方 Anthropic 文档和行业专家的建议编写。

### 配套实战案例

教程中的实践案例参考 [`mybatis-boost`](C:\PythonProject\mybatis-boost) 项目——一个真实的 VSCode 扩展，展示了 Claude Code 工作流的实际应用。

---

## 项目结构

```
cc-tutorial/
├── .claude/                      # Claude Code 配置
│   ├── commands/                 # 自定义斜杠命令
│   └── settings.json             # 项目设置
│
├── docs/
│   ├── tutorial/                 # 教程章节（11 个模块）
│   ├── video-scripts/            # 视频脚本大纲
│   ├── examples/                 # 示例代码和参考资料
│   └── research/                 # 研究资料
│
├── CLAUDE.md                     # 给 Claude Code 的项目说明
├── LICENSE                       # MIT 许可证
└── README.md                     # 本文件
```

---

## 教程模块

| 模块 | 标题 | 章节数 | 重点内容 |
|------|------|--------|----------|
| 01 | 基础入门 | 4 | 安装、快捷键、Plan Mode |
| 02 | 核心工作流 | 4 | 探索-规划-编码-提交、TDD、多实例 |
| 03 | 高级功能 | 5 | 插件、MCP、技能、钩子、命令 |
| 04 | 真实案例 | 5 | mybatis-boost 项目分析 |
| 05 | 架构设计 | 4 | 整洁架构、六边形架构、可测试性 |
| 06 | LLM 局限性 | 3 | LLM 工作原理、失败模式、辅助与自动化 |
| 07 | 专家智慧 | 4 | Boris Power、Addy Osmani、Andrew Ng 等 |
| 08 | 构建工作流 | 4 | 自定义工作流构建 |
| 09 | 高级主题 | 3 | CI/CD、企业集成、AI 编程的未来 |
| 10 | 参考资料 | 3 | 速查表、故障排查、资源汇总 |
| 11 | Git 精通 | 1 | 并行开发工作流 |

---

## 主要特性

### 自定义斜杠命令

- **`/commit-push`** - 暂存、提交（约定式提交格式）、推送，智能排除调试文件

### 示例代码库

位于 `docs/examples/`：

- **HTTP API 示例** - 128+ 示例，涵盖 LLM 能力、函数调用、提示工程、代理模式
- **官方技能文档** - 9 个官方 Claude Code 技能参考
- **推荐插件** - 精选的实用插件和扩展列表

### 研究资料

`docs/research/` 中收录的权威资料：

- Boris Cherny（Claude Code 创造者）最佳实践
- 官方 Plan Mode 指南
- Andrew Ng 的 DeepLearning.AI 课程大纲
- Addy Osmani 的 2026 AI 编程工作流
- Ethan Mollick 和 Zvi Mowshowitz 的见解

---

## 核心理念

### AI 辅助工程 vs AI 自动化工程

本教程强调 **AI 辅助工程**：
- AI 是人类专业能力的放大器
- 人类工程师保持主导权和责任感
- Plan Mode 是基础工作流

### 重点技术主题

1. **Plan Mode** - 最重要的功能（按两次 Shift+Tab）
2. **多实例工作流** - 使用 git worktree 进行并行开发
3. **验证机制** - 测试、CI/CD、代码审查
4. **架构模式** - 整洁架构、六边形架构、DDD
5. **AAA 测试模式** - 单元测试的 Arrange-Act-Assert

---

## 视频脚本模板

每集视频遵循以下标准化格式：

1. **开场（30-60 秒）** - 是什么，为什么
2. **概念讲解（2-3 分钟）** - 配合图表/动画
3. **实机演示（5-8 分钟）** - 屏幕录制 + 编码
4. **总结（1-2 分钟）** - 关键要点
5. **练习（可选）** - 实践活动

完整模板见 `docs/video-scripts/episode-outline-template.md`

---

## 快速开始

1. **安装 Claude Code** - 参考 [模块 01，第 02 章](docs/tutorial/module-01-fundamentals/chapter-02-setup.md)

   > **国内用户**: 原生安装可能遇到网络问题，推荐使用 npm 全局安装：
   > ```bash
   > npm install -g @anthropic-ai/claude-code
   > ```

2. **学习基础知识** - 从 [模块 01：基础入门](docs/tutorial/module-01-fundamentals/) 开始
3. **练习示例代码** - 探索 [`docs/examples/`](docs/examples/) 中的代码
4. **观看视频脚本** - 查看 [`docs/video-scripts/`](docs/video-scripts/) 了解制作大纲

---

## 配置说明

### 给 Claude Code 用户

[`CLAUDE.md`](CLAUDE.md) 文件为 Claude Code 会话提供项目上下文和编写规则。

### MCP 服务器

`.mcp.json` 文件可配置模型上下文协议（MCP）服务器以扩展功能。

### 环境变量配置

如需使用自定义 API 端点或模型，可设置以下环境变量：

#### 示例 1：本地/自建代理

适用于本地部署的 OpenAI-compatible API（如 Nginx 代理、LiteLLM 等）。

**PowerShell:**

**PowerShell:**
```powershell
# API 配置（请替换为你的实际值）
$env:ANTHROPIC_BASE_URL="http://192.168.10.24:3456"
$env:ANTHROPIC_AUTH_TOKEN="sk-your-api-key-here"

# 禁用非必要流量（推荐）
$env:CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC="1"

# 模型映射（可选）
$env:ANTHROPIC_MODEL="gemini-3-pro-preview"
$env:ANTHROPIC_DEFAULT_SONNET_MODEL="gemini-3-pro-preview"
$env:ANTHROPIC_DEFAULT_OPUS_MODEL="gemini-3-pro-preview"
$env:ANTHROPIC_DEFAULT_HAIKU_MODEL="gemini-3-flash-preview"
$env:ANTHROPIC_SMALL_FAST_MODEL="gemini-3-flash-preview"
```

**Bash/Zsh (类 Unix 系统):**
```bash
# API 配置（请替换为你的实际值）
export ANTHROPIC_BASE_URL="http://192.168.10.24:3456"
export ANTHROPIC_AUTH_TOKEN="sk-your-api-key-here"

# 禁用非必要流量（推荐）
export CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC="1"

# 模型映射（可选）
export ANTHROPIC_MODEL="gemini-3-pro-preview"
export ANTHROPIC_DEFAULT_SONNET_MODEL="gemini-3-pro-preview"
export ANTHROPIC_DEFAULT_OPUS_MODEL="gemini-3-pro-preview"
export ANTHROPIC_DEFAULT_HAIKU_MODEL="gemini-3-flash-preview"
export ANTHROPIC_SMALL_FAST_MODEL="gemini-3-flash-preview"
```

#### 示例 2：智谱 AI

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

#### 示例 3：DeepSeek

DeepSeek 提供的 Anthropic API 兼容接口。

**PowerShell:**
```powershell
# API 配置（请替换为你的实际值）
$env:ANTHROPIC_BASE_URL="https://api.deepseek.com/anthropic"
$env:ANTHROPIC_AUTH_TOKEN="sk-your-deepseek-api-key-here"

# 禁用非必要流量（推荐）
$env:CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC="1"

# 模型映射
$env:ANTHROPIC_MODEL="deepseek-reasoner"
$env:ANTHROPIC_SMALL_FAST_MODEL="deepseek-reasoner"
$env:ANTHROPIC_DEFAULT_SONNET_MODEL="deepseek-reasoner"
$env:ANTHROPIC_DEFAULT_OPUS_MODEL="deepseek-reasoner"
$env:ANTHROPIC_DEFAULT_HAIKU_MODEL="deepseek-reasoner"
```

**Bash/Zsh (类 Unix 系统):**
```bash
# API 配置（请替换为你的实际值）
export ANTHROPIC_BASE_URL="https://api.deepseek.com/anthropic"
export ANTHROPIC_AUTH_TOKEN="sk-your-deepseek-api-key-here"

# 禁用非必要流量（推荐）
export CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC="1"

# 模型映射
export ANTHROPIC_MODEL="deepseek-reasoner"
export ANTHROPIC_SMALL_FAST_MODEL="deepseek-reasoner"
export ANTHROPIC_DEFAULT_SONNET_MODEL="deepseek-reasoner"
export ANTHROPIC_DEFAULT_OPUS_MODEL="deepseek-reasoner"
export ANTHROPIC_DEFAULT_HAIKU_MODEL="deepseek-reasoner"
```

> **注意:** 环境变量可通过以下方式永久生效：
> - **全局配置**: `~/.claude/settings.json`（所有项目生效）
> - **项目配置**: 项目目录下的 `.claude/settings.json`（仅当前项目生效）
> - **Shell 配置文件**:
>   - PowerShell: `$PROFILE`
>   - Bash: `~/.bashrc`
>   - Zsh: `~/.zshrc`

---

## 许可证

MIT License - 详见 [LICENSE](LICENSE)

---

## 相关资源

- [教程总览](docs/tutorial/00-tutorial-overview.md)
- [研究摘要](docs/research/00-research-summary.md)
- [命令速查表](docs/tutorial/module-10-reference/chapter-37-command-cheatsheet.md)
- [故障排查](docs/tutorial/module-10-reference/chapter-38-troubleshooting.md)
