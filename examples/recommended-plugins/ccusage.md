# 工具：ccusage

## 概述

`ccusage` 是一个命令行工具，用于追踪 Claude API 的 Token 用量和成本，支持按天、按会话、按模型分类统计。

**Stars**: 10,200+
**GitHub**: `ryoppippi/ccusage`
**类型**: 独立 CLI 工具
**安装方式**: npm 或 Cargo（Rust）

**解决的核心问题**：
使用 Claude API 时，不清楚自己每天/每月花了多少 Token，成本完全不透明。`ccusage` 读取本地 Claude Code 的使用日志，生成详细的用量报告，帮助控制成本。

**使用场景**:
- 监控每日/每月 API 费用
- 对比不同工作方式的 Token 效率
- 设置成本预警
- 优化 Prompt 减少 Token 消耗

---

## 安装

### npm（推荐）

```bash
npm install -g ccusage
```

### Cargo（Rust，性能更好）

```bash
cargo install ccusage
```

### 验证安装

```bash
ccusage --version
```

---

## 工作原理

```
Claude Code 使用日志
~/.claude/logs/
        │
        ▼
  ccusage 解析器
        │
        ├── Token 统计
        │   ├── 输入 Token
        │   ├── 输出 Token
        │   └── 缓存 Token
        │
        ├── 成本估算
        │   └── 基于各模型定价
        │
        └── 可视化报告
```

ccusage 完全在本地运行，不会上传任何数据到外部服务器。

---

## 核心命令

### 查看今日用量

```bash
ccusage
```

**输出示例**：

```
Today's Claude Usage (2026-02-10)
═══════════════════════════════════════════

Model: claude-opus-4-6
  Input tokens:    45,230  ($0.68)
  Output tokens:   12,890  ($0.39)
  Cache read:      89,450  ($0.22)
  Cache write:      2,100  ($0.01)
  ─────────────────────────────────
  Total:                   $1.30

Model: claude-haiku-3-5
  Input tokens:     8,920  ($0.01)
  Output tokens:    2,340  ($0.01)
  ─────────────────────────────────
  Total:                   $0.02

══════════════════════════════════════════
Today Total:               $1.32
Cache savings:             $0.22 (14%)
```

### 按天统计

```bash
ccusage --daily
```

```
Daily Usage (Last 7 days)
═══════════════════════════════════════════
Date         Tokens (K)  Cost    Sessions
────────────────────────────────────────
2026-02-10     58.4      $1.32     8
2026-02-09     124.7     $3.11     15
2026-02-08     89.2      $2.24     12
2026-02-07     43.1      $1.08     6
2026-02-06     0         $0.00     0
2026-02-05     201.3     $5.02     22
2026-02-04     156.8     $3.92     18
────────────────────────────────────────
Week Total:    673.5     $16.69
Daily Avg:     96.2      $2.38
```

### 按会话统计

```bash
ccusage --session
```

```
Session Usage
═══════════════════════════════════════════
Session ID          Tokens    Cost    Duration
──────────────────────────────────────────────
session-abc123      45,230    $1.30   2h 15m
session-def456      23,100    $0.58   45m
session-ghi789       8,920    $0.22   20m
```

### 按月统计

```bash
ccusage --monthly
```

### 实时监控模式

```bash
ccusage --watch
# 每 30 秒刷新一次
```

---

## 实战应用

### 场景 1：设置每日预算告警

```bash
# 添加到 ~/.bashrc 或 ~/.zshrc
alias claude-check='ccusage && echo "---" && ccusage --budget-alert 5.00'

# 每次开始工作前检查
claude-check
```

自定义脚本：

```bash
#!/bin/bash
# check-budget.sh
DAILY_COST=$(ccusage --json | jq '.today.total_cost')
BUDGET=5.00

if (( $(echo "$DAILY_COST > $BUDGET" | bc -l) )); then
  echo "⚠️  今日 Claude 费用已超 \$$BUDGET（当前：\$$DAILY_COST）"
fi
```

### 场景 2：对比工作流 Token 效率

```bash
# 记录任务开始时的用量快照
BEFORE=$(ccusage --json | jq '.today.total_tokens')

# 执行任务...
# claude "帮我重构这个模块"

# 记录结束时的用量
AFTER=$(ccusage --json | jq '.today.total_tokens')
USED=$((AFTER - BEFORE))

echo "此次任务消耗: $USED tokens"
```

### 场景 3：月度成本报告

```bash
# 生成月度报告
ccusage --monthly --output report.csv

# 或 JSON 格式供程序处理
ccusage --monthly --json > monthly-report.json
```

### 场景 4：分析缓存效率

```bash
ccusage --cache-analysis
```

```
Cache Efficiency Analysis
═══════════════════════════════════════
Total cache reads:    234,500 tokens
Total cache writes:    18,900 tokens
Cache hit rate:        92.6%
Estimated savings:    $5.86 (vs no cache)

Top cached sessions:
  session-abc: 89,450 cache reads (82% hit rate)
  session-def: 56,200 cache reads (95% hit rate)
```

---

## 配置

创建 `~/.ccusage.json` 自定义配置：

```json
{
  "budget": {
    "daily": 10.00,
    "monthly": 200.00,
    "alert_threshold": 0.8
  },
  "display": {
    "currency": "USD",
    "timezone": "Asia/Shanghai"
  },
  "models": {
    "claude-opus-4-6": {
      "input_per_mtok": 15.00,
      "output_per_mtok": 75.00,
      "cache_read_per_mtok": 1.50,
      "cache_write_per_mtok": 18.75
    }
  }
}
```

---

## 常见问题

### Q1: 数据从哪里读取？

**A**: 读取 `~/.claude/logs/` 目录下的本地日志文件，完全离线运行。

### Q2: 支持 Claude Code 以外的 Claude 使用吗？

**A**: 目前主要支持 Claude Code 的日志格式。直接 API 调用需要手动记录。

### Q3: 计费模型是否准确？

**A**: 基于公开定价计算，实际账单以 Anthropic 官方为准。

### Q4: 如何追踪多台机器的用量？

**A**: 目前不支持多机聚合，需要在每台机器上分别运行。

---

## 技巧与最佳实践

### 将 ccusage 集成到开发工作流

```bash
# 在 .git/hooks/post-commit 中添加用量提示
#!/bin/bash
ccusage --brief
# 输出: Today: 45,230 tokens ($1.32)
```

### 使用缓存降低成本

当 ccusage 显示缓存命中率较低时，考虑：

```bash
# 在同一会话中处理相关任务（提高缓存复用率）
# 而不是为每个小任务开新会话
claude
> 任务 1: 分析 auth.ts
> 任务 2: 修改 auth.ts（复用上面的上下文）
> 任务 3: 写 auth.ts 的测试
```

### 比较不同 Prompt 策略的成本

```bash
# 测试精简 Prompt 的效果
ccusage --session | grep "session-xyz"
# 对比冗长 Prompt 和精简 Prompt 的 token 消耗
```

---

## 相关工具

- [claude-mem](./claude-mem.md) - 通过缓存记忆减少重复 Token 消耗
- [repomix](./repomix.md) - 优化代码库上下文的打包方式

---

**工具版本**: 最新
**最后更新**: 2026-02-10
