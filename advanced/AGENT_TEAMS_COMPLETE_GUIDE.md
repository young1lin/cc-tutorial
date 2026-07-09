# Claude Code Agent Teams 完全指南

> 最全面的 Agent Teams 教程，涵盖从入门到精通的所有内容

---

## 目录

1. [概念与架构](#1-概念与架构)
2. [启用与配置](#2-启用与配置)
3. [显示模式详解](#3-显示模式详解)
4. [创建与管理团队](#4-创建与管理团队)
5. [任务系统](#5-任务系统)
6. [代理间通信](#6-代理间通信)
7. [计划审批机制](#7-计划审批机制)
8. [与 Subagents 对比](#8-与-subagents-对比)
9. [Token 成本与性能](#9-token-成本与性能)
10. [最佳应用场景](#10-最佳应用场景)
11. [高级用法](#11-高级用法)
12. [Hooks 集成](#12-hooks-集成)
13. [故障排除](#13-故障排除)
14. [局限性](#14-局限性)
15. [快速参考](#15-快速参考)

---

## 1. 概念与架构

### 1.1 什么是 Agent Teams

Agent Teams 是 Claude Code 的多代理协作系统，允许你同时运行多个 Claude Code 实例，它们可以：
- 并行处理独立任务
- 相互通信和协作
- 共享任务列表
- 自主协调工作流程

### 1.2 核心组件

```
┌─────────────────────────────────────────────────────────────┐
│                      Agent Team 架构                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐                                            │
│  │  Team Lead  │ ◄─── 主 Claude Code 会话                   │
│  │             │      • 创建团队                            │
│  │             │      • 协调工作                            │
│  │             │      • 综合结果                            │
│  └──────┬──────┘                                            │
│         │                                                   │
│         ▼                                                   │
│  ┌─────────────────────────────────────────────┐           │
│  │              Shared Task List               │           │
│  │  • 任务状态管理 (pending/in_progress/done)  │           │
│  │  • 依赖关系追踪                              │           │
│  │  • 自动解锁机制                              │           │
│  └─────────────────────────────────────────────┘           │
│         │                                                   │
│         ▼                                                   │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐       │
│  │Teammate│  │Teammate│  │Teammate│  │Teammate│       │
│  │   #1   │  │   #2   │  │   #3   │  │   #4   │       │
│  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘       │
│       │           │           │           │               │
│       └───────────┴───────────┴───────────┘               │
│                       │                                     │
│                       ▼                                     │
│              ┌──────────────┐                              │
│              │   Mailbox    │ ◄─── 代理间消息传递           │
│              └──────────────┘                              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 1.3 组件详解

| 组件 | 角色 | 职责 |
|------|------|------|
| **Team Lead** | 主会话 | 创建团队、生成队友、分配任务、综合结果、清理团队 |
| **Teammates** | 独立实例 | 处理分配的任务、报告进度、与其他队友通信 |
| **Task List** | 协调中心 | 管理任务状态、追踪依赖、解锁阻塞任务 |
| **Mailbox** | 通信系统 | 代理间消息传递、自动通知、广播 |

### 1.4 工作流程

```
1. 用户请求 → Team Lead 分析任务
                    ↓
2. Team Lead 创建团队 → 生成 Teammates → 创建 Task List
                    ↓
3. Teammates 启动 → 加载项目上下文 → 接收分配的任务
                    ↓
4. 并行工作 → 各 Teammate 独立处理任务
           → 通过 Mailbox 通信
           → 更新 Task List 状态
                    ↓
5. 任务完成 → Team Lead 综合结果 → 报告给用户
                    ↓
6. 清理 → 关闭 Teammates → 删除团队资源
```

---

### 1.5 落盘位置（官方 T1）

团队与任务按会话派生名存本地（团队名 = `session-` + 会话 ID 前 8 位）：

| 路径 | 内容 | 生命周期 |
|------|------|----------|
| `~/.claude/teams/{team-name}/config.json` | 运行时状态（会话 ID、tmux pane ID 等） | **会话结束删除** |
| `~/.claude/tasks/{team-name}/` | 共享任务列表 | **持久化**，恢复会话保留（受 `cleanupPeriodDays` 管） |

- team config 存运行时状态，**别手改或预写**——下次状态更新会覆盖。
- **没有项目级等价物**：项目里的 `.claude/teams/teams.json` 不被识别为配置，Claude 当普通文件对待。
- 要定义可复用的 teammate 角色，用 **subagent 定义**（见 11.5）。

## 2. 启用与配置

### 2.1 启用 Agent Teams

Agent Teams 是实验性功能，默认禁用。

**方法一：settings.json（推荐）**

```json
// 路径: ~/.claude/settings.json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  }
}
```

**方法二：环境变量**

```bash
# Windows PowerShell
$env:CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS = "1"

# Windows CMD
set CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1

# Linux/macOS
export CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1

# 或在启动时指定
CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1 claude
```

**方法三：命令行参数**

```bash
claude --teammate-mode in-process
```

### 2.2 配置选项

```json
// settings.json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  },
  // 其他相关配置
  "permissions": {
    "defaultMode": "default",
    "allow": [
      "Read(**)",
      "Glob(**)",
      "Grep(**)"
    ]
  },
  "hooks": {
    "TeammateIdle": [...],
    "TaskCompleted": [...]
  }
}
```

### 2.3 验证启用状态

启用后，在 Claude Code 中输入：

```
创建一个测试用的 agent team
```

如果功能已启用，Claude 会开始创建团队。如果未启用，Claude 会提示该功能未开启。

---

## 3. 显示模式详解

### 3.1 两种显示模式

Agent Teams 支持两种显示模式，各有优缺点：

#### In-Process 模式

```
┌─────────────────────────────────────┐
│  Terminal Window                     │
│  ┌─────────────────────────────────┐│
│  │ Team Lead View                  ││
│  │ > 创建团队...                   ││
│  │ > Teammate 1: Security Review   ││
│  │ > Teammate 2: Performance       ││
│  └─────────────────────────────────┘│
│                                      │
│  [↑/↓ 切换] ────────────────────────►│
│                                      │
│  ┌─────────────────────────────────┐│
│  │ Teammate 1 View                 ││
│  │ > 分析安全漏洞...               ││
│  │ > 发现 3 个潜在问题             ││
│  └─────────────────────────────────┘│
└─────────────────────────────────────┘
```

**特点：**
- 所有队友在同一终端窗口内
- 使用 `↑` / `↓` 方向键在 agent panel 切换不同队友
- 无需任何额外软件
- 适用于任何终端

**适用平台：**
- ✅ Windows（CMD、PowerShell、Windows Terminal）
- ✅ macOS（Terminal.app、iTerm2）
- ✅ Linux（所有终端）
- ✅ VS Code 集成终端

#### Split Panes 模式

```
┌─────────────────┬─────────────────┐
│   Team Lead     │   Teammate 1    │
│                 │                 │
│ > 协调中...     │ > 安全审查中... │
│                 │                 │
├─────────────────┼─────────────────┤
│   Teammate 2    │   Teammate 3    │
│                 │                 │
│ > 性能分析中... │ > 测试验证中... │
│                 │                 │
└─────────────────┴─────────────────┘
```

**特点：**
- 每个队友独立窗格
- 同时查看所有队友输出
- 点击窗格直接交互
- 需要特定终端支持

**适用平台：**
- ✅ macOS（需要 iTerm2 或 tmux）
- ✅ Linux（需要 tmux）
- ❌ Windows Terminal（不支持）
- ❌ VS Code 集成终端（不支持）

### 3.2 配置显示模式

**方法一：命令行参数**

```bash
# in-process 模式（v2.1.179 起为默认）
claude --teammate-mode in-process

# auto：在 tmux 会话内或 iTerm2 + it2 时启用 split panes，否则回退 in-process
claude --teammate-mode auto
```

**方法二：在 tmux 中自动启用 split panes**

```bash
# 先启动 tmux
tmux new -s claude-team

# 然后启动 Claude Code
claude

# 创建团队时会自动使用 split panes
```

> **默认模式与取值（官方，T1）**：`teammateMode` 取值 `in-process`（**v2.1.179 起为默认**）、`auto`、`tmux`、`iterm2`（v2.1.186 起，显式启用 iTerm2 原生分屏，需 `it2` CLI，缺失时报错并附安装命令）。v2.1.179 之前默认是 `auto`，升级后曾开 split panes 的会话会回到单终端，除非显式设置。可在 `~/.claude/settings.json` 写 `"teammateMode": "auto"`，或单次会话传 `claude --teammate-mode auto`。

### 3.3 macOS iTerm2 一键分屏配置（推荐）

**这是获得最佳 Agent Teams 体验的方式**。配置完成后，创建团队时会自动为每个队友打开独立窗格。

#### 步骤一：安装 iTerm2

```bash
# 使用 Homebrew 安装
brew install --cask iterm2

# 或手动下载: https://iterm2.com/
```

#### 步骤二：安装 it2 CLI 工具

```bash
brew install mkusaka/it2/it2
```

#### 步骤三：启用 iTerm2 Python API

1. 打开 iTerm2
2. 菜单栏点击 **iTerm2** → **Settings...** (或按 `⌘,`)
3. 选择 **General** 标签
4. 滚动到底部找到 **Magic** 部分
5. ✅ 勾选 **Enable Python API**

```
┌─────────────────────────────────────────────────────┐
│  iTerm2 Settings                                    │
├─────────────────────────────────────────────────────┤
│  General  Profiles  Appearance  Keys  ...          │
│                                                     │
│  ...                                                │
│                                                     │
│  ┌─────────────────────────────────────────────┐   │
│  │ Magic                                        │   │
│  │                                              │   │
│  │ ☑ Enable Python API           ← 勾选这个     │   │
│  │ ☐ Instant Replay Uses Less Memory           │   │
│  │ ☐ Shell Integration                         │   │
│  └─────────────────────────────────────────────┘   │
│                                                     │
└─────────────────────────────────────────────────────┘
```

#### 步骤四：验证配置

```bash
# 验证 it2 CLI 安装成功
it2 --version

# 启动 Claude Code
claude
```

#### 步骤五：创建团队 - 自动分屏

```bash
# 在 iTerm2 中启动 Claude Code
claude

# 输入创建团队命令
创建一个 3 人团队审查代码：安全、性能、测试覆盖率
```

**Claude Code 会自动：**
1. 检测到你在 iTerm2 中
2. 为 Team Lead 保留当前窗格
3. 为每个 Teammate 自动创建新窗格
4. 自动排列窗格布局

**最终效果：**

```
┌─────────────────┬─────────────────┐
│   Team Lead     │   Teammate 1    │
│   (协调者)      │   (安全审查)    │
│                 │                 │
├─────────────────┼─────────────────┤
│   Teammate 2    │   Teammate 3    │
│   (性能分析)    │   (测试验证)    │
│                 │                 │
└─────────────────┴─────────────────┘

你可以直接点击任意窗格与该队友交互！
```

#### 一键启动脚本（可选）

创建别名，一键启动 tmux + Claude Code：

```bash
# 添加到 ~/.zshrc 或 ~/.bashrc
alias ct='claude --teammate-mode auto'
alias cteam='tmux new-session -A -s claude "claude --teammate-mode auto"'
```

然后：
```bash
source ~/.zshrc
ct      # 直接启动
cteam   # tmux 模式启动
```

### 3.4 tmux 配置（Linux/备选方案）

**tmux 安装：**

```bash
# macOS
brew install tmux

# Ubuntu/Debian
sudo apt install tmux

# Fedora
sudo dnf install tmux

# Arch Linux
sudo pacman -S tmux
```

**使用 tmux 启动：**

```bash
# 创建 tmux 会话
tmux new -s claude

# 启动 Claude Code
claude

# 创建团队时会自动使用 tmux split panes
```

**tmux 常用快捷键：**

| 快捷键 | 功能 |
|--------|------|
| `Ctrl+B %` | 垂直分割窗格 |
| `Ctrl+B "` | 水平分割窗格 |
| `Ctrl+B 方向键` | 切换窗格 |
| `Ctrl+B d` | 分离会话 |
| `Ctrl+B c` | 新建窗口 |

### 3.5 Windows 平台配置

Windows 原生不支持 split panes 模式，推荐使用 **in-process 模式**：

```bash
# 直接启动即可
claude

# 使用 ↑/↓ 选择队友，Enter 查看
```

**Windows 上使用 tmux（需要 MSYS2）：**

```bash
# 安装 tmux（在 MSYS2 中）
pacman -S tmux

# 启动
tmux new -s claude
claude
```

> ⚠️ 注意：Windows + MSYS2 + tmux 体验不如 macOS/iTerm2，建议直接用 in-process 模式。

---

## 4. 创建与管理团队

### 4.1 创建团队的基本语法

```
创建一个 agent team [任务描述]
Create an agent team to [task description]
```

### 4.2 创建团队的方式

#### 方式一：自动推断

让 Claude 根据任务自动决定团队结构：

```
创建一个 agent team 审查当前代码库的代码质量
```

Claude 会：
1. 分析任务复杂度
2. 决定需要多少队友
3. 分配每个队友的职责
4. 创建任务列表

#### 方式二：指定队友数量

```
创建一个 5 人团队并行重构以下模块：
- internal/ssh/
- internal/storage/
- internal/ui/
- internal/api/
- internal/service/
```

#### 方式三：详细角色定义

```
创建一个 agent team 进行 PR #42 的全面审查：

Teammate 1 - Security Reviewer:
  • 检查 SQL 注入、XSS、CSRF
  • 验证认证和授权逻辑
  • 审查敏感数据处理

Teammate 2 - Performance Analyst:
  • 分析算法复杂度
  • 检查数据库查询效率
  • 识别内存泄漏风险

Teammate 3 - Code Quality Reviewer:
  • 检查代码风格一致性
  • 验证错误处理
  • 评估可维护性

Teammate 4 - Test Coverage Validator:
  • 验证单元测试覆盖
  • 检查边界条件测试
  • 确保集成测试完整
```

#### 方式四：指定模型

```
创建一个 3 人团队，使用不同模型：
- Teammate 1: 使用 Opus 进行深度架构分析
- Teammate 2: 使用 Sonnet 进行代码审查
- Teammate 3: 使用 Haiku 进行快速语法检查
```

> **模型继承（官方 T1）**：teammates **默认不继承** lead 的 `/model` 选择。改默认模型：在 `/config` 设 **Default teammate model**（选 "Default (leader's model)" 则跟随 lead）。但 teammates **继承 lead 的 effort level**（split-pane 自 v2.1.186 起）。teammate 的模型和 fast mode 在生成时固定，`/model`、`/fast` 只改 lead 设置。

### 4.3 管理团队

#### 查看团队状态

```
显示团队状态
Show me the team status
```

#### 查看任务列表

```
显示任务列表
Show the task list
```
或按 `Ctrl + T`

#### 与队友交互

```
# 查询队友进度
Ask the security reviewer about their findings

# 给队友额外指令
Tell the architect teammate to also consider scalability

# 重定向队友工作
Ask the tester to focus on edge cases instead
```

#### 关闭单个队友

```
Ask the researcher teammate to shut down
```

#### 关闭整个团队

会话结束时团队的共享目录（team config 等）会**自动清理**，无需单独 cleanup 步骤（官方 T1）；任务列表目录则保留，供恢复会话用。中途想结束整个团队，逐个让队友关闭或直接退出会话即可：

```
Ask the researcher teammate to shut down
```

### 4.4 团队操作快捷键

| 快捷键 | 功能 | 说明 |
|--------|------|------|
| `↑` / `↓` | 选择队友 | 在 agent panel 中上下移动 |
| `Enter` | 查看详情 | 进入队友会话，可直接打字发消息 |
| `x` | 停止队友 | 选中队友时按 `x` 停止它 |
| `Escape` | 中断 | 中断队友当前操作 |
| `Ctrl + T` | 任务列表 | 切换任务列表视图 |

---

## 5. 任务系统

### 5.1 任务状态

```
┌─────────────────────────────────────────────────┐
│              Task State Machine                 │
├─────────────────────────────────────────────────┤
│                                                 │
│   ┌──────────┐                                  │
│   │ PENDING  │ ◄─── 任务创建                    │
│   └────┬─────┘                                  │
│        │ (被分配或自领取)                        │
│        ▼                                        │
│   ┌──────────────┐                              │
│   │ IN_PROGRESS  │ ◄─── 正在处理                │
│   └──────┬───────┘                              │
│          │                                      │
│          ▼                                      │
│   ┌───────────┐                                 │
│   │ COMPLETED │ ◄─── 任务完成                   │
│   └───────────┘                                 │
│                                                 │
│   依赖阻塞: PENDING → BLOCKED                   │
│   依赖解除: BLOCKED → PENDING                   │
│                                                 │
└─────────────────────────────────────────────────┘
```

### 5.2 任务依赖

任务可以设置依赖关系，被依赖的任务完成后，依赖它的任务才能开始：

```
创建团队开发用户认证功能：

任务 1: 设计认证 API 接口 (无依赖)
任务 2: 实现后端认证逻辑 (依赖任务 1)
任务 3: 实现前端登录页面 (依赖任务 1)
任务 4: 编写集成测试 (依赖任务 2 和 3)
任务 5: 更新文档 (依赖任务 4)
```

### 5.3 任务分配方式

#### Lead 分配

```
Assign the security review task to the security teammate
```

Lead 明确指定哪个队友处理哪个任务。

#### 自主领取

队友完成任务后，会自动领取下一个：
- 未分配的
- 未被阻塞的
- 优先级最高的

任务使用文件锁防止竞争条件。

### 5.4 任务粒度建议

| 粒度 | 描述 | 建议 |
|------|------|------|
| 太小 | "修复这个 typo" | ❌ 开销大于收益 |
| 太大 | "重构整个项目" | ❌ 难以追踪和协调 |
| 合适 | "重构 auth 模块并添加测试" | ✅ 明确交付物 |

**好的任务特征：**
- 自包含单元
- 有明确的交付物
- 可以在合理时间内完成
- 与其他任务文件不冲突

---

## 6. 代理间通信

### 6.1 通信机制

```
┌─────────────────────────────────────────────────────┐
│                 Communication Flow                   │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Teammate A          Mailbox          Teammate B   │
│      │                 │                   │        │
│      │─── message ────►│                   │        │
│      │                 │─── deliver ─────►│        │
│      │                 │                   │        │
│      │                 │◄── response ─────│        │
│      │◄── deliver ─────│                   │        │
│      │                 │                   │        │
│      │                 │                   │        │
│      │═════════════════│═══════════════════│        │
│      │     Broadcast   │                   │        │
│      │────────────────►│─── to all ───────►│        │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### 6.2 消息类型

#### 直接消息

发送给特定队友：

```
Ask the architect teammate to share their API design
```

Teammate 收到消息后会在自己的上下文中处理。

#### 群发消息（按接收方逐条发送）

官方**没有原生广播原语**（T1）。要触达所有队友，给每个接收方各发一条消息——"Tell all teammates..." 这类指令实际会被拆成 N 条按名点对点消息：

```
Tell all teammates that the API schema has changed
```

**注意：** 成本随接收方数量线性增长（每条单独处理），应谨慎使用。

### 6.3 自动通知

系统自动发送的通知：

| 通知类型 | 触发时机 | 接收者 |
|----------|----------|--------|
| Idle Notification | 队友完成当前工作变为空闲 | Team Lead |
| Task Completed | 任务标记为完成 | Team Lead + 所有队友 |
| Task Unblocked | 阻塞任务完成，依赖任务解锁 | 相关队友 |
| Peer DM Summary | 队友间直接消息 | Team Lead（仅摘要） |

### 6.4 通信最佳实践

**DO:**
```
# 具体明确
Ask the security reviewer: "Did you find any SQL injection vulnerabilities in the auth module?"

# 及时同步
Tell all teammates: The database schema has been updated, please check docs/schema.md
```

**DON'T:**
```
# 频繁广播（成本高）
Tell all teammates: I'm still working...  # 每 5 分钟一次

# 模糊消息
Ask the teammate something  # 哪个 teammate？什么问题？
```

---

## 7. 计划审批机制

### 7.1 什么是计划审批

对于复杂或高风险任务，可以让队友先制定计划，由 Lead 审批后才能实施：

```
┌─────────────────────────────────────────────────────┐
│              Plan Approval Workflow                  │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌──────────┐      ┌──────────┐                    │
│  │ Plan Mode│ ───► │  Submit  │                    │
│  │(readonly)│      │  Plan    │                    │
│  └──────────┘      └────┬─────┘                    │
│                         │                          │
│                         ▼                          │
│                    ┌─────────┐                     │
│                    │  Lead   │                     │
│                    │ Review  │                     │
│                    └────┬────┘                     │
│                         │                          │
│              ┌──────────┴──────────┐               │
│              ▼                     ▼               │
│         ┌─────────┐          ┌──────────┐         │
│         │ Approve │          │  Reject  │         │
│         └────┬────┘          └────┬─────┘         │
│              │                    │               │
│              ▼                    ▼               │
│      ┌──────────────┐     ┌──────────────┐       │
│      │ Exit Plan    │     │ Revise Plan  │       │
│      │ Start Work   │     │ Stay in Mode │       │
│      └──────────────┘     └──────────────┘       │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### 7.2 启用计划审批

```
创建一个架构师队友重构认证模块，要求在实施前获得计划审批。
Spawn an architect teammate to refactor the authentication module.
Require plan approval before they make any changes.
```

### 7.3 审批流程

**1. 队友进入 Plan Mode**
- 只读访问代码库
- 可以分析、设计、规划
- 不能修改任何文件

**2. 提交计划**
- 队友完成规划后发送审批请求
- 请求包含详细的实施计划

**3. Lead 审批**
- Lead 自动审查计划
- 可接受或拒绝

**4a. 接受 → 实施**
- 队友退出 Plan Mode
- 开始实施更改

**4b. 拒绝 → 修改**
- 队友收到反馈
- 继续在 Plan Mode 中修改
- 重新提交

### 7.4 影响审批决策

可以给 Lead 设定审批标准：

```
创建重构队友，要求计划审批。
只批准包含测试覆盖的计划。
拒绝任何修改数据库 schema 的计划。
```

### 7.5 手动干预

用户可以随时手动干预：

```
# 手动批准
Approve the architect's plan

# 手动拒绝并提供反馈
Reject the plan - need more details on error handling
```

---

## 8. 与 Subagents 对比

### 8.1 核心区别

```
┌─────────────────────────────────────────────────────────────┐
│                    Agent Teams vs Subagents                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Agent Teams                    Subagents                   │
│  ─────────────                  ──────────                  │
│                                                             │
│  ┌─────────┐ ┌─────────┐      ┌─────────────────────┐      │
│  │Lead     │ │Teammate │      │ Main Session        │      │
│  │         │ │    1    │      │                     │      │
│  │         │ │         │      │  ┌───────┐         │      │
│  │         │ │         │      │  │Sub-   │ Results │      │
│  │         │ │         │◄─────┤  │agent  │────────►│      │
│  │         │ │         │      │  └───────┘         │      │
│  │         │ │         │      │                     │      │
│  │         │ │         │      └─────────────────────┘      │
│  │         │ │         │                                   │
│  │         │ │Teammate │      特点:                         │
│  │         │ │    2    │      • 单向报告                    │
│  │         │ │         │      • 结果汇总回主会话            │
│  │         │ │         │      • 无代理间通信                │
│  └─────────┘ └─────────┘                                   │
│                                                             │
│  特点:                                                      │
│  • 双向通信                                                 │
│  • 代理间可协作                                             │
│  • 共享任务列表                                             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 8.2 详细对比表

| 特性 | Agent Teams | Subagents |
|------|-------------|-----------|
| **上下文** | 完全独立实例 | 独立窗口，结果返回调用者 |
| **通信方式** | 代理间直接通信 | 只报告给主代理 |
| **协调机制** | 共享任务列表，自协调 | 主代理管理所有工作 |
| **并行能力** | 强（可同时运行多个） | 中（可并行但有限制） |
| **Token 成本** | 高（每个队友独立 context） | 较低（结果汇总） |
| **复杂任务** | ✅ 适合 | ⚠️ 可能不足 |
| **简单任务** | ⚠️ 开销大 | ✅ 非常适合 |
| **代理间协作** | ✅ 支持 | ❌ 不支持 |
| **任务依赖** | ✅ 完整支持 | ❌ 不支持 |
| **状态持久化** | ✅ 独立持久化 | ❌ 随主会话 |

### 8.3 选择决策树

```
需要多代理协作？
│
├── 是 ──► 代理间需要通信/协作？
│          │
│          ├── 是 ──► Agent Teams
│          │          例: 竞争假设调试、跨模块开发
│          │
│          └── 否 ──► 任务是否复杂/需要独立上下文？
│                     │
│                     ├── 是 ──► Agent Teams
│                     │          例: 独立模块重构
│                     │
│                     └── 否 ──► Subagents
│                                例: 代码搜索、快速验证
│
└── 否 ──► 单会话即可
```

### 8.4 使用场景示例

**Agent Teams 更适合：**

```
# 需要协作
创建团队调试连接断开问题，让队友们互相质疑对方的假设

# 需要独立上下文
创建团队开发三个独立模块，每个队友只负责自己的文件集

# 需要共享状态
创建团队进行 PR 审查，共享发现的清单，避免重复检查
```

**Subagents 更适合：**

```
# 快速搜索
使用 subagent 搜索所有 deprecated API 的使用

# 验证任务
生成 subagent 验证测试是否全部通过

# 轻量研究
让 subagent 快速调研一下这个库的用法
```

---

## 9. Token 成本与性能

### 9.1 Token 消耗模型

```
┌─────────────────────────────────────────────────────────┐
│                 Token Cost Model                         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Total Cost = Lead Context + Σ(Teammate Context)        │
│                                                         │
│  ┌─────────────┐                                        │
│  │Lead Context │ ≈ 基础会话成本                          │
│  └─────────────┘                                        │
│                                                         │
│  ┌───────────────────┐                                  │
│  │Teammate Context   │ = 项目上下文 + 任务上下文         │
│  │                   │ + 对话历史 + 通信消息             │
│  └───────────────────┘                                  │
│                                                         │
│  每个 Teammate 都有独立的 context window                │
│  成本随队友数量线性增长                                  │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 9.2 成本估算

> **[Author's analysis]** 官方未公布具体倍数，仅说明 token 用量"显著高于单会话"且"随活跃队友数线性增长"（[T1 官方文档](https://code.claude.com/docs/en/agent-teams)）。下表为本教程的**量级估算（T4，非实测）**：

| 配置 | 相对成本（T4 估算） | 说明 |
|------|----------|------|
| 单会话 | 1x（基准） | 基准 |
| N 个队友 | ≈ 线性增长 | 每个队友独立 context window，成本随队友数近似线性上升 |

### 9.3 成本优化策略

**1. 控制团队规模**
```
# 不推荐
创建一个 10 人团队...

# 推荐
创建一个 3 人团队...
```

**2. 使用更小的模型**
```
创建 3 人团队，使用 Haiku 模型进行简单的代码格式化
```

**3. 精简任务描述**
```
# 不推荐（冗长）
创建一个团队，Teammate 1 负责...（1000 字描述）

# 推荐（精简）
创建团队审查代码安全性、性能、测试覆盖率
```

**4. 合并相似任务**
```
# 不推荐
Teammate 1: 检查 SQL 注入
Teammate 2: 检查 XSS
Teammate 3: 检查 CSRF

# 推荐
Teammate 1: 安全审查（SQL注入、XSS、CSRF）
```

### 9.4 性能优化

**并行度选择：**

| 任务数量 | 推荐队友数 | 原因 |
|----------|------------|------|
| 1-2 | 1-2 | 开销小 |
| 3-5 | 2-3 | 平衡 |
| 6-10 | 3-4 | 避免过多协调 |
| 10+ | 4-5 | 分批处理 |

**避免瓶颈：**
- 确保任务独立，减少依赖
- 每个队友负责不同文件
- 定期检查进度，及时调整

---

## 10. 最佳应用场景

### 10.1 场景一：并行代码审查

**问题描述：**
单人代码审查容易遗漏特定类型的问题，且难以同时关注多个维度。

**解决方案：**

```
Create an agent team to review PR #42. Spawn three reviewers:

Teammate 1 - Security Reviewer:
  • Authentication and authorization vulnerabilities
  • SQL injection, XSS, CSRF risks
  • Sensitive data handling
  • Input validation

Teammate 2 - Performance Analyst:
  • Algorithm complexity analysis
  • Database query optimization
  • Memory leak detection
  • Resource usage patterns

Teammate 3 - Test Coverage Validator:
  • Unit test coverage verification
  • Edge case testing
  • Integration test completeness
  • Mock quality assessment

Each reviewer works independently and reports findings.
The lead synthesizes all findings into a comprehensive review.
```

**为什么有效：**
- 每个审查者有明确的专业领域
- 并行工作节省时间
- 独立视角减少盲点
- 结果综合更全面

---

### 10.2 场景二：竞争假设调试

**问题描述：**
复杂 Bug 的根因不明时，单人调查容易锚定在第一个看似合理的理论。

**解决方案：**

```
用户报告应用在发送消息后意外退出，而不是保持连接。
生成 5 个 agent teammates 调查以下独立假设：

Teammate 1: 内存泄漏导致 OOM
  • 检查内存分配模式
  • 查找未释放的资源
  • 分析 goroutine 泄漏

Teammate 2: 网络超时处理不当
  • 检查连接超时配置
  • 验证错误恢复逻辑
  • 分析网络状态处理

Teammate 3: 并发竞态条件
  • 检查共享状态访问
  • 验证锁使用正确性
  • 分析 goroutine 同步

Teammate 4: 配置解析错误
  • 检查配置加载逻辑
  • 验证默认值处理
  • 分析配置验证

Teammate 5: 第三方库 bug
  • 检查库版本和已知 issue
  • 验证库的使用方式
  • 分析库的错误处理

让他们互相交流质疑对方的理论，像科学辩论一样。
更新 findings.md 文档记录最终共识。
```

**为什么有效：**
- 避免确认偏误
- 多角度独立验证
- 辩论机制确保结论可靠
- 比顺序调查更快找到根因

---

### 10.3 场景三：跨层功能开发

**问题描述：**
新功能涉及前端、后端、数据库等多层，单人开发上下文切换成本高。

**解决方案：**

```
创建团队开发用户通知系统，按层次分配工作：

Teammate 1 - Frontend Developer:
  负责: internal/ui/views/notification*.go
  任务:
    • 通知列表 UI 组件
    • 通知详情弹窗
    • WebSocket 状态显示
    • Toast 通知组件

Teammate 2 - Backend API Developer:
  负责: internal/api/notification*.go
  任务:
    • REST API 端点 (CRUD)
    • WebSocket 连接管理
    • 请求验证和处理

Teammate 3 - Database/Model Developer:
  负责: internal/models/notification*.go
  任务:
    • 数据模型定义
    • 数据库迁移脚本
    • 查询优化

Teammate 4 - Service Layer Developer:
  负责: internal/service/notification*.go
  任务:
    • 业务逻辑实现
    • 邮件/推送发送
    • 通知规则引擎

Teammate 5 - Test Developer:
  负责: internal/**/*notification*_test.go
  任务:
    • 单元测试
    • 集成测试
    • E2E 测试场景

约束: 每个队友只能修改自己负责的文件，避免冲突。
```

**为什么有效：**
- 文件隔离，无合并冲突
- 专业分工，质量更高
- 并行开发，缩短周期
- 每人专注自己的领域

---

### 10.4 场景四：研究与调研

**问题描述：**
需要在多个方向并行调研，综合比较后做出决策。

**解决方案：**

```
创建一个研究团队，调研三个不同的日志框架：

Teammate 1: zap (Uber) 研究员
  • 性能基准
  • API 易用性
  • 社区活跃度
  • 集成复杂度

Teammate 2: logrus 研究员
  • 性能基准
  • API 易用性
  • 社区活跃度
  • 集成复杂度

Teammate 3: zerolog 研究员
  • 性能基准
  • API 易用性
  • 社区活跃度
  • 集成复杂度

完成后互相比较，给出推荐方案和理由。
```

**为什么有效：**
- 每个框架深度研究
- 并行进行节省时间
- 统一评估标准
- 综合比较更客观

---

### 10.5 场景六：大规模重构

**问题描述：**
需要对多个模块进行重构，模块间相对独立但需要协调。

**解决方案：**

```
创建团队重构认证系统，分模块并行：

Teammate 1: 认证核心模块
  文件: internal/auth/core/
  任务:
    • 重构 token 生成逻辑
    • 实现 refresh token 机制
    • 添加 token 黑名单

Teammate 2: 密码处理模块
  文件: internal/auth/password/
  任务:
    • 升级哈希算法到 bcrypt
    • 添加密码强度验证
    • 实现密码重置流程

Teammate 3: 会话管理模块
  文件: internal/auth/session/
  任务:
    • 重构会话存储
    • 添加并发安全
    • 实现会话过期

Teammate 4: 测试更新
  文件: internal/auth/**/*_test.go
  任务:
    • 更新现有测试
    • 添加新功能测试
    • 确保覆盖率 > 80%

要求: 每个模块完成后通知其他队友，确保接口兼容。
```

**为什么有效：**
- 模块隔离，独立重构
- 接口协调，保证兼容
- 并行进行，效率更高
- 测试同步更新

---

## 11. 高级用法

### 11.1 混合模型团队

不同任务使用不同模型以优化成本和效果：

```
创建混合模型团队分析系统架构：

Teammate 1 (Opus): 深度架构分析
  • 复杂度高，需要深度思考
  • 使用最强大的模型

Teammate 2 (Sonnet): 代码审查
  • 平衡能力和成本
  • 标准审查任务

Teammate 3 (Haiku): 快速扫描
  • 简单模式匹配
  • 语法和格式检查
```

### 11.2 动态团队调整

在团队运行中调整：

```
# 添加新队友
添加一个新的队友专门处理文档更新

# 移除队友
Ask the syntax checker to shut down - we don't need that anymore

# 修改任务
Update the security review task to also check for SSRF vulnerabilities

# 重新分配
Reassign the database task from Teammate 2 to Teammate 3
```

### 11.3 嵌套协调模式

虽然不支持嵌套团队，但可以通过 Lead 协调：

```
创建主团队，Lead 作为总协调者：

Team Lead:
  • 协调三个工作流
  • 综合所有结果
  • 处理跨领域问题

Teammate 1: 前端工作流协调
  • 子任务: UI 组件、状态管理、样式
  • 自行组织这些子任务

Teammate 2: 后端工作流协调
  • 子任务: API、数据库、缓存
  • 自行组织这些子任务

Teammate 3: 测试工作流协调
  • 子任务: 单元测试、集成测试、E2E
  • 自行组织这些子任务
```

### 11.4 外部工具集成

通过 Hooks 集成外部工具：

```json
// settings.json
{
  "hooks": {
    "TaskCompleted": [
      {
        "hooks": [
          {
            "type": "http",
            "url": "https://api.example.com/notify",
            "headers": {
              "Authorization": "Bearer $API_TOKEN"
            },
            "allowedEnvVars": ["API_TOKEN"]
          }
        ]
      }
    ]
  }
}
```

---

### 11.5 用 subagent 定义复用为 teammate 角色

生成 teammate 时可引用任何 scope（project / user / plugin / CLI）的 subagent 类型，把一个角色（如 `security-reviewer`）定义一次，既作委托 subagent 又作 teammate 复用（官方 T1）：

```
Spawn a teammate using the security-reviewer agent type to audit the auth module.
```

该 teammate 遵守定义的 `tools` allowlist 和 `model`；定义体**追加**进系统 prompt（非替换）。即便 `tools` 限制了别的工具，`SendMessage` 和任务管理工具对 teammate **始终可用**。

---

## 12. Hooks 集成

### 12.1 TeammateIdle Hook

队友空闲时触发，可用于质量检查或继续工作：

```json
{
  "hooks": {
    "TeammateIdle": [
      {
        "hooks": [
          {
            "type": "agent",
            "prompt": "Verify the teammate's work quality. Check: 1) Code follows project conventions 2) Tests exist for new code 3) No obvious bugs. If issues found, provide feedback to continue working.",
            "timeout": 60
          }
        ]
      }
    ]
  }
}
```

**Exit Codes:**
- `0`: 正常，队友可以继续或结束
- `2`: 发送反馈，队友继续工作

### 12.2 TaskCompleted Hook

任务完成时触发，可用于验证或阻止完成：

```json
{
  "hooks": {
    "TaskCompleted": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "go test ./... -v",
            "timeout": 120
          }
        ]
      }
    ]
  }
}
```

**Exit Codes:**
- `0`: 任务可以标记为完成
- `2`: 阻止完成，发送反馈

### 12.3 TaskCreated Hook

任务被创建时触发，可用于校验任务 schema 或阻止创建（官方 T1）：

```json
{
  "hooks": {
    "TaskCreated": [
      {
        "hooks": [
          {
            "type": "prompt",
            "prompt": "Reject the task if it lacks an acceptance criterion. Otherwise allow.",
            "timeout": 30
          }
        ]
      }
    ]
  }
}
```

**Exit Codes:**
- `0`: 任务正常创建
- `2`: 阻止创建，发送反馈

### 12.4 完整配置示例

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
            "type": "prompt",
            "prompt": "Evaluate teammate output quality. Consider: code style, test coverage, documentation. Return 'pass' or 'fail: [reason]'",
            "model": "claude-haiku-4-5-20251001",
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
            "prompt": "Verify task completion: 1) All tests pass 2) No lint errors 3) Documentation updated if needed. Use $ARGUMENTS for task details.",
            "timeout": 90
          }
        ]
      }
    ]
  }
}
```

---

## 13. 故障排除

### 13.1 队友不出现

**症状：** 请求创建团队后，没有看到队友

**可能原因和解决方案：**

| 原因 | 解决方案 |
|------|----------|
| 功能未启用 | 检查 `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` |
| 任务太简单 | Claude 可能判断不需要团队，增加任务复杂度 |
| 队友在后台 | 用 `↑` / `↓` 在 agent panel 选择，按 `Enter` 查看 |
| 配置错误 | 检查 settings.json 语法 |

**验证步骤：**
```bash
# 检查环境变量
echo $CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS  # Linux/macOS
echo %CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS% # Windows CMD
$env:CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS   # Windows PowerShell
```

### 13.2 太多权限提示

**症状：** 队友频繁请求权限确认

**解决方案：**

```json
// settings.json
{
  "permissions": {
    "allow": [
      "Read(**)",
      "Glob(**)",
      "Grep(**)",
      "Bash(go test*)",
      "Bash(git *)"
    ],
    "defaultMode": "dontAsk"
  }
}
```

> **权限安全约束（官方 T1）**：
> - teammates 以 lead 的权限设置启动；lead 跑 `--dangerously-skip-permissions` 则所有 teammates 也是。
> - 生成后可改单个 teammate 的模式，但**生成时不能逐个设**。
> - **teammate 不能替你批准权限提示或提供同意**；被拒的动作不能转发给另一个 teammate 绕过检查。
> - auto 模式下，分类器把"从别的 agent 转来的批准声明"当**不可信输入**。
> - teammate 的权限提示**冒泡到 lead 会话**——在那里自己批准。

### 13.3 队友遇到错误停止

**症状：** 队友遇到错误后不再继续

**解决方案：**
1. 切换到该队友：用 `↑` / `↓` 在 agent panel 选择，`Enter` 查看
2. 查看错误信息
3. 给予额外指令：
   ```
   Continue with an alternative approach, or skip this task if blocked
   ```
4. 或生成替代队友：
   ```
   Spawn a new teammate to continue the security review task
   ```

### 13.4 Lead 提前结束

**症状：** Lead 认为工作完成，但任务尚未完成

**解决方案：**
```
Wait for all teammates to complete their tasks before finishing.
Check the task list to ensure everything is done.
```

### 13.5 任务状态卡住

**症状：** 任务显示 in_progress 但实际已完成

**解决方案：**
```
# 手动更新状态
Mark task #3 as completed

# 或让 Lead 处理
Check task status and update if work is done
```

### 13.6 Split Panes 不工作

**症状：** 请求 split panes 但不显示

**可能原因：**
- 不在 tmux 会话中
- iTerm2 Python API 未启用
- 不支持的终端

**解决方案：**
```bash
# 检查是否在 tmux 中
echo $TMUX

# 如果为空，先启动 tmux
tmux new -s claude

# 然后启动 Claude Code
claude
```

### 13.7 Orphaned tmux Sessions

**症状：** 团队结束后 tmux session 仍然存在

**解决方案：**
```bash
# 列出所有 session
tmux ls

# 删除特定 session
tmux kill-session -t session-name

# 删除所有 Claude 相关 session
tmux ls | grep claude | cut -d: -f1 | xargs -I {} tmux kill-session -t {}
```

---

## 14. 局限性

### 14.1 当前限制

| 限制 | 说明 | 变通方案 |
|------|------|----------|
| 无会话恢复 | `/resume` 不恢复 in-process 队友 | 重新生成队友 |
| 任务状态滞后 | 队友有时忘记标记完成 | 手动更新或让 Lead 检查 |
| 关闭较慢 | 队友需完成当前工具调用 | 耐心等待 |
| 一个团队/会话 | 每个会话只能管理一个团队 | 清理后再创建 |
| 无嵌套团队 | 队友不能创建子团队 | 通过 Lead 协调 |
| Lead 固定 | 不能更换或提升队友 | 在 Lead 中处理 |
| Split panes 限制 | 需要 tmux 或 iTerm2 | 使用 in-process 模式 |
| in-process 队友无后台 subagent | in-process teammate 的 subagents 跑前台；`run_in_background` 或 frontmatter `background: true` 会报错（官方 T1） | 让 teammate 用前台 subagent，或从主会话起后台 subagent |
| 权限生成时定 | 所有队友以 lead 权限启动，生成时不能逐个设 | 生成后再改单个 teammate 模式 |

### 14.2 已知问题

1. **消息延迟**: 高负载时消息可能有延迟
2. **任务竞争**: 极少数情况下两个队友可能尝试领取同一任务
3. **上下文丢失**: 长时间运行的队友可能丢失早期上下文

### 14.3 不适用场景

**不推荐使用 Agent Teams：**

- 简单的单步任务
- 需要频繁编辑同一文件
- 顺序依赖强的任务
- Token 预算有限的情况
- 需要即时响应的交互

---

## 15. 快速参考

### 15.1 启用命令

```bash
# settings.json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  }
}
```

### 15.2 创建团队

```
创建一个 agent team [任务描述]
Create an agent team to [task description]
```

### 15.3 快捷键

| 快捷键 | 功能 |
|--------|------|
| `↑` / `↓` | 选择队友 |
| `Enter` | 查看 / 进入队友 |
| `x` | 停止选中队友 |
| `Escape` | 中断队友 |
| `Ctrl + T` | 任务列表 |

### 15.4 常用命令

```
# 团队管理
Show team status
Show task list
# 共享目录在会话结束时自动清理，无需手动 cleanup

# 队友交互
Ask [teammate] to [action]
Tell [teammate] that [information]

# 任务管理
Assign [task] to [teammate]
Mark task #[n] as completed

# 关闭
Ask [teammate] to shut down
```

### 15.5 最佳实践清单

- [ ] 团队规模: 3-5 队友
- [ ] 任务/队友: 5-6 任务每人
- [ ] 文件隔离: 每队友不同文件集
- [ ] 任务粒度: 明确交付物
- [ ] 定期检查: 监控进度
- [ ] 等待队友: Lead 不要提前动手

---

## 附录：术语表

| 术语 | 定义 |
|------|------|
| **Agent Team** | 多个 Claude Code 实例协同工作的团队 |
| **Team Lead** | 主会话，负责创建和协调团队 |
| **Teammate** | 独立的 Claude Code 实例，处理分配的任务 |
| **Task List** | 共享的任务列表，管理任务状态和依赖 |
| **Mailbox** | 代理间消息传递系统 |
| **In-Process Mode** | 所有队友在同一终端的显示模式 |
| **Split Panes Mode** | 每个队友独立窗格的显示模式 |
| **Plan Mode** | 只读规划模式，需审批后才能实施 |
| **Subagent** | 轻量级子代理，用于简单委托任务 |

---

*文档版本: 2.1*
*最后更新: 2026-07-04*
*适用于: Claude Code CLI - Agent Teams Feature*
*校对来源: [官方文档](https://code.claude.com/docs/en/agent-teams)（截至 v2.1.199），见 research/16-claude-code-agent-teams.md*
