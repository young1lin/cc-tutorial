# 第八层：实战案例

> **本层展示完整的 Claude Code 实战流程** —— 从需求分析到代码实现，演示如何用 Claude Code 修改真实项目。


# 案例 1：修改 claude-token-monitor 布局

## 项目背景

`claude-token-monitor` 是一个 Claude Code statusline 插件，用于在状态栏显示 Token 消耗、模型信息等。本次需求是更新布局，改进时间显示和工具调用状态展示。

**项目路径**：`C:\PythonProject\minimal-mcp\go\claude-token-monitor`

## 现有架构分析

### 三层架构

```
┌─────────────────────────────────────────────────────────────┐
│ Layer 1: Content Collection                                 │
│  - Collectors: 从 stdin 和 transcript 收集数据              │
│  - Composers: 组合多个 collector 的输出                      │
├─────────────────────────────────────────────────────────────┤
│ Layer 2: Layout                                             │
│  - Grid: 4x4 网格布局                                        │
│  - Filter: 根据配置过滤显示内容                              │
├─────────────────────────────────────────────────────────────┤
│ Layer 3: Render                                             │
│  - TableRenderer: 渲染成多行文本输出                         │
└─────────────────────────────────────────────────────────────┘
```

### 当前布局（4x4 Grid）

```
Row 0: folder      | token (model+bar+info) | claude-version
Row 1: git         | memory-files           | skills
Row 2: tools       | agent                  | todo / session-duration
Row 3: time-quota  | (空)                   | (空)
```

### stdin 输入示例（通过 --debug 获取）

```json
{
  "session_id": "c18e5eae-c469-4ccc-b590-3e7ba33b73ba",
  "transcript_path": "C:\\Users\\...\\session.jsonl",
  "cwd": "C:\\PythonProject\\minimal-mcp\\go",
  "model": {
    "id": "claude-opus-4-5-20251101",
    "display_name": "Opus 4.5"
  },
  "workspace": {
    "current_dir": "C:\\PythonProject\\minimal-mcp\\go",
    "project_dir": "C:\\PythonProject\\minimal-mcp\\go"
  },
  "version": "2.1.31",
  "context_window": {
    "total_input_tokens": 326,
    "total_output_tokens": 299,
    "context_window_size": 200000
  }
}
```

### 关键文件

| 文件 | 职责 |
|------|------|
| `cmd/statusline/main.go` | 入口，读取 stdin，协调各层 |
| `internal/statusline/config/config.go` | YAML 配置解析 |
| `internal/statusline/layout/grid.go` | 布局定义（4x4 grid） |
| `internal/statusline/content/time.go` | 时间收集器（当前格式：`YYYY-MM-dd HH:mm`） |
| `internal/statusline/content/session.go` | 工具统计（当前只显示 `🔧 N tools`） |
| `internal/parser/transcript.go` | 解析 transcript.jsonl 获取工具调用信息 |

## 需求描述

### 1. 布局调整

**当前布局**（4x4 Grid，时间在第四行）：
```
Row 0: folder      | token (model+bar+info) | claude-version
Row 1: git         | memory-files           | skills
Row 2: tools       | agent                  | todo / session-duration
Row 3: time-quota  | (空)                   | (空)
```

**目标布局**：
- 时间从第四行移到第三行
- 第四行改为工具状态展示，**不参与前三行的对齐**
- TODO 格式可能也需要调整

### 2. 时间格式

支持两种格式，通过配置切换：
- `YYYY-MM-dd HH:mm` — 完整日期时间
- `HH:mm` — 仅时间

### 3. 工具状态展示

**当前**：只显示 `🔧 2 tools` 这样的汇总

**目标**：显示每个工具的执行次数和结果
```
✓ Read(3) ✓ Grep(2) ✓ Bash(1) ✖ Edit(1)
```

需要从 transcript 中解析每个工具调用的成功/失败状态。

### 4. 并行化处理

使用 goroutine 将所有 collector 并行化执行，提升响应速度。

### 5. 架构考虑

后续版本可能用 Rust 重写，目标是：
- 跨平台（Windows、macOS、Linux）
- 二进制文件体积小
- 原生并发支持


## 关键步骤：用 --debug 获取实际数据

**这是最重要的一步**。在开始实现之前，必须用 `--debug` 获取实际的 stdin JSON 数据，让 Claude 自己分析数据结构，判断怎么做。

### 获取 debug 数据

1. 在 Claude Code 设置中，临时添加 `--debug` 参数：
   ```json
   "command": "C:\\path\\to\\statusline.exe --debug"
   ```

2. 正常使用 Claude Code 一段时间，让它执行一些工具调用

