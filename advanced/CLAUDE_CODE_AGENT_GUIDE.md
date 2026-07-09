# Claude Code Agent 协作系统高级教程

> 本教程涵盖 Claude Code 的所有多代理协作功能，包括 Agent Teams、Subagents、Skills 等，以及详细的最佳实践和应用场景。

---

## 目录

1. [概述](#1-概述)
2. [Agent Teams（多代理团队）](#2-agent-teams多代理团队)
3. [Subagents（子代理）](#3-subagents子代理)
4. [Skills（技能系统）](#4-skills技能系统)
5. [Hooks（钩子系统）](#5-hooks钩子系统)
6. [Worktrees（工作树隔离）](#6-worktrees工作树隔离)
7. [功能对比与选择指南](#7-功能对比与选择指南)
8. [最佳实践场景](#8-最佳实践场景)
9. [常见问题与故障排除](#9-常见问题与故障排除)

---

## 1. 概述

Claude Code 提供了多种代理协作机制，每种机制适用于不同的场景：

| 功能 | 核心用途 | 并行能力 | 通信能力 | 复杂度 |
|------|----------|----------|----------|--------|
| **Agent Teams** | 多代理并行协作 | ✅ 强 | ✅ 代理间直接通信 | 高 |
| **Subagents** | 轻量级任务委托 | ✅ 中 | ❌ 只报告给主代理 | 中 |
| **Skills** | 专业能力扩展 | ❌ 无 | N/A | 低 |
| **Hooks** | 自动化流程控制 | ❌ 无 | N/A | 低 |
| **Worktrees** | 代码隔离工作 | ❌ 无 | N/A | 中 |

---

## 2. Agent Teams（多代理团队）

### 2.1 什么是 Agent Teams

Agent Teams 允许你创建多个 Claude Code 实例协同工作的团队：
- **Team Lead**: 主会话，负责协调、分配任务、综合结果
- **Teammates**: 独立的 Claude Code 实例，各自处理分配的任务
- **Task List**: 共享任务列表，支持依赖关系
- **Mailbox**: 代理间消息系统

### 2.2 启用 Agent Teams

```json
// settings.json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  }
}
```

### 2.3 显示模式

| 模式 | 说明 | 适用环境 |
|------|------|----------|
| **in-process** | 所有队友在同一终端，`↑` / `↓` 切换（v2.1.179 起为默认） | Windows、任意终端 |
| **split panes** | 每个队友独立窗格 | 需要 tmux 或 iTerm2 (macOS) |

Windows 用户默认使用 in-process 模式，无需额外配置。

### 2.4 创建团队

**基础创建：**
```
创建一个 agent team 从三个角度分析这个项目：
- 架构设计分析
- 安全漏洞检查
- 性能优化建议
```

**指定队友数量和模型：**
```
创建一个 4 人团队并行重构这些模块，每个队友使用 Sonnet 模型：
- Teammate 1: 重构 internal/ssh/ 模块
- Teammate 2: 重构 internal/storage/ 模块
- Teammate 3: 重构 internal/ui/ 模块
- Teammate 4: 更新所有相关测试
```

**要求计划审批：**
```
创建一个架构师队友重构认证模块，要求在实施前获得计划审批。
```

### 2.5 团队操作

| 快捷键/命令 | 功能 |
|-------------|------|
| `↑` / `↓` | 在 agent panel 选择队友 |
| `Enter` | 查看队友会话，可直接打字发消息 |
| `x` | 停止选中的队友 |
| `Escape` | 中断队友当前操作 |
| `Ctrl + T` | 切换任务列表视图 |

**命令示例：**
```
# 分配任务
Assign the security review task to the security teammate

# 让队友领取任务
Tell teammates to claim available tasks

# 直接与队友对话
Ask the architect teammate to explain their design decision

# 关闭单个队友
Ask the researcher teammate to shut down

# 共享目录在会话结束时自动清理（无需手动 cleanup）
```

### 2.6 最佳应用场景

✅ **强烈推荐：**
- 并行代码审查（安全、性能、测试覆盖率各自独立）
- 竞争假设调试（多个队友测试不同理论）
- 跨层功能开发（前端、后端、测试分离）
- 研究与调研（不同方向并行探索）

❌ **不推荐：**
- 顺序执行的任务
- 需要频繁编辑同一文件
- 任务之间有大量依赖

---

## 3. Subagents（子代理）

### 3.1 什么是 Subagents

Subagents 是在当前会话内生成的轻量级代理，用于：
- 快速、专注的任务
- 只需要结果，不需要协作的场景
- 研究和验证工作

### 3.2 与 Agent Teams 的区别

| 特性 | Subagents | Agent Teams |
|------|-----------|-------------|
| **上下文** | 独立窗口，结果返回调用者 | 完全独立实例 |
| **通信** | 只报告给主代理 | 队友直接通信 |
| **协调** | 主代理管理所有工作 | 共享任务列表，自协调 |
| **Token 成本** | 较低 | 较高 |
| **最佳场景** | 快速专注任务 | 复杂协作工作 |

### 3.3 使用 Subagents

Claude Code 会自动使用 subagents 处理某些任务，你也可以显式请求：

```
使用 subagent 搜索项目中所有使用 deprecated API 的地方
```

```
生成一个 subagent 验证所有单元测试是否通过
```

### 3.4 内置 Agent 类型

| Agent 类型 | 用途 |
|------------|------|
| `general-purpose` | 通用任务、复杂搜索 |
| `Explore` | 快速代码库探索 |
| `Plan` | 实现计划设计 |

### 3.5 最佳应用场景

✅ **推荐：**
- 代码库搜索（需要多轮查询）
- 快速研究任务
- 验证和测试
- 不需要代理间协作的并行任务

---

## 4. Skills（技能系统）

### 4.1 什么是 Skills

Skills 是预定义的专业能力模块，让 Claude 获得特定领域的专业知识。

### 4.2 内置 Skills

| Skill | 用途 | 触发场景 |
|-------|------|----------|
| `simplify` | 代码质量审查和优化 | 手动调用 |
| `loop` | 定时执行任务 | 手动调用 |
| `claude-api` | Claude API/SDK 开发 | 代码导入相关包 |
| `docx` | Word 文档处理 | 手动调用 |
| `frontend-design` | 高质量前端界面设计 | 构建前端组件 |
| `mcp-builder` | MCP 服务器开发 | 构建 MCP server |
| `pdf` | PDF 处理 | 手动调用 |
| `project-planner` | 项目规划文档生成 | 新项目规划 |
| `skill-creator` | 创建新技能 | 手动调用 |
| `webapp-testing` | Web 应用测试 | 手动调用 |
| `code-review` | PR 代码审查 | 手动调用 |

### 4.3 使用 Skills

```
/simplify  # 审查代码质量
```

```
/frontend-design 创建一个登录页面
```

```
/project-planner 规划一个任务管理系统
```

### 4.4 创建自定义 Skills

Skills 存放在 `.claude/skills/` 目录，格式：

```
.claude/skills/
├── my-skill/
│   ├── SKILL.md          # 主技能定义（文件名必须大写 SKILL.md）
│   └── references/       # 参考资料（可选，渐进式披露）
```

**SKILL.md 示例（官方格式，T1）：**
```markdown
---
name: my-skill
description: Use when [触发场景].   # 写给模型看的触发条件，不是摘要
---

# My Custom Skill

## Instructions
Detailed instructions for Claude when this skill is active.

## Gotchas
- 常见陷阱 1
- 常见陷阱 2
```

> **官方要点（T1，见 research/13）**：文件名必须是大写 `SKILL.md`；`description` 是"何时触发"而非摘要；信号密度最高的是 Gotchas 段；skill 是文件夹，用 `references/`、`assets/` 做渐进式披露。

---

## 5. Hooks（钩子系统）

### 5.1 什么是 Hooks

Hooks 是在特定事件发生时自动执行的命令或脚本，用于：
- 自动化工作流
- 强制执行规则
- 集成外部工具

### 5.2 可用的 Hook 类型

| Hook 类型 | 触发时机 | 常见用途 |
|-----------|----------|----------|
| `PreToolUse` | 工具执行前 | 验证输入、阻止危险操作 |
| `PostToolUse` | 工具执行后 | 记录日志、触发通知 |
| `PostToolUseFailure` | 工具执行失败后 | 错误处理、重试 |
| `UserPromptSubmit` | 用户提交提示时 | 预处理、日志记录 |
| `SessionStart` | 会话开始时 | 初始化环境 |
| `SessionEnd` | 会话结束时 | 清理、报告 |
| `Stop` | 会话停止时 | 通知、清理 |
| `TeammateIdle` | 队友空闲时 | 质量检查、继续工作 |
| `TaskCreated` | 任务被创建时 | 校验 schema、阻止创建 |
| `TaskCompleted` | 任务完成时 | 验证、测试 |

### 5.3 配置 Hooks

```json
// settings.json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write",
        "hooks": [
          {
            "type": "command",
            "command": "echo 'File written: $FILE_PATH' >> log.txt"
          }
        ]
      }
    ],
    "TeammateIdle": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python ~/.claude/hooks/check-quality.py",
            "timeout": 30
          }
        ]
      }
    ],
    "TaskCompleted": [
      {
        "hooks": [
          {
            "type": "agent",
            "prompt": "Verify that the completed task meets quality standards. Check for tests and documentation.",
            "timeout": 60
          }
        ]
      }
    ]
  }
}
```

### 5.4 Hook 类型详解

**Command Hook:**
```json
{
  "type": "command",
  "command": "your-script.sh",
  "timeout": 30,
  "statusMessage": "Running quality check..."
}
```

**Prompt Hook (LLM 评估):**
```json
{
  "type": "prompt",
  "prompt": "Evaluate if this change follows best practices. Return 'approve' or 'reject' with reasons.",
  "model": "claude-sonnet-4-6"
}
```

**Agent Hook (代理验证):**
```json
{
  "type": "agent",
  "prompt": "Verify that unit tests pass and code coverage is maintained.",
  "timeout": 120
}
```

**HTTP Hook:**
```json
{
  "type": "http",
  "url": "https://api.example.com/webhook",
  "headers": {
    "Authorization": "Bearer $API_TOKEN"
  },
  "allowedEnvVars": ["API_TOKEN"]
}
```

---

## 6. Worktrees（工作树隔离）

### 6.1 什么是 Worktrees

Git worktrees 允许你在同一仓库的独立目录中工作，适合：
- 同时处理多个分支
- 隔离实验性更改
- 避免切换分支时的上下文丢失

### 6.2 使用 Worktrees

**创建 Worktree:**
```
创建一个 worktree 来处理 feature-x 分支
```

**退出 Worktree:**
```
退出当前 worktree 并保留更改
```

或删除：
```
退出并删除 worktree
```

### 6.3 配置 Worktree

```json
// settings.json
{
  "worktree": {
    "symlinkDirectories": ["node_modules", ".cache"],
    "sparsePaths": ["src/", "tests/"]
  }
}
```

---

## 7. 功能对比与选择指南

### 7.1 决策树

```
需要多代理协作？
├── 是 → 代理间需要通信？
│   ├── 是 → Agent Teams
│   └── 否 → Subagents
└── 否 → 需要专业能力？
    ├── 是 → Skills
    └── 否 → 需要自动化？
        ├── 是 → Hooks
        └── 否 → 需要代码隔离？
            ├── 是 → Worktrees
            └── 否 → 单会话即可
```

### 7.2 场景-功能映射表

| 场景 | 推荐功能 | 原因 |
|------|----------|------|
| PR 代码审查（多维度） | Agent Teams | 并行独立审查 |
| 快速代码搜索 | Subagents | 轻量、专注 |
| 前端界面开发 | Skills (frontend-design) | 专业能力 |
| CI/CD 集成 | Hooks | 自动化触发 |
| 同时开发多特性 | Worktrees | 隔离工作 |
| 复杂 Bug 调查 | Agent Teams | 竞争假设验证 |
| 文档生成 | Skills (docx/pdf) | 专业工具 |
| 项目规划 | Skills (project-planner) | 结构化输出 |

---

## 8. 最佳实践场景

### 8.1 场景一：并行代码审查

**问题：** 单人审查容易遗漏特定类型的问题

**解决方案：** 使用 Agent Teams 创建专业审查团队

```
Create an agent team to review PR #42. Spawn three reviewers:
- Security reviewer: Focus on authentication, input validation, SQL injection, XSS
- Performance reviewer: Analyze algorithms, database queries, memory usage
- Test reviewer: Verify coverage, edge cases, test quality

Each reviewer works independently and reports findings.
The lead synthesizes all findings into a summary.
```

**为什么有效：**
- 每个审查者有明确的关注点
- 并行工作节省时间
- 结果综合后更全面

---

### 8.2 场景二：竞争假设调试

**问题：** 复杂 Bug 的根因不明，单人容易锚定在第一个理论

**解决方案：** 使用 Agent Teams 进行竞争假设调查

```
用户报告应用在发送消息后意外退出。
生成 5 个 agent teammates 调查以下假设：
1. 内存泄漏导致 OOM
2. 网络超时处理不当
3. 并发竞态条件
4. 配置解析错误
5. 第三方库 bug

让他们互相质疑对方的理论，像科学辩论一样。
更新 findings.md 记录最终共识。
```

**为什么有效：**
- 避免确认偏误
- 多角度验证
- 辩论机制确保结论可靠

---

### 8.3 场景三：跨层功能开发

**问题：** 新功能涉及前端、后端、数据库，切换上下文成本高

**解决方案：** 使用 Agent Teams 按层分配

```
创建团队开发用户通知系统：

Teammate 1 (Frontend):
- 通知 UI 组件（Toast、Badge）
- WebSocket 连接管理
- 文件: internal/ui/views/notification*.go

Teammate 2 (Backend API):
- 通知 REST API
- 数据库模型和迁移
- 文件: internal/api/notification*.go, internal/models/notification*.go

Teammate 3 (Business Logic):
- 通知服务层
- 邮件/推送发送逻辑
- 文件: internal/service/notification*.go

Teammate 4 (Tests):
- 单元测试和集成测试
- 文件: internal/**/*_test.go

确保每人只修改自己负责的文件。
```

**为什么有效：**
- 文件隔离避免冲突
- 专业分工提高效率
- 并行开发缩短周期

---

### 8.4 场景四：自动化质量保证

**问题：** 需要确保每次代码更改都符合质量标准

**解决方案：** 使用 Hooks 自动验证

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit",
        "hooks": [
          {
            "type": "command",
            "command": "golangci-lint run --fast",
            "timeout": 60
          }
        ]
      }
    ],
    "TaskCompleted": [
      {
        "hooks": [
          {
            "type": "agent",
            "prompt": "Verify: 1) Tests pass 2) No lint errors 3) Documentation updated if public API changed",
            "timeout": 120
          }
        ]
      }
    ]
  }
}
```

**为什么有效：**
- 自动执行，无需记忆
- 即时反馈
- 可自定义规则

---

### 8.5 场景五：专业领域开发

**问题：** 需要高质量的前端界面，但缺乏设计专业知识

**解决方案：** 使用 Skills

```
/frontend-design 创建一个现代化的仪表板页面：
- 侧边导航
- 数据卡片组件
- 图表展示区域
- 响应式设计
- 暗色主题支持
```

**为什么有效：**
- 内置专业知识和最佳实践
- 避免通用 AI 美学
- 生产级别输出

---

### 8.6 场景六：项目规划与文档

**问题：** 新项目需要完整的规划文档

**解决方案：** 使用 project-planner Skill

```
/project-planner 规划一个 SSH 隧道管理工具：
- 技术栈：Go + Fyne GUI
- 目标平台：Windows
- 核心功能：连接管理、隧道配置、状态监控
```

**为什么有效：**
- 结构化输出
- 包含需求、设计、实现文档
- 可追踪的 TODO 列表

---

## 9. 常见问题与故障排除

### 9.1 Agent Teams

**Q: 队友没有出现？**
- 用 `↑` / `↓` 在 agent panel 选择，按 `Enter` 查看是否已运行但不可见
- 确认任务足够复杂（简单任务不会创建团队）
- 检查环境变量是否正确设置

**Q: 太多权限提示？**
- 在权限设置中预批准常见操作

**Q: Lead 提前结束工作？**
- 告诉 Lead 等待队友完成：`Wait for teammates to complete their tasks`

**Q: 任务状态卡住？**
- 检查任务是否实际已完成
- 手动更新状态或告诉 Lead 处理

### 9.2 Subagents

**Q: Subagent 超时？**
- 增加超时时间或简化任务

**Q: 结果不准确？**
- 提供更具体的指令和上下文

### 9.3 Hooks

**Q: Hook 不执行？**
- 检查命令路径是否正确
- 验证 JSON 语法
- 查看 Claude Code 日志

**Q: Hook 阻塞工作流？**
- 设置合理的 timeout
- 考虑使用 `async: true` 异步执行

### 9.4 通用问题

**Q: Token 消耗过高？**
- 减少队友数量
- 使用更小的模型（如 Haiku）用于简单任务
- 合并相关任务

**Q: 响应变慢？**
- 减少并行代理数量
- 检查网络连接
- 简化任务指令

---

## 附录 A：快速参考卡

### Agent Teams 快速命令

```
# 创建团队
Create an agent team to [task description]

# 切换队友
↑ / ↓（Enter 查看，x 停止）

# 查看任务
Ctrl + T

# 分配任务
Assign [task] to [teammate]

# 关闭队友
Ask [teammate] to shut down

# 清理团队（会话结束自动清理）
```

### Skills 快速调用

```
/simplify          # 代码质量审查
/frontend-design   # 前端设计
/project-planner   # 项目规划
/code-review       # 代码审查
/docx              # Word 文档
/pdf               # PDF 处理
```

### 环境变量

```
CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1   # 启用 Agent Teams
```

---

## 附录 B：配置模板

### 完整 settings.json 模板

```json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  },
  "hooks": {
    "TeammateIdle": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python ~/.claude/hooks/quality-check.py",
            "timeout": 30
          }
        ]
      }
    ],
    "TaskCompleted": [
      {
        "hooks": [
          {
            "type": "agent",
            "prompt": "Verify tests pass and code follows project conventions.",
            "timeout": 60
          }
        ]
      }
    ]
  },
  "permissions": {
    "allow": ["Read(**)", "Grep(**)", "Glob(**)"],
    "defaultMode": "default"
  },
  "effortLevel": "high"
}
```

---

*文档版本: 1.1*
*最后更新: 2026-07-04*
*适用于: Claude Code CLI*
*校对: Agent Teams / Skills 部分已按官方文档校对（research/16、research/13）；Hooks / Worktrees 部分待对照官方文档*
