# Claude Code Tutorial

> A comprehensive tutorial project for mastering Claude Code - Anthropic's AI-powered coding assistant

## Overview

This project contains **10 modules (39+ chapters)** of tutorial content, video scripts, example code, and research materials designed to teach developers how to effectively use Claude Code. The curriculum is suitable for beginners to advanced users and is based on official Anthropic documentation and expert advice from industry leaders.

### Companion Case Study

The practical examples in this tutorial reference [`mybatis-boost`](C:\PythonProject\mybatis-boost) - a real VSCode extension project that demonstrates Claude Code workflows in action.

---

## Project Structure

```
cc-tutorial/
├── .claude/                      # Claude Code configuration
│   ├── commands/                 # Custom slash commands
│   └── settings.json             # Project settings
│
├── video-scripts/                # Video script outlines
├── examples/                     # Example code and references
├── research/                     # Research materials
│
├── CLAUDE.md                     # Project instructions for Claude
├── LICENSE                       # MIT License
└── README.md                     # This file
```

---

## Tutorial Modules

| Module | Title | Chapters | Focus |
|--------|-------|----------|-------|
| 01 | Fundamentals | 4 | Installation, shortcuts, Plan Mode |
| 02 | Core Workflows | 4 | Explore-plan-code-commit, TDD, multi-instance |
| 03 | Advanced Features | 5 | Plugins, MCP, Skills, Hooks, Commands |
| 04 | Real-World Case Study | 5 | mybatis-boost project analysis |
| 05 | Architecture | 4 | Clean architecture, hexagonal, testability |
| 06 | LLM Limitations | 3 | How LLMs work, failures, assisted vs automated |
| 07 | Expert Wisdom | 4 | Boris Power, Addy Osmani, Andrew Ng, others |
| 08 | Building Workflows | 4 | Custom workflow construction |
| 09 | Advanced Topics | 3 | CI/CD, enterprise, future of AI coding |
| 10 | Reference | 3 | Cheatsheet, troubleshooting, resources |
| 11 | Git Mastery | 1 | Parallel development workflow |

---

## Key Features

### Custom Slash Commands

- **`/commit-push`** - Stage, commit (conventional commits format), and push with smart file exclusion
- **`/setup`** - Install claude-token-monitor statusline plugin

### Example Code Collection

Located in `examples/`:

- **HTTP API Examples** - 128+ examples covering LLM capabilities, function calling, prompt engineering, agent patterns
- **Official Skills Documentation** - Reference for 9 official Claude Code Skills
- **Recommended Plugins** - Curated list of useful plugins and extensions

### Research Materials

Curated research from authoritative sources in `research/`:

- Boris Cherny (Claude Code creator) best practices
- Official Plan Mode guide
- Andrew Ng's DeepLearning.AI course outline
- Addy Osmani's 2026 AI coding workflow
- Insights from Ethan Mollick and Zvi Mowshowitz

---

## Core Concepts

### AI-Assisted vs AI-Automated Engineering

This tutorial emphasizes **AI-Assisted Engineering**:
- AI as a force multiplier for human expertise
- Human engineers remain responsible and in control
- Plan Mode as the fundamental workflow

### Key Technical Topics

1. **Plan Mode** - The most important feature (Shift+Tab twice)
2. **Multi-instance workflows** - Using git worktrees for parallel development
3. **Verification mechanisms** - Testing, CI/CD, code review
4. **Architecture patterns** - Clean architecture, hexagonal, DDD
5. **AAA testing pattern** - Arrange-Act-Assert for unit tests

---

---

## Getting Started

1. **Install Claude Code** - See [Layer 02: Setup](video-scripts/layer-02-setup.md)
2. **Learn the basics** - Start with [Layer 03: Basics](video-scripts/layer-03-basics.md)
3. **Practice with examples** - Explore code in [`examples/`](examples/)
4. **Follow video scripts** - Check [`video-scripts/`](video-scripts/) for production outlines

---

## Configuration

### For Claude Code Users

The [`CLAUDE.md`](CLAUDE.md) file provides project context and authoring rules for Claude Code sessions.

### MCP Servers

The `.mcp.json` file can be configured to add Model Context Protocol servers for extended functionality.

### Environment Variables

To use a custom API endpoint or model, set the following environment variables:

#### Example 1: Local/Self-hosted Proxy

For local OpenAI-compatible API deployments (e.g., Nginx proxy, LiteLLM, etc.).

**PowerShell:**

**PowerShell:**
```powershell
# API Configuration (replace with your actual values)
$env:ANTHROPIC_BASE_URL="http://192.168.10.24:3456"
$env:ANTHROPIC_AUTH_TOKEN="sk-your-api-key-here"

# Disable non-essential traffic (recommended)
$env:CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC="1"

# Model mapping (optional)
$env:ANTHROPIC_MODEL="gemini-3-pro-preview"
$env:ANTHROPIC_DEFAULT_SONNET_MODEL="gemini-3-pro-preview"
$env:ANTHROPIC_DEFAULT_OPUS_MODEL="gemini-3-pro-preview"
$env:ANTHROPIC_DEFAULT_HAIKU_MODEL="gemini-3-flash-preview"
$env:ANTHROPIC_SMALL_FAST_MODEL="gemini-3-flash-preview"
```

