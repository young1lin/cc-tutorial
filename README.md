# Claude Code 教程

> 全面掌握 Claude Code - Anthropic 出品的 AI 编程助手

## 简介

本项目包含 **9 层深度教程**的视频脚本、示例代码和研究资料，旨在帮助开发者有效使用 Claude Code。课程内容由浅入深：理论基础 → 安装与环境 → 基础操作 → 核心工作流 → 项目配置体系 → 高级功能 → 注意事项 → 实战案例 → 补充内容。基于官方 Anthropic 文档和行业专家（Boris Cherny、Addy Osmani、Andrew Ng 等）的建议编写。

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
├── video-scripts/                # 视频脚本（9 层结构）
├── examples/                     # 示例代码和参考资料
├── research/                     # 研究资料
├── docs/                         # 文章、图片等
│
├── CLAUDE.md                     # 给 Claude Code 的项目说明
├── LICENSE                       # MIT 许可证
└── README.md                     # 本文件
```

---

## 视频脚本（九层结构）

| 层级 | 标题 | 内容概要 |
|------|------|----------|
| 第一层 | [理论基础](video-scripts/layer-01-theory.md) | LLM 基础、Token 与上下文窗口、多模态、模型选择 |
| 第二层 | [安装与环境](video-scripts/layer-02-setup.md) | 安装 Claude Code、IDE 联动、/init、中转、模型切换与费用 |
| 第三层 | [基础操作](video-scripts/layer-03-basics.md) | 快捷键、深度思考关键词、Resume/Rewind、Compact、图片支持 |
| 第四层 | [核心工作流](video-scripts/layer-04-workflow.md) | Vibe vs Spec Coding、Plan Mode、CLAUDE.md、Git 工作流、TDD |
| 第五层 | [项目配置体系](video-scripts/layer-05-config.md) | 配置目录结构、Rules、Memory、Commands、Context Engineering |
| 第六层 | [高级功能](video-scripts/layer-06-advanced.md) | MCP、SubAgent、插件、Skills、Hooks、Headless、Worktrees、SDK |
| 第七层 | [注意事项](video-scripts/layer-07-caveats.md) | AI 能力边界、翻车场景、Burnout、数据安全、扩展学习资源 |
| 第八层 | [实战案例](video-scripts/layer-08-practice.md) | 完整的项目修改流程演示 |
| 第九层 | [补充内容](video-scripts/layer-09-supplement.md) | Web 端、Session Teleport、国内订阅指南、安全提示 |

---

## 主要特性

### 自定义斜杠命令

- **`/commit-push`** - 暂存、提交（约定式提交格式）、推送，智能排除调试文件

### 示例代码库

位于 `examples/`：

- **HTTP API 示例** - 97 个示例，涵盖 LLM 能力、函数调用、提示工程、代理模式
- **官方技能文档** - 9 个官方 Claude Code 技能参考
- **推荐插件** - 精选的实用插件和扩展列表

### 研究资料

`research/` 中收录的权威资料：

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


---

## 快速开始

1. **安装 Claude Code** - 参考 [第二层：安装与环境](video-scripts/layer-02-setup.md)

   > **国内用户**: 原生安装可能遇到网络问题，推荐使用 npm 全局安装：
   > ```bash
   > npm install -g @anthropic-ai/claude-code
   > ```

2. **学习基础知识** - 从 [第一层：理论基础](video-scripts/layer-01-theory.md) 开始
3. **掌握核心工作流** - 重点学习 [第四层：核心工作流](video-scripts/layer-04-workflow.md)
4. **练习示例代码** - 探索 [`examples/`](examples/) 中的代码
5. **观看实战案例** - 查看 [第八层：实战案例](video-scripts/layer-08-practice.md)

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
```powershell
# API 配置（请替换为你的实际值）
$env:ANTHROPIC_BASE_URL="http://192.168.1.2:3456"
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
export ANTHROPIC_BASE_URL="http://192.168.1.2:3456"
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

- [文档导航](docs/README.md)
- [公众号文章：2026 年古法编程注定被淘汰](docs/article-2026-coding-evolution.md)
- [研究摘要](research/00-research-summary.md)
- [视频脚本总览](video-scripts/README.md)
- [官方 Skills 文档](examples/official-skills/README.md)
- [推荐插件列表](examples/recommended-plugins/README.md)
