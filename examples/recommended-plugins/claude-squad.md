# 工具：claude-squad

## 概述

`claude-squad` 是一个多代理并行管理工具，使用 tmux 管理多个终端会话 + git worktrees 隔离工作区，让多个 AI 代理同时处理不同任务。

**Stars**: 5,600+
**GitHub**: `smtg-ai/claude-squad`
**类型**: 独立 CLI 工具
**依赖**: tmux（多终端管理）

**解决的核心问题**：
单个 Claude Code 实例是串行处理任务的。在处理大型项目时，如果能让多个代理并行工作（一个写代码、一个写测试、一个写文档），效率会大幅提升。

**使用场景**:
- 并行开发多个功能，最后合并
- 一个代理写实现，另一个同时写测试
- 大型重构：各个模块并行处理
- 代码库迁移：前端/后端/数据库层并行处理

---

## 安装

### npm

```bash
npm install -g claude-squad
```

### 从源码编译（Go）

```bash
git clone https://github.com/smtg-ai/claude-squad
cd claude-squad
go build -o claude-squad .
sudo mv claude-squad /usr/local/bin/
```

### 前置依赖

```bash
# macOS
brew install tmux

# Linux
sudo apt-get install tmux
# 或
sudo yum install tmux
```

---

## 工作原理

```
claude-squad start
        │
        ▼
┌─────────────────────────────────────────┐
│            tmux 会话管理                 │
│                                         │
│  ┌──────────┐  ┌──────────┐  ┌───────┐ │
│  │ 代理 1   │  │ 代理 2   │  │ 代理 3│ │
│  │ (功能A)  │  │ (测试A)  │  │ (文档)│ │
│  └────┬─────┘  └────┬─────┘  └───┬───┘ │
│       │             │             │     │
└───────┼─────────────┼─────────────┼─────┘
        │             │             │
        ▼             ▼             ▼
┌─────────────┐ ┌──────────┐ ┌──────────┐
│ worktree/   │ │worktree/ │ │worktree/ │
│ feature-a   │ │ tests    │ │  docs    │
└─────────────┘ └──────────┘ └──────────┘
        │             │             │
        └──────────────┴─────────────┘
                       │
                       ▼
              git merge / 人工审查
```

每个代理运行在独立的 git worktree 中，互不干扰，完成后合并。

---

## 核心命令

```bash
# 启动 claude-squad TUI（终端 UI）
claude-squad

# 常用快捷键（在 TUI 中）
n    # 新建代理实例
d    # 删除代理实例
q    # 退出 TUI（代理继续后台运行）
↑↓   # 切换代理
Enter # 进入代理终端
```

---

## 实际演示

### 场景 1：功能开发 + 测试并行

```bash
# 启动 claude-squad
$ claude-squad

# 在 TUI 中按 n 新建第一个代理
# 选择工作目录：./worktrees/feature-payment
# 代理指令：
"实现支付模块 PaymentService，包含：
- 创建订单
- 处理支付回调
- 退款逻辑
基于现有的 OrderService 模式"

# 按 n 新建第二个代理
# 选择工作目录：./worktrees/test-payment
# 代理指令：
"为 PaymentService 编写完整的单元测试，
覆盖正常流程和边界情况（支付失败、网络超时、重复回调）"

# 两个代理并行工作...

# 完成后合并
cd worktrees/feature-payment
git checkout main
git merge feature-payment
git merge test-payment  # 或 cherry-pick 测试文件
```

### 场景 2：大型代码库迁移（JS → TS）

```bash
# 三个代理分别处理不同层
# 代理 1：前端组件迁移
"将 src/components/ 下所有 .js 文件迁移到 TypeScript，
添加严格类型，不改变组件行为"

# 代理 2：API 层迁移
"将 src/api/ 下所有 .js 文件迁移到 TypeScript，
为所有请求/响应添加接口定义"

# 代理 3：工具函数迁移
"将 src/utils/ 下所有 .js 文件迁移到 TypeScript，
确保工具函数都有正确的泛型支持"
```

### 场景 3：混合不同 AI 代理

claude-squad 支持混合使用不同的 AI 代理：

```bash
# 代理 1：Claude Code（主要开发）
# 代理 2：Aider（擅长重构）
# 代理 3：OpenHands（处理特定任务）
```

---

## 配置文件

创建 `.claude-squad.yaml`：

```yaml
# .claude-squad.yaml
default_agent: claude-code

worktrees:
  base_dir: ./worktrees
  auto_cleanup: true  # 合并后自动清理

agents:
  - name: feature-dev
    agent: claude-code
    prompt_template: "实现功能：{task}"

  - name: test-writer
    agent: claude-code
    prompt_template: "为 {feature} 编写测试"

tmux:
  session_prefix: cs
  layout: tiled  # even-horizontal, even-vertical, tiled
```

---

## 进度监控

```bash
# 查看所有代理状态
claude-squad status

# 输出示例：
╔═══════════════════════════════════════════╗
║  claude-squad Status                      ║
╠═══════════════════════════════════════════╣
║ Agent 1 (feature-a)    ▶ Running  [45m]   ║
║ Agent 2 (test-a)       ✓ Done     [38m]   ║
║ Agent 3 (docs)         ▶ Running  [12m]   ║
╚═══════════════════════════════════════════╝

# 查看特定代理的输出
claude-squad logs 1
```

---

## 常见问题

### Q1: git worktrees 是什么，安全吗？

**A**: git worktrees 允许同一个仓库在多个目录同时检出不同分支，是 Git 原生功能，完全安全。每个代理在独立分支上工作，不会互相影响。

### Q2: 多个代理同时修改共享文件怎么办？

**A**: 建议在分配任务时明确划分文件边界，避免多个代理修改同一文件。必要时在合并阶段手动处理冲突。

### Q3: 代理会互相通信吗？

**A**: 目前代理之间不直接通信，通过 git 合并协调结果。社区有讨论增加代理间通信的功能。

### Q4: 一次可以运行多少个代理？

**A**: 受机器资源限制，通常 3-5 个是实用范围。每个 Claude Code 实例大约占用 200-500MB 内存。

---

## 技巧与最佳实践

### 任务分解原则

```
好的任务分解（低依赖）:
✓ 前端组件 vs 后端 API（互相独立）
✓ 功能实现 vs 测试编写
✓ 不同模块的迁移

差的任务分解（高依赖）:
✗ 同一文件的不同部分
✗ 有调用关系的函数
✗ 共享状态的组件
```

### 为每个代理提供清晰上下文

```bash
# 每个代理的指令应该包含：
"任务：[具体任务]
参考：[相关文件路径]
规范：[遵循的代码风格]
输出：[期望的文件结构]
不要：[不应该改动的部分]"
```

### 使用 CLAUDE.md 统一规范

确保每个 worktree 都有相同的 `CLAUDE.md`，让所有代理遵循一致的规范：

```bash
# 创建 worktree 后复制规范文件
cp CLAUDE.md worktrees/feature-a/
cp CLAUDE.md worktrees/test-a/
```

### 合并前的 Review 流程

```bash
# 合并前用 code-review 检查每个代理的输出
> /code-review worktrees/feature-a
> /code-review worktrees/test-a

# 确认无问题后再合并
git merge feature-a
git merge test-a
```

---

## 相关工具

- [code-review 插件](./code-review-plugin.md) - 多代理审查每个分支的输出
- [repomix](./repomix.md) - 合并前生成完整上下文供审查

---

**工具版本**: 最新
**最后更新**: 2026-02-10