3. 查看 debug 文件（在 statusline.exe 同目录下）：
   ```
   C:\PythonProject\minimal-mcp\go\claude-token-monitor\statusline.debug
   ```

### 提供给 Claude 分析

将 debug 输出贴给 Claude：

```
这是 --debug 输出的 stdin JSON 数据：

[贴入 statusline.debug 内容]

请分析这个 JSON 结构，告诉我：
1. 时间应该从哪个字段获取？
2. 工具调用信息在 transcript_path 指向的文件里，结构是什么样的？
3. TODO 信息有什么变化？
4. 根据实际数据结构，给出实现方案
```


## 实战流程

### Step 1：获取 --debug 数据

```bash
# 在项目中运行一段时间后，查看 debug 文件
cat statusline.debug
```

### Step 2：进入项目，让 Claude 理解结构

```bash
cd C:\PythonProject\minimal-mcp\go\claude-token-monitor
claude
```

```
请阅读这个项目的代码结构，理解 stdin 解析逻辑和状态栏渲染机制
```

### Step 3：提供 debug 数据，让 Claude 分析

```
这是 --debug 输出的实际数据：

[贴入 statusline.debug 内容]

请根据这个实际数据结构，分析如何实现以下需求：
1. 时间从第四行移到第三行
2. 第四行显示每个工具的执行次数和结果（✓/✖）
3. 时间格式支持 YYYY-MM-dd HH:mm 和 HH:mm
4. TODO 格式是否需要调整？

给出具体的实现方案，包括需要修改哪些文件
```

### Step 4：进入 Plan Mode 制定详细方案

按 `Shift+Tab` 两次进入 Plan Mode：

```
根据刚才的分析，制定详细的实现步骤，按优先级排序
```

### Step 5：审核并执行

- 审核方案的合理性
- 切回 Normal 模式执行
- 每完成一步提交一次

### Step 6：验证

```
运行测试：go test ./...
```

```
手动测试：go build -o statusline.exe ./cmd/statusline
然后在 Claude Code 设置中使用这个新编译的版本
```


## 预期输出示例

```
📁 claude-token-monitor | [Opus 4.5] ████░░░░ 75K/200K | v2.1.31
🌿 main +2 ~1           | 3 memories              | skills: 2
🕐 14:30                | 🤖 Explore: searching   | 📋 ✓2/4 | ⏱️ 5m
✓ Read(3) ✓ Grep(2) ✓ Bash(1) ✖ Edit(1)
```

## 踩坑记录

> **提示**：欢迎提交实际踩坑案例。

## 总结

本案例的核心是：**不要猜测数据结构，用 --debug 获取实际数据，让 Claude 自己分析**。

演示了：
- 如何用 --debug 获取 stdin 的实际 JSON 结构
- 如何让 Claude 根据实际数据制定实现方案
- 小步提交、逐步验证的工作流
- Feedback Loop 的实际应用


## 从零开发项目的关键建议

**[教程观点]** 如果是从零开始开发一个新项目，**强烈建议找参考项目让 LLM 学习**。

### 为什么需要参考项目？

**LLM 的本质局限性：猜词游戏**

LLM 的工作原理本质上是"猜下一个词"——它根据上下文预测最可能的输出。当没有参考项目时：

```
你的需求 → LLM 凭空想象 → 可能的输出（概率最高）
                    ↓
              但这不是你想要的！
```

这就是为什么没有参考项目时，LLM 经常：
- 生成"看起来对但实际不对"的代码
- 选择不合适的库或架构
- 忽略边界情况和最佳实践
- 需要多轮修改才能接近目标

**有参考项目时，情况完全不同**：

```
你的需求 + 参考项目 → LLM 学习已有模式 → 类似风格的输出
                              ↓
                    这正是你想要的！
```

具体好处：

1. **避免踩坑**：参考项目通常已经解决了常见的架构问题和边界情况
2. **找到更优雅的解决方案**：成熟的参考项目往往有更好的设计模式
3. **加速开发**：LLM 可以快速理解"你想要什么样的效果"
4. **减少来回修改**：有明确的目标，方向更清晰

### 如何提供参考项目？

```
我想开发一个类似 [参考项目名] 的功能，这是参考项目的代码：

[贴入或指向参考项目的关键文件]

请学习这个项目的架构和设计模式，然后帮我实现 [你的需求]
```

### 实际例子

比如你想做一个状态栏插件，可以提供：
- `claude-token-monitor` 的代码作为参考
- 告诉 LLM "我要做一个类似的，但显示不同的信息"

这样 LLM 就能：
- 学习现有的架构模式
- 理解数据流和渲染逻辑
- 复用成熟的设计决策
- 在此基础上做定制化修改

> **核心原则**：不要让 LLM 凭空想象，给它一个明确的"榜样"来学习。