**Bash/Zsh (Unix-like systems):**
```bash
# API Configuration (replace with your actual values)
export ANTHROPIC_BASE_URL="http://192.168.10.24:3456"
export ANTHROPIC_AUTH_TOKEN="sk-your-api-key-here"

# Disable non-essential traffic (recommended)
export CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC="1"

# Model mapping (optional)
export ANTHROPIC_MODEL="gemini-3-pro-preview"
export ANTHROPIC_DEFAULT_SONNET_MODEL="gemini-3-pro-preview"
export ANTHROPIC_DEFAULT_OPUS_MODEL="gemini-3-pro-preview"
export ANTHROPIC_DEFAULT_HAIKU_MODEL="gemini-3-flash-preview"
export ANTHROPIC_SMALL_FAST_MODEL="gemini-3-flash-preview"
```

#### Example 2: Zhipu AI

**PowerShell:**
```powershell
# API Configuration (replace with your actual values)
$env:ANTHROPIC_BASE_URL="https://open.bigmodel.cn/api/anthropic"
$env:ANTHROPIC_AUTH_TOKEN="your-zhipu-api-key-here"

# API timeout (milliseconds)
$env:API_TIMEOUT_MS="3000000"

# Disable non-essential traffic (recommended)
$env:CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC="1"

# Model mapping
$env:ANTHROPIC_MODEL="GLM-4.7"
$env:ANTHROPIC_SMALL_FAST_MODEL="GLM-4.7"
$env:ANTHROPIC_DEFAULT_SONNET_MODEL="GLM-4.7"
$env:ANTHROPIC_DEFAULT_OPUS_MODEL="GLM-4.7"
$env:ANTHROPIC_DEFAULT_HAIKU_MODEL="GLM-4.7"
```

**Bash/Zsh (Unix-like systems):**
```bash
# API Configuration (replace with your actual values)
export ANTHROPIC_BASE_URL="https://open.bigmodel.cn/api/anthropic"
export ANTHROPIC_AUTH_TOKEN="your-zhipu-api-key-here"

# API timeout (milliseconds)
export API_TIMEOUT_MS="3000000"

# Disable non-essential traffic (recommended)
export CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC="1"

# Model mapping
export ANTHROPIC_MODEL="GLM-4.7"
export ANTHROPIC_SMALL_FAST_MODEL="GLM-4.7"
export ANTHROPIC_DEFAULT_SONNET_MODEL="GLM-4.7"
export ANTHROPIC_DEFAULT_OPUS_MODEL="GLM-4.7"
export ANTHROPIC_DEFAULT_HAIKU_MODEL="GLM-4.7"
```

#### Example 3: DeepSeek

DeepSeek's Anthropic-compatible API endpoint.

**PowerShell:**
```powershell
# API Configuration (replace with your actual values)
$env:ANTHROPIC_BASE_URL="https://api.deepseek.com/anthropic"
$env:ANTHROPIC_AUTH_TOKEN="sk-your-deepseek-api-key-here"

# Disable non-essential traffic (recommended)
$env:CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC="1"

# Model mapping
$env:ANTHROPIC_MODEL="deepseek-chat"
$env:ANTHROPIC_SMALL_FAST_MODEL="deepseek-chat"
$env:ANTHROPIC_DEFAULT_SONNET_MODEL="deepseek-chat"
$env:ANTHROPIC_DEFAULT_OPUS_MODEL="deepseek-chat"
$env:ANTHROPIC_DEFAULT_HAIKU_MODEL="deepseek-chat"
```

**Bash/Zsh (Unix-like systems):**
```bash
# API Configuration (replace with your actual values)
export ANTHROPIC_BASE_URL="https://api.deepseek.com/anthropic"
export ANTHROPIC_AUTH_TOKEN="sk-your-deepseek-api-key-here"

# Disable non-essential traffic (recommended)
export CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC="1"

# Model mapping
export ANTHROPIC_MODEL="deepseek-chat"
export ANTHROPIC_SMALL_FAST_MODEL="deepseek-chat"
export ANTHROPIC_DEFAULT_SONNET_MODEL="deepseek-chat"
export ANTHROPIC_DEFAULT_OPUS_MODEL="deepseek-chat"
export ANTHROPIC_DEFAULT_HAIKU_MODEL="deepseek-chat"
```

> **Note:** Add the above to your Shell configuration file for persistence:
> - PowerShell: `$PROFILE`
> - Bash: `~/.bashrc`
> - Zsh: `~/.zshrc`

---

## License

MIT License - See [LICENSE](LICENSE) for details.

---

## Resources

- [Video Scripts Overview](video-scripts/)
- [Research Summary](research/00-research-summary.md)
- [Example Code](examples/)
