# 第一层：理论基础（认知地基）

要想充分发挥 Claude Code 能力，必须要理解什么是大语言模型，以及它的局限性是什么。上下文、提示词、Function Calling、Agent 模式等基础概念非常重要，后面所有的所谓的各种各样的概念，本质都是为了解决**上下文有限**的问题。如果你已经看完了 Andrej Karpathy 的 *Deep Dive into LLMs Like ChatGPT* 视频，可以跳过下面的大语言模型基础介绍，直接去 Claude Code 使用那一节，我的截图的 Token 的图片也是来自他的视频。

这一层是整个教程最厚的地基。我准备了 **9 个 HTTP 示例文件、90+ 个可执行的 API 请求**，覆盖从 Token 概念到 Agent 模式的完整知识链条。每一节都有对应的动手练习，不是纸上谈兵。

> **学习路径建议**：
> - 零基础 → 从头到尾按顺序走
> - 有 LLM 使用经验 → 跳到「LLM 的局限性」看看你是否真的了解边界
> - 想直接上手 Agent → 跳到「Agent 模式」，但建议回头补 Function Calling


## 全部动手练习一览

| 序号 | 示例文件 | 内容 | 示例数 | 难度 |
|------|----------|------|--------|------|
| 01 | [01-main.http](../examples/http/01-main.http) | 基础功能：Token 演示、对话、流式、Function Calling | 7 | ⭐ |
| 02 | [02-limitations.http](../examples/http/02-limitations.http) | LLM 局限性：数学、幻觉、逻辑、知识截止 | 8 | ⭐⭐ |
| 03 | [03-practical-scenarios.http](../examples/http/03-practical-scenarios.http) | 实战场景：代码审查、摘要、情感分析、翻译、数据提取 | 9 | ⭐⭐ |
| 04 | [04-function-calling-advanced.http](../examples/http/04-function-calling-advanced.http) | 高级工具调用：多工具编排、并行调用、错误处理 | 13 | ⭐⭐⭐ |
| 05 | [05-prompt-engineering.http](../examples/http/05-prompt-engineering.http) | 提示词工程：Few-Shot、CoT、结构化输出、角色扮演 | 20 | ⭐⭐ |
| 06 | [06-parameter-experiments.http](../examples/http/06-parameter-experiments.http) | 参数调优：Temperature、Top-P、Penalties、Stream | 15 | ⭐⭐⭐ |
| 07 | [07-agent-patterns.http](../examples/http/07-agent-patterns.http) | Agent 设计模式：ReAct、Plan-and-Execute、Self-Reflection | 9 | ⭐⭐⭐⭐ |
| 08 | [08-legacy-tool-calling.http](../examples/http/08-legacy-tool-calling.http) | 传统工具调用：Text ReAct、XML、JSON vs 原生 FC | 6 | ⭐⭐⭐ |
| 09 | [09-api-protocol-compatibility.http](../examples/http/09-api-protocol-compatibility.http) | 协议兼容：OpenAI 格式 vs Anthropic 格式 | 5 | ⭐⭐ |
| | **合计** | | **90+** | |


# 一、大语言模型基础

## 1.1 什么是 LLM

现在的 LLM（Large Language Model，大语言模型）的本质，就是输入一串文本/图片/音频，将输入向量化（转成一组数字称之为 Token），预测下一个 Token，一个个输出，输入的 Token 数量 + 输出的 Token 数量不能超过 200K 或者 1M。

```
用户输入: "今天天气"
         ↓ 分词(Tokenize)
Token序列: [今天, 天气]
         ↓ 模型预测
下一个Token: "怎"
         ↓ 继续预测
下一个Token: "么"
         ↓ 继续预测
下一个Token: "样"
         ↓ 继续预测
下一个Token: "？"
         ↓ 结束标记
输出: "怎么样？"
```

关键理解：**LLM 不是数据库，不是搜索引擎，不是计算器**。它是一个**概率语言模型**——根据前面的内容，预测下一个最可能的词。

![LLM](https://s2.loli.net/2025/08/06/46yrGOqJc73EpjK.png)

上面图片截取自 Andrej Karpathy 的 *[Deep Dive into LLMs Like ChatGPT](https://www.youtube.com/watch?v=7xTGNNLPyMI)* 视频。

## 1.2 Token —— LLM 的最小单位

查看这个网页，深入了解什么是 Token：[TikTokenizer](https://tiktokenizer.vercel.app/?model=gpt-4o)

**Token ≠ 字符，Token ≠ 单词**

直观体验：打开 TikTokenizer，输入任意文本，看看它被切分成多少个 Token。

```
英文: "Hello World"     → 2 个 Token
中文: "你好世界"         → 2-4 个 Token（取决于分词器）
代码: "console.log()"   → 3-4 个 Token
混合: "调用 API 接口"    → 3-5 个 Token（取决于分词器）
```

**为什么 Token 很重要？** 因为：
1. **计费按 Token**：不是按字数，而是按 Token 数量计费
2. **上下文按 Token**：200K 的窗口指的是 200K Token，不是 200K 字
3. **中文更"贵"**：一个或者多个中文字通常占 1 个 Token，而一个英文单词通常只占 1 个 Token。例如 “你好” 占用一个 Token，“你好世界” 占用 2 个 Token。

> **动手练习** → [01-main.http](../examples/http/01-main.http)：第一个请求展示了"字数不等于 Token"的概念

## 1.3 Context Window 上下文窗口

大语言模型并没有记住你说的话，你说的内容，都会带上去，和之前的内容一起作为 input tokens，然后进行推理，生成 output tokens 转成你理解的语言。也就是说，LLMs 本质是个猜词器，根本没有真正的智能，只是看起来和人一样通过强思维链的方式，一步步推导出答案。那些说什么 AI 产生了自己的“思维”，走向 AGI 的所谓“砖家”全是扯淡的，他们的目的很简单，钱，训练大模型，不仅硬件烧钱，人也烧钱，顶级的算法工程师高薪聘请。没有钱，寸步难行，他们就必须往外吹吹牛逼拉投资。

你可以简单把上下文窗口是一个固定长度的数组，根据前面输入的内容，一个个 Token 输出，直到数组被填满。理解上下文窗口概念十分重要，后续的所有的包装出来的概念，都和这个有限的上下文窗口概念有关。以及为什么上下文窗口要有这个限制，并且合理构建上下文又被称之为 Context Engineering。

**为什么这很重要？** 因为后面一切的内容——CLAUDE.md、MCP、Skills、SubAgent、LSP、`/compact`——都是围绕一个核心问题：**在有限的上下文窗口中，尽可能实现功能**。

> **核心洞察**：Claude Code 的所有高级功能，本质上都是上下文管理策略。理解了这一点，后面所有概念都会豁然开通。


# 二、LLM 的局限性

不了解局限性，就会对 LLM 有错误预期。以下所有结论均来自 2026-02-15 实测（glm-4-flash，无内置推理）。

> **动手练习** → [02-limitations.http](../examples/http/02-limitations.http)：8 个请求，覆盖 5 大类局限性

### 2.1 数学计算局限

LLM 不是计算器，它靠**概率预测**数字，不是真的在算。

```
问: 982717.1211 × 213213.23321 - 321312.777 / 1112.1121 = ?
正确: 约 2095 亿    模型: 约 20 亿    → 差了 100 倍
```

**解决方案**：Function Calling 调用计算器工具。同一个 glm-4-flash，给了工具就能拿到精确结果。

### 2.2 知识截止（Knowledge Cutoff）

直接问"你知不知道"，模型会承认；但**预设事实再问细节**，模型就会跟着编。

```
问: 2026 年 2 月有哪些科技新闻？  → 承认不知道 ✓
问: Python 3.14 的 compression.zstd 怎么用？ → 编了一套假代码 ✗
```

**解决方案**：MCP / Web Search 获取实时信息。

### 2.3 逻辑推理局限

无推理能力的基础模型在形式逻辑上会犯低级错误（带 CoT 的推理模型已能解决简单逻辑题）。

```
问: A<B<C<D<E，C 和 A 谁更高？
模型: 排成 "D>E>A>B>C"，结论 "C 比 A 矮"  → 完全搞反
```

**解决方案**：使用推理模型，或用 CoT 提示词强制分步推理。

### 2.4 幻觉（Hallucination）

2026 年仍然最顽固的问题：**模型会非常自信地说出完全错误的内容**。

| 类型 | 实测案例 |
|------|---------|
| **事实混淆** | 中文问"林黛玉倒拔垂杨柳"已免疫，换英文问 → 编造"凤姐砍柳树" |
| **编造统计** | 问 SO 2023 调查数据 → 编了 Kite 23%（2022 年已停服） |
| **技术幻觉** | 问新 API 用法 → 用第三方包 API 冒充标准库模块 |

**解决方案**：要求引用来源、代码必须运行验证、结合 LSP 检查。

### 2.5 计数与上下文偏差

LLM 不会真正"数"东西，对列表中间位置的感知尤其差（Lost in the Middle）。

```
30 个城市列表，问第 15 个 → 模型答第 13 个（差 2 位）
```

**对 Claude Code 的影响**：CLAUDE.md 最重要的规则放开头，长对话用 `/compact` 管理上下文。

### 2.6 局限性总结

| 局限性 | 根本原因 | 解决方案 | 对应工具 |
|--------|---------|---------|---------|
| 数学计算 | 概率预测，非精确计算 | Function Calling | 计算器工具 |
| 知识截止 | 训练数据有截止日期 | 实时信息检索 | MCP、Web Search |
| 逻辑推理 | 缺乏形式化推理能力 | 推理模型 / CoT | Extended Thinking |
| 幻觉 | 概率生成，无真实性验证 | 验证 + 引用 | LSP、测试 |
| 计数偏差 | 不会逐个数，靠感觉猜 | 代码执行 | /compact、SubAgent |

> **核心认知**：LLM 是**语言专家**，不是知识库，不是计算器。Function Calling 让同一个模型从"算不对"变成"精确计算"——理解这个定位，才能正确使用 Claude Code。

# 三、实战应用场景

知道了 LLM 能做什么、不能做什么之后，来看看它在实际工作中最擅长的场景。

> **动手练习** → [03-practical-scenarios.http](../examples/http/03-practical-scenarios.http)：9 个实战场景，覆盖 6 大类

### 3.1 代码审查与测试（2 个示例）

LLM 最强的能力之一是代码理解和审查：

```python
# 给 LLM 一段代码，让它找 Bug
def calculate_average(numbers):
    total = 0
    for n in numbers:
        total += n
    return total / len(numbers)  # Bug: 空列表会除零！
```

LLM 能快速发现：
- 除零错误（空列表）
- 键不存在（字典操作）
- 类型不匹配
- 性能问题

> **动手练习** → [03-practical-scenarios.http](../examples/http/03-practical-scenarios.http)：
> - Bug 发现（Python 除零、键错误）
> - 单元测试生成（pytest）

### 3.2 文本处理（4 个示例）

| 场景 | 能力 | 推荐 temperature |
|------|------|------------------|
| 新闻摘要 | 提取 3-5 个关键点 | 0 |
| 会议纪要 | 提取待办事项 + 负责人 | 0 |
| 多维度情感分析 | 质量/服务/价格 JSON 评分 | 0 |
| 术语翻译 | 保留领域术语 | 0 |

### 3.3 数据提取与内容生成（3 个示例）

- **命名实体识别**：从文本中提取人名、地名、组织、日期
- **简历解析**：文本 → 结构化 JSON
- **商务邮件**：根据要点生成专业邮件
- **社交媒体文案**：带表情和 CTA 的营销文案

> **最佳实践建议**：

| 场景 | temperature | max_tokens | 要求 |
|------|------------|------------|------|
| 代码审查 | 0 | 1000 | 结构化输出 |
| 文本摘要 | 0 | 300 | 要点列表 |
| 情感分析 | 0 | - | JSON 输出 |
| 翻译 | 0.3 | 1000 | 保留术语 |
| 数据提取 | 0 | - | JSON Schema |
| 内容生成 | 0.3-0.7 | 500 | 创意自由 |


# 四、Function Calling —— LLM 的"手"

LLM 本身只能输出文本。Function Calling 让 LLM 能够**调用外部工具**——查天气、执行代码、访问数据库——这是从"聊天机器人"到"AI Agent"的关键跨越。

> **核心类比**：LLM 是大脑，Function Calling 是手脚。没有 Function Calling 的 LLM 就是一个只能说话不能动手的人。

## 4.1 基本流程

```
用户: "北京今天天气怎么样？"
  ↓
LLM 判断: 我需要调用 get_weather 工具
  ↓
LLM 输出: { "tool": "get_weather", "args": { "location": "北京" } }
  ↓
程序执行: 调用天气 API，返回 "晴，18°C"
  ↓
LLM 收到结果: "北京今天天气晴朗，气温 18°C，适合外出。"
  ↓
用户看到: 最终的自然语言回答
```

**关键理解**：LLM 不是自己去调用 API，而是**输出一段结构化的"工具调用指令"**，由外部程序执行，再把结果喂回给 LLM。

## 4.2 实际 HTTP 请求解剖 —— 真正看懂 Function Calling

上面的流程图是简化的。下面用**真实的 HTTP 请求体**展示 Function Calling 的完整交互。这是你在 01-main.http 中能直接运行的。

### 第一步：定义工具 + 发送用户请求

```json
// POST https://api.stepfun.com/v1/chat/completions
{
  "messages": [
    {
      "role": "system",
      "content": "你是一个智能客服 Alice。"
    },
    {
      "role": "user",
      "content": "查一下杭州天气"
    }
  ],
  "model": "step-3.5-flash",
  "tools": [                          // ← 告诉模型有哪些工具可用
    {
      "type": "function",
      "function": {
        "name": "get_weather",        // ← 工具名称
        "description": "获取天气信息", // ← 模型靠这个判断何时调用
        "parameters": {               // ← JSON Schema 定义参数
          "type": "object",
          "properties": {
            "location": {
              "type": "string",
              "description": "城市名称，如 hangzhou, beijing"
            }
          },
          "required": ["location"]
        }
      }
    }
  ],
  "stream": false,
  "temperature": 0
}
```

**注意**：`tools` 数组**每次请求都要带上**——模型不会"记住"你之前定义过什么工具。这意味着工具定义也消耗上下文 Token。

### 第二步：模型返回 tool_calls（不是最终回答）

```json
// 模型的响应
{
  "choices": [{
    "message": {
      "role": "assistant",
      "content": "我来帮你查一下杭州的天气。",
      "tool_calls": [                    // ← 模型决定调用工具
        {
          "id": "call_0_c9f112b0-766e-48ee-8b7d-a70c14f16b43",
          "type": "function",
          "function": {
            "name": "get_weather",       // ← 要调用哪个工具
            "arguments": "{\"location\": \"hangzhou\"}"  // ← 参数（JSON 字符串）
          }
        }
      ]
    },
    "finish_reason": "tool_calls"        // ← 注意：不是 "stop"，是 "tool_calls"
  }]
}
```

**关键**：`finish_reason` 是 `"tool_calls"` 而不是 `"stop"`——这告诉你的程序"模型还没说完，需要你先执行工具"。

### 第三步：你的程序执行工具，把结果喂回去

```json
// 你的程序构造的下一次请求
{
  "messages": [
    { "role": "system", "content": "你是一个智能客服 Alice。" },
    { "role": "user", "content": "查一下杭州天气" },
    {
      "role": "assistant",                // ← 把模型上一轮的回复原封不动放回来
      "content": "我来帮你查一下杭州的天气。",
      "tool_calls": [{
        "id": "call_0_c9f112b0-766e-48ee-8b7d-a70c14f16b43",
        "type": "function",
        "function": {
          "name": "get_weather",
          "arguments": "{\"location\": \"hangzhou\"}"
        }
      }]
    },
    {
      "role": "tool",                     // ← 新的消息类型：tool
      "tool_call_id": "call_0_c9f112b0-766e-48ee-8b7d-a70c14f16b43",  // ← 对应哪次调用
      "content": "Sunny, 29°C"            // ← 工具执行的结果（你的程序填的）
    }
  ],
  "model": "step-3.5-flash",
  "tools": [/* 同上，工具定义还要带 */],
  "stream": false,
  "temperature": 0
}
```

### 第四步：模型基于工具结果给出最终回答

```json
{
  "choices": [{
    "message": {
      "role": "assistant",
      "content": "杭州今天天气晴朗，气温 29°C，非常适合外出活动！建议做好防晒。"
    },
    "finish_reason": "stop"              // ← 这次是 "stop"，表示回答完毕
  }]
}
```

### 完整循环图

```
┌─────────────────────────────────────────────────────────────┐
│                   Function Calling 完整循环                   │
│                                                              │
│  Round 1:                                                    │
│    你的程序 ──→ [messages + tools定义] ──→ LLM API           │
│    LLM API  ──→ { tool_calls: [...] } ──→ 你的程序          │
│                                                              │
│  你的程序执行工具（HTTP/数据库/文件操作...）                    │
│                                                              │
│  Round 2:                                                    │
│    你的程序 ──→ [messages + tool结果 + tools定义] ──→ LLM API │
│    LLM API  ──→ { content: "最终回答" } ──→ 你的程序         │
│                                                              │
│  注意：可能不止 2 轮！模型可能连续调用多个工具                   │
└─────────────────────────────────────────────────────────────┘
```

> **核心认知**：Function Calling 不是一次请求完成的——它是一个**多轮对话循环**。每次 `finish_reason === "tool_calls"` 都意味着"还没完，继续"。Claude Code 的 Agent 循环本质上就是这个循环。

> **动手练习** → [01-main.http](../examples/http/01-main.http)：
> - 基础 Function Calling（get_weather 工具定义）
> - 模拟 tool_calls 响应后的第二轮请求
> - 完整的多轮工具调用对话
>
> **Python 实现** → [examples/python/00_basic_function_calling.py](../examples/python/00_basic_function_calling.py)：纯 httpx 手写多轮工具调用循环，不依赖任何 SDK，展示底层完整流程

## 4.3 高级工具调用

> **动手练习** → [04-function-calling-advanced.http](../examples/http/04-function-calling-advanced.http)：13 个高级示例

### 多工具编排

一个请求可能需要调用多个工具。模型需要决定**调用顺序**：

```
用户: "明天杭州天气怎么样？如果天气好，帮我安排户外活动"

Step 1: 调用 get_weather("杭州", "明天")
Step 2: 根据天气结果，决定是否调用 get_attractions(category="outdoor")
Step 3: 如果需要，调用 get_restaurants(area="西湖附近")
```

### 并行工具调用

某些场景下，多个工具调用之间**没有依赖关系**，可以并行执行：

```
用户: "北京、上海、广州今天天气分别怎么样？"

并行调用:
  get_weather("北京") ──┐
  get_weather("上海") ──┼── 同时执行
  get_weather("广州") ──┘
```

### 错误处理

模型需要优雅地处理工具调用失败的情况：

```
用户: "火星今天天气怎么样？"
工具返回: { "error": "invalid_location", "message": "火星不在支持范围内" }
LLM 应回答: "抱歉，天气服务目前只支持地球上的城市。"
```

### 复杂参数

工具可以接受复杂的嵌套参数：

```json
{
  "tool": "query_database",
  "args": {
    "table": "users",
    "filters": { "age": { "gte": 18 }, "status": "active" },
    "sort": { "field": "created_at", "order": "desc" },
    "pagination": { "page": 1, "size": 20 }
  }
}
```

### 工具设计原则

1. **描述清晰**：工具的 description 直接影响模型何时调用它
2. **类型严格**：参数类型、枚举值、required 字段都要写明
3. **单一职责**：每个工具只做一件事
4. **错误信息结构化**：让模型能理解错误并给用户有用的提示

## 4.4 传统工具调用方式（历史演进）

在原生 Function Calling 之前，业界经历了多种"手工"方案。理解这些历史有助于理解当前方案为什么是这样。

> **动手练习** → [08-legacy-tool-calling.http](../examples/http/08-legacy-tool-calling.http)：6 个示例，覆盖 3 种传统格式 + 原生 FC 对比

### 技术演进时间线

| 年份 | 方式 | 代表 | 特点 |
|------|------|------|------|
| 2022 | Text ReAct | LangChain | 纯文本格式，正则提取 |
| 2023 | XML 格式 | Anthropic Claude 2.x | 标签结构化 |
| 2023 | JSON 格式 | OpenAI 早期 | JSON 输出 |
| 2024+ | 原生 Function Calling | OpenAI/Anthropic 标准 | 模型内置支持 |

### Text ReAct 格式（2022）

```
Thought: 我需要查询天气
Action: get_weather
Action Input: {"location": "北京"}
Observation: [程序插入工具结果]
Thought: 我现在知道答案了
Final Answer: 北京今天晴朗，18°C。
```

**问题**：需要用正则表达式解析，模型可能忘记格式、输出不一致。

### XML 格式（2023，Anthropic Claude 2.x 风格）

```xml
<thinking>用户想知道天气</thinking>
<action>
  <tool>get_weather</tool>
  <parameters>
    <location>北京</location>
  </parameters>
</action>
```

### JSON 格式（2023，OpenAI 早期）

```json
{
  "thought": "需要查询天气",
  "action": "get_weather",
  "action_input": {"location": "北京"}
}
```

### 为什么要学传统方式？

1. **理解演进**：知道"为什么"，不只是"是什么"
2. **调试能力**：遇到老系统能看懂
3. **底层原理**：Function Calling 本质就是结构化输出 + 外部执行
4. **灵活扩展**：某些自定义场景可能需要回退到传统方式

## 4.5 API 协议兼容

不同厂商的 Function Calling 协议不同。理解差异才能在多模型之间切换。

> **动手练习** → [09-api-protocol-compatibility.http](../examples/http/09-api-protocol-compatibility.http)：5 个协议对比示例

| 方面 | OpenAI 格式 | Anthropic 格式 |
|------|------------|---------------|
| **System Prompt** | 在 messages 里作为第一条 | 顶层 `system` 参数 |
| **工具定义** | `tools[].function` | `tools[].input_schema` |
| **工具调用** | `tool_calls` 在 response 中 | `tool_use` 在 content 数组中 |
| **工具结果** | user message + `tool_result` | user message + `tool_result` |
| **使用者** | OpenAI, StepFun, DeepSeek | Anthropic Claude, GLM |

**设计建议**：使用适配器模式抽象协议差异：

```typescript
interface UnifiedChatRequest {
  model: string;
  messages: Message[];
  tools?: Tool[];
  temperature?: number;
}

class OpenAIAdapter implements ChatProvider { ... }
class AnthropicAdapter implements ChatProvider { ... }
```

> **与 Claude Code 的关系**：Claude Code 底层使用 Anthropic 协议，但当你配置第三方模型（StepFun、DeepSeek）时，中继层需要做协议转换。理解两种协议有助于调试连接问题。

## 4.6 从 Function Calling 到 MCP —— 为什么需要协议标准化

Function Calling 有个致命问题：每个 AI 平台格式不同，同一个工具要为 OpenAI、Anthropic、Cursor、Cline 各写一遍适配。N 个平台 × M 个工具 = N×M 个适配，这不可持续。

**MCP（Model Context Protocol）** 就是 USB 接口——统一标准，工具只写一次，到处运行。它提供三种能力：Tools（执行操作）、Resources（只读数据，被动推送给模型）、Prompts（提示词模板）。

Claude Code 本身就是一个 MCP Client，内置的 Read/Write/Edit/Bash 等工具都是内置 Tool，外部 MCP Server 就是给它扩展工具箱。

> **深入学习**：MCP 协议架构、JSON-RPC 消息格式、动手实现详解 → [supplement-mcp.md](supplement-mcp.md)
>
> 从零实现看这个：[minimal-mcp](https://github.com/young1lin/minimal-mcp)
>
> Claude Code 中 MCP 的实际配置和使用 → **第六层（高级功能）**


# 五、Prompt Engineering —— 与 LLM 对话的艺术

提示词工程不是玄学，是有方法论的工程实践。写好提示词，输出质量可以提升 10 倍。

> **动手练习** → [05-prompt-engineering.http](../examples/http/05-prompt-engineering.http)：20 个示例，覆盖 6 大技术
>
> **延伸阅读**：[promptingguide.ai](https://www.promptingguide.ai/) —— 最全面的提示词工程参考

## 5.0 标准提示词参考：Claude Code 的内置提示词

学提示词工程，不要只看理论。看真实的、被 Anthropic 工程师打磨过的生产级提示词。

**[claude-code-system-prompts](https://github.com/Piebald-AI/claude-code-system-prompts/tree/main/system-prompts)** — 从 Claude Code 工具本身提取的系统提示词，完整公开，可以直接研究。

这批提示词之所以值得反复学习，是因为它们遵循了一套对大模型极其友好的**标准结构**：

```
1. 一段话描述这个工具/指令是什么、解决什么问题（不是一句话，是一段）
2. ## When to Use This Tool — 编号列出具体使用场景
3. ## When NOT to Use This Tool — 编号列出明确不该用的情况 + NOTE 补充说明
4. ## Examples of When to Use — <example> 块，每个都带 <reasoning>
5. ## Examples of When NOT to Use — <example> 块，每个都带 <reasoning>
6. （可选）## 操作细节 — 状态管理、任务分解规则等
```

这个结构的核心是**消除歧义**。大模型不怕复杂，怕模糊。模糊的描述，模型会脑补；脑补就会出错。但还不止于此——`<example>` + `<reasoning>` 的组合才是真正的精华。

### `<example>` + `<reasoning>` 结构：为什么有效

普通的 Examples 只给模式，但不解释原因。Claude Code 的提示词多了一个 `<reasoning>` 块——**把"为什么在这个场景下该用/不该用"直接写给模型看**：

```xml
<example>
User: I want to add a dark mode toggle...
Assistant: I'll create a todo list to track this implementation...
*Creates todo list with 5 items*

<reasoning>
The assistant used the todo list because:
1. Adding dark mode is a multi-step feature requiring UI, state management, and styling changes
2. The user explicitly requested tests and build be run afterward
3. The assistant inferred that tests and build need to pass
</reasoning>
</example>
```

模型看到这个之后，学到的不只是"什么时候用 todo"，而是学到了**判断逻辑**：任务涉及多个子系统、用户明确提到了后续步骤、需要推断隐含要求——这些才是触发 todo 的真正原因。

反例同理——`<reasoning>` 会解释"这个任务是单步操作，没有要追踪的中间状态，所以不用 todo"。

### 烂提示词 vs 这套结构

```
# 烂版本（你可能在用的）
"用 todo 工具管理复杂任务。"

问题：
- "复杂"是什么？没定义
- 修改一个函数算复杂吗？不知道
- 回答用户问题要开 todo 吗？不知道
- 结果：模型乱用，或者该用的时候不用
```

```
# Claude Code 版本的等价做法：
描述段：一段话说清楚用途和价值
When to Use：5条具体场景，带数字编号
When NOT to Use：4条 + 一个加粗的 NOTE
Examples：4个正例 + 4个反例，每个都有 <reasoning>
```

**你写 CLAUDE.md 的时候，就模仿这套结构**：

```markdown
## 提交代码

在项目中，使用 /commit-push 命令提交代码。提交前确保代码已经通过测试，
且符合 Conventional Commits 格式（feat/fix/refactor/docs/chore）。

**什么时候用**：
1. 完成一个独立功能或修复
2. 用户明确要求提交
3. 一次修改涉及 3 个以上文件

**什么时候不用**：
1. 代码还没写完，只是中间状态
2. 测试还没跑，或者测试在跑中
3. 用户只是说"先看看效果"

**正例**：
- 用户说"这个 bug 修完了，提交一下" → 用 /commit-push
- 完成了一个完整的 API endpoint，包括测试 → 用 /commit-push

**反例**：
- 用户说"把这行注释掉试试" → 不要提交，这是临时调试
- 重构到一半，函数签名改了但调用方还没改 → 不要提交，会 break
```

这不是多此一举，这是让模型**少犯错**的最直接方式。结构化的提示词，比自然语言描述的执行准确率高得多。

## 5.1 Few-Shot Learning（少样本学习）

给模型几个示例，让它学会输出模式。这是最实用的技术。

```
Zero-Shot（零样本）:
  "分析以下评论的情感：这家餐厅太棒了！"
  → 模型可能输出任意格式

3-Shot（三样本）:
  "示例1: '味道不错' → 正面
   示例2: '服务太差' → 负面
   示例3: '一般般' → 中性
   请分析: '这家餐厅太棒了！'"
  → 模型会按照示例格式输出: "正面"
```

**在 Claude Code 中的应用**：这就是 CLAUDE.md 中放示例代码的原因——给模型看你项目的代码风格，它就会按你的风格写新代码。Boris Cherny 称之为"对牛弹琴不如抛砖引玉"（Pearls Before Swine）。

### Benchmark 中的 Few-Shot vs Zero-Shot 争议

**评估方法差异会显著影响 benchmark 结果**。一个经典的例子是 Gemini 1 发布时的争议：

根据 [Google Gemini 1 技术报告](https://storage.googleapis.com/deepmind-media/gemini/gemini_1_report.pdf)（2023-12）第 8 页的 benchmark 表格，Gemini 在多项测试中声称超越了 GPT-4。但社区很快发现了一个关键问题：

| 评估方式 | 说明 | 对结果的影响 |
|---------|------|-------------|
| **CoT@32** | 运行 32 次 Chain-of-Thought，取最好的结果 | 显著提升分数（相当于给 32 次机会） |
| **5-shot** | 给 5 个示例，单次运行 | 标准评估方式，一次机会 |

争议点在于：**Gemini Ultra 使用 CoT@32（32次运行取最好），而对比的 GPT-4 使用 5-shot（单次运行）**。这种"best-of-32 vs single-run"的不对等比较让 benchmark 数值失去了直接可比性。

> **来源**：[Hacker News 讨论](https://news.ycombinator.com/item?id=38545663)、[Reddit 分析](https://www.reddit.com/r/singularity/comments/18dxszz/so_gemini_ultra_beats_gpt4_in_30_of_32_benchmarks/)、本地截图证据 [Gemini Report Table 2](../research/evidence/gemini-1-report-page8-benchmark-table.png)

这个争议给我们的启示是：不要盲目相信 benchmark 排名。根据 [arXiv 论文](https://arxiv.org/html/2506.12286v3)，SWE-bench 存在数据污染问题（94% 的测试用例在模型训练数据中出现过），导致"可疑的高性能"。评估模型时，应该：
1. 确认评估方法是否一致（few-shot 数量、prompt 格式）
2. 关注第三方独立评估（如 [LMSYS Chatbot Arena](https://chat.lmsys.org/) 的盲测）
3. 在自己的实际场景中测试

> **延伸阅读**：[Hacker News 讨论](https://news.ycombinator.com/item?id=38545663)详细分析了 Gemini benchmark 的方法论问题。

> **动手练习** → [05-prompt-engineering.http](../examples/http/05-prompt-engineering.http)：
> - Zero-Shot vs 3-Shot 情感分析对比
> - Few-Shot 代码生成（带类型标注和文档字符串）
> - 4-Shot 实体提取

## 5.2 Chain-of-Thought（链式思维, CoT）

让模型**先推理，再回答**。一句 "Let's think step by step" 就能大幅提升复杂问题的准确率。

```
不用 CoT:
  问: "一个商店有 23 个苹果，卖掉了 17 个，又进货了 12 个，还剩多少？"
  答: "18 个" ← 可能直接跳到错误答案

用 CoT:
  问: "...请一步一步思考"
  答: "
  1. 初始苹果: 23 个
  2. 卖掉 17 个: 23 - 17 = 6 个
  3. 进货 12 个: 6 + 12 = 18 个
  答案: 18 个" ← 推理过程可见，容易验证
```

**Claude Code 中的对应**：Extended Thinking（深度思考）

| 关键词 | 思考 Token 数 | 适用场景 |
|--------|-------------|---------|
| `think` | ~4K | 普通多步骤任务 |
| `think harder` | ~10K | 复杂架构设计 |
| `ultrathink` | ~32K | 极其复杂的多文件重构 |

> **注意**：思考 Token 按**输出 Token 费率**计费，不消耗上下文窗口。上述数值可能随版本更新而变化（详见 [Claude Code Guide](https://www.claude-code-guide.com/)）。

> **动手练习** → [05-prompt-engineering.http](../examples/http/05-prompt-engineering.http)：
> - Zero-Shot CoT（"Let's think step by step"）
> - 有无 CoT 的对比实验
> - Few-Shot CoT（提供推理示例）
> - 逻辑谜题推理
> - 代码调试步骤分析

## 5.3 Structured Output（结构化输出）

强制模型输出特定格式（JSON、表格、代码块），而不是自由文本。

```json
// 用 JSON Schema 约束输出
{
  "type": "object",
  "properties": {
    "sentiment": { "enum": ["positive", "negative", "neutral"] },
    "confidence": { "type": "number", "minimum": 0, "maximum": 1 },
    "keywords": { "type": "array", "items": { "type": "string" } }
  },
  "required": ["sentiment", "confidence"]
}
```

**在 Claude Code 中的应用**：
- Headless 模式的 `--output-format json` 就是结构化输出
- MCP 工具的返回值需要结构化
- Agent 的 Function Calling 本身就是结构化输出

> **动手练习** → [05-prompt-engineering.http](../examples/http/05-prompt-engineering.http)：
> - 基础 JSON 格式要求
> - JSON Schema 约束
> - 复杂嵌套 JSON（电商订单结构）
> - Markdown 表格生成
> - Markdown 文档 + 代码块

## 5.4 Role Playing（角色扮演）

给模型一个**身份和专业背景**，让它以特定角色的方式回答。

```
普通提问: "设计一个高并发系统"
→ 泛泛而谈

角色提问: "你是一位有 15 年经验的系统架构师，曾在阿里巴巴负责双十一架构。
          请设计一个支持百万并发的电商系统。"
→ 专业、有深度、有实战经验的回答
```

**在 Claude Code 中的应用**：CLAUDE.md 中的 persona 设置就是角色扮演——告诉 Claude 它是某个项目的资深开发者。

> **动手练习** → [05-prompt-engineering.http](../examples/http/05-prompt-engineering.http)：
> - 系统架构师角色
> - 普通助手 vs 架构师对比
> - 创意角色（诗人写西湖诗）

## 5.5 Negative Prompting（负面提示）

告诉模型**不要做什么**，有时比告诉它要做什么更有效。

```
"请解释什么是 Docker。
 不要使用专业术语。
 不要超过 3 句话。
 不要给出代码示例。"
```

**在 Claude Code 中的应用**：CLAUDE.md 中经常会有类似规则：
- "不要修改 config/ 目录下的文件"
- "不要在没有测试的情况下提交"
- "不要引入新的依赖"

## 5.6 In-Context Learning（上下文学习）

让模型从对话历史中**学习风格和模式**，而不需要显式的示例。

```
用户: "客服回复要用轻松的语气，带表情符号 😊"
助手: "好的，以后都用这种风格回复哦~ 😊"
用户: "客户说他的订单丢了"
助手: "哎呀，真是太抱歉了 😅 让我帮您查一下订单状态~"
```

> **动手练习** → [05-prompt-engineering.http](../examples/http/05-prompt-engineering.http)：客服风格学习示例


# 六、参数调优 —— 控制 LLM 的"旋钮"

不同参数组合对输出质量影响巨大。这不是理论，是必须动手调的。

> **动手练习** → [06-parameter-experiments.http](../examples/http/06-parameter-experiments.http)：15 个参数实验，覆盖核心参数

## 6.1 Temperature（温度）

控制输出的**随机性/创造性**。温度越高越随机，越低越确定。

```
temperature=0:     每次输出完全相同（确定性）
temperature=0.3:   轻微变化，基本稳定
temperature=0.7:   平衡点（多数场景默认值）
temperature=1.0:   较高创造性
temperature=1.5:   高度随机（质量开始下降）
temperature=2.0:   极端随机（基本不可用）
```

**直觉理解**：温度就是"掷骰子"——温度 0 是一个永远掷出最大面的骰子，温度 2 是一个完全随机的骰子。

| 场景 | 推荐 temperature |
|------|-----------------|
| 代码生成 | 0 |
| 技术文档 | 0 |
| 数据提取 | 0 |
| 日常对话 | 0.7 |
| 创意写作 | 0.8 |
| 头脑风暴 | 1.0-1.2 |

> **动手练习** → [06-parameter-experiments.http](../examples/http/06-parameter-experiments.http)：
> - temperature=0 / 0.7 / 1.5 三级对比实验
> - 同一首诗在不同温度下的变化

## 6.2 Top-P（核采样）

另一种控制随机性的方式：只从概率最高的前 P% 的 Token 中选择。

```
top_p=0.1:   只考虑前 10% 概率的 Token（极保守）
top_p=0.5:   前 50%
top_p=0.9:   前 90%（默认值）
top_p=1.0:   全部 Token（不限制）
```

> **重要**：通常不要同时调 temperature 和 top_p，选一个调就行。

## 6.3 Max Tokens（最大输出长度）

```
max_tokens=50:    极短摘要
max_tokens=200:   中等长度（~100-150 中文字）
max_tokens=1000:  详细解释（~500-700 中文字）
不设置:           模型自然结束
```

## 6.4 Frequency Penalty & Presence Penalty

控制模型是否重复说过的话。

| 参数 | 作用 | 效果 |
|------|------|------|
| frequency_penalty=0 | 允许重复 | 正常 |
| frequency_penalty=0.5 | 适度避免重复 | 更丰富 |
| frequency_penalty=2.0 | 极度避免重复 | 可能不自然 |
| presence_penalty=0 | 集中一个话题 | 深入 |
| presence_penalty=1.0 | 鼓励新话题 | 发散 |
| presence_penalty=2.0 | 强制话题转换 | 可能跑题 |

## 6.5 实用参数组合

| 场景 | temperature | top_p | max_tokens | frequency_penalty |
|------|------------|-------|-----------|-------------------|
| 技术文档 | 0 | 1 | 1000 | 0 |
| 创意写作 | 0.8 | - | - | 0.5 |
| 头脑风暴 | 1.2 | - | - | - |
| 客服回复 | 0.3 | - | 300 | 0 |
| 数据分析 | 0 | 1 | - | 0 |

> **动手练习** → [06-parameter-experiments.http](../examples/http/06-parameter-experiments.http)：
> - 参数组合实验（创意写作、技术文档）
> - 流式 vs 非流式对比
> - 流式 vs 非流式响应


# 七、注意力机制 —— LLM 的核心引擎

上下文窗口是"能装多少"，注意力机制决定"怎么看"。核心一句话：**每个 Token 要和所有其他 Token 两两计算关联度，所以计算量是 O(n²)**——这就是长上下文贵的根本原因，也是为什么不同注意力架构（Full Attention vs 滑动窗口 vs 线性）编码能力差异巨大。

Claude 的具体架构未公开，但从实测表现看长距离代码依赖处理得很好。架构猜测不如实测有价值。

> **深入学习**：Self-Attention 原理、Multi-Head 分工、各变体对比（Full/SWA/线性/Flash Attention/Ring Attention）→ [supplement-attention-mechanism.md](supplement-attention-mechanism.md)


# 八、Agent 模式 —— 从工具调用到自主决策

最应该学的课程 [HuggingFace Agent Course](https://huggingface.co/learn/agents-course/en/unit0/introduction)

Function Calling 让 LLM 能调用一个工具。Agent 模式让 LLM 能**自主决定调用哪些工具、以什么顺序调用、如何根据中间结果调整策略**。这是从"工具使用者"到"自主执行者"的跃迁。

> **动手练习** → [07-agent-patterns.http](../examples/http/07-agent-patterns.http)：9 个 Agent 模式示例

## 8.1 什么是 AI Agent？

根据 Lilian Weng 的经典论文 [LLM Powered Autonomous Agents](https://lilianweng.github.io/posts/2023-06-23-agent/)（Lilian Weng, 2023-06），一个 LLM 驱动的自主 Agent 系统由三大组件构成：

```
┌─────────────────────────────────────────────────────────┐
│                    LLM-Powered Agent                     │
│                                                          │
│  ┌──────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ Planning  │  │   Memory     │  │   Tool Use       │  │
│  │ 规划      │  │   记忆       │  │   工具使用        │  │
│  │           │  │              │  │                   │  │
│  │ • 任务分解│  │ • 短期记忆   │  │ • 外部 API       │  │
│  │ • 自我反思│  │  (上下文)    │  │ • 代码执行       │  │
│  │ • 策略调整│  │ • 长期记忆   │  │ • 信息检索       │  │
│  │           │  │  (向量存储)  │  │ • 专业工具       │  │
│  └──────────┘  └──────────────┘  └──────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### Planning（规划）—— Agent 的"大脑"

Agent 需要能把复杂任务分解成子任务，然后逐步执行。Lilian Weng 总结了三种主要的规划策略：

**1. Chain of Thought (CoT)**

一步步推理（前面 Prompt Engineering 部分已详细介绍）。Wei et al. (2022) 的原始论文表明，简单地在提示词中加入"Let's think step by step"就能显著提升复杂推理任务的准确率。

```
用户: "把这个 Express 应用重构成 NestJS"

CoT 规划:
  Step 1: 分析现有 Express 路由结构
  Step 2: 创建对应的 NestJS Module
  Step 3: 迁移每个路由到 NestJS Controller
  Step 4: 迁移中间件到 NestJS Guard/Interceptor
  Step 5: 迁移数据库连接到 NestJS Provider
  Step 6: 运行测试验证
```

**2. Tree of Thoughts (ToT)**

CoT 是一条线性推理链，ToT 则是**同时探索多条推理路径**，形成一棵搜索树。当一条路径走不通时，可以回溯到分叉点尝试另一条。

```
                    "重构方案"
                   /          \
          "方案A: 渐进迁移"    "方案B: 完全重写"
          /        \              /        \
    "先迁移路由"  "先迁移数据层"  "NestJS"   "Fastify"
        |              |            |          |
    评估可行性      评估可行性    评估可行性  评估可行性
        ↓              ↓            ↓          ↓
      得分:0.8      得分:0.6      得分:0.9    得分:0.7
                                    ↑
                              选择最优路径
```

ToT 使用 BFS（广度优先）或 DFS（深度优先）搜索策略。每个节点都有一个评估函数判断"这条路靠不靠谱"。

> **Claude Code 对应**：当你使用 `ultrathink`（~128K 思考 Token）时，模型内部很可能在做类似 ToT 的多路径探索。

**3. LLM+P（LLM + 外部规划器）**

把规划问题用 PDDL（Planning Domain Definition Language）描述，然后交给经典的 AI 规划器（而不是 LLM）来求解。

```
LLM 的角色: 把自然语言翻译成 PDDL
          ↓
PDDL 规划器: 用搜索算法找到最优步骤序列
          ↓
LLM 的角色: 把 PDDL 结果翻译回自然语言/执行步骤
```

这种方案适合有明确状态转换的任务（如物流调度、游戏关卡规划），但编码场景较少使用。

**4. 自我反思（Reflexion）**

不仅规划，还要**评估自己的规划是否有效**。Shinn & Labash (2023) 提出的 Reflexion 框架让 Agent 能：
1. 执行一个计划
2. 评估执行结果
3. 把失败经验写入"反思记忆"
4. 下次规划时参考这些反思

```
第一次尝试:
  计划: 直接修改数据库 Schema
  执行: 报错——外键约束冲突
  反思: "修改 Schema 前需要先处理外键依赖"

第二次尝试（参考反思记忆）:
  计划: 先删除外键约束 → 修改 Schema → 重建外键
  执行: 成功 ✓
```

> **Claude Code 对应**：当 Claude Code 运行测试失败后自动分析错误并修改代码，这就是 Reflexion 模式的简化版。

### Memory（记忆）—— Agent 的"记忆系统"

Lilian Weng 将 Agent 的记忆系统映射到人类认知科学的三种记忆类型：

| 人类记忆类型 | 特点 | AI Agent 对应 | 实现方式 |
|-------------|------|-------------|---------|
| **感觉记忆** | 极短暂，原始输入 | 输入编码 | Embedding 向量化 |
| **短期记忆** | 有限容量，当前工作 | 上下文窗口 | 有限的 Context Window（200K Token） |
| **长期记忆** | 大容量，持久存储 | 外部存储 | 向量数据库 + 检索 |

**短期记忆 = 上下文窗口**

这是 Agent 最直接的记忆。所有对话历史、工具调用结果、系统提示词都在这里。

```
上下文窗口（200K Token）的分配:
  ├── System Prompt（CLAUDE.md 等）     ~2-5K Token
  ├── 对话历史（之前的 Q&A）            ~10-50K Token
  ├── 工具调用结果（代码文件等）         ~20-100K Token
  ├── 当前用户输入                      ~0.1-2K Token
  └── 剩余空间给输出                    ~50-150K Token
```

**关键限制**：**上下文窗口用完了，Agent 就"失忆"了。** 这就是为什么长对话后 Claude Code 会忘记早期指令。

**长期记忆 = 向量数据库 + 检索（MIPS）**

为了突破上下文窗口的限制，Agent 需要外部长期记忆。核心思路：
1. 把信息转换成 **Embedding 向量**（一组数字）
2. 存入**向量数据库**
3. 需要时通过**近似最近邻搜索（ANN）** 检索

Lilian Weng 论文中详细讨论了五种 ANN（Approximate Nearest Neighbor）算法：

| 算法 | 核心思想 | 特点 |
|------|---------|------|
| **LSH** (Locality-Sensitive Hashing) | 用哈希函数把相似向量映射到同一个桶 | 简单高效，但精度一般 |
| **ANNOY** (Approximate Nearest Neighbors Oh Yeah) | 随机投影树，用超平面切分空间 | Spotify 开发，适合静态数据集 |
| **HNSW** (Hierarchical Navigable Small World) | 分层小世界图，多层级导航 | 查询快，内存占用大 |
| **FAISS** (Facebook AI Similarity Search) | 向量量化 + 倒排索引 | Meta 开发，工业级，支持 GPU |
| **ScaNN** (Scalable Nearest Neighbors) | 各向异性向量量化 | Google 开发，保持内积相似度 |

```
长期记忆的读写流程:

写入（存储）:
  "这个函数的作用是..."
    → Embedding Model → [0.12, -0.45, 0.87, ...] (384维向量)
    → 存入向量数据库

读取（检索）:
  "之前那个函数怎么用来着？"
    → Embedding Model → [0.11, -0.43, 0.85, ...] (查询向量)
    → ANN 搜索 → 返回最相似的 Top-K 条记录
    → 注入到上下文窗口中
```

> **Claude Code 对应**：
> - **CLAUDE.md / MEMORY.md** = 简单的长期记忆（文本文件，每次加载到上下文）
> - **向量知识库**（本教程的 vector-kb-mcp）= 真正的向量检索长期记忆
> - **SubAgent** = 解决短期记忆不够的方案（每个子代理有独立的 200K 上下文）
> - **`/compact`** = 压缩短期记忆，释放空间

**为什么这对编码 Agent 很重要？**

一个真实的项目可能有几万行代码，远超 200K Token 的上下文窗口。Agent 必须有策略地选择"记住什么、忘记什么、什么时候去查"：

```
一个 8 万行 IM 系统的代码量 ≈ 300K-500K Token
Claude 的上下文窗口 = 200K Token

结论: 不可能一次性把所有代码放进上下文
解决方案:
  1. CLAUDE.md 描述项目架构（全局地图）
  2. Glob/Grep 按需搜索（精确定位）
  3. Read 只读取相关文件（选择性加载）
  4. SubAgent 处理独立子任务（并行记忆）
  5. /compact 压缩历史对话（释放空间）
```

### Tool Use（工具使用）—— Agent 的"手脚"

就是 Function Calling + MCP 的 Agent 化应用。Lilian Weng 论文中总结了工具使用的四个关键框架：

**1. MRKL（Modular Reasoning, Knowledge and Language）**

LLM 作为**路由器**，把请求分发给最合适的专家模块：

```
用户请求 → LLM（路由器）
              ├── "这是数学问题" → 计算器模块
              ├── "这是天气查询" → 天气 API 模块
              ├── "这是代码问题" → 代码执行模块
              └── "这是常识问题" → LLM 自己回答
```

> **Claude Code 对应**：Claude Code 根据你的请求自动选择工具——需要看代码用 Read，需要搜索用 Grep，需要执行命令用 Bash。这就是 MRKL 模式。

**2. Toolformer**

不是在 Prompt 中告诉模型"你有这些工具可用"，而是通过**微调**让模型学会"什么时候该调用工具"。

```
训练数据:
  输入: "79 + 892 = "
  标注: "79 + 892 = [CALC(79+892)] 971"

模型学会: 遇到精确计算时，自动插入 [CALC(...)] 标记
```

**3. HuggingGPT**

四阶段框架，用 ChatGPT 做任务规划，调用 Hugging Face 上的专业模型执行：

```
Stage 1 - 任务规划:     ChatGPT 分析"修复这张模糊的猫图"
Stage 2 - 模型选择:     选择 image-deblurring 模型
Stage 3 - 任务执行:     调用模型处理图片
Stage 4 - 结果汇总:     ChatGPT 总结"图片已去模糊，清晰度提升 40%"
```

**4. API-Bank —— 评估工具使用能力的三个层级**

| 层级 | 能力 | 说明 |
|------|------|------|
| Level 1 | API 调用 | 能正确调用单个工具 |
| Level 2 | API 检索 | 能从大量工具中**找到**合适的工具 |
| Level 3 | 多 API 规划 | 能**规划**多个工具的调用顺序和组合 |

> **对 Claude Code 的启示**：大多数时候 Claude Code 在做 Level 3 的工作——面对一个复杂的编码任务，它需要规划"先 Grep 搜索 → 再 Read 相关文件 → 然后 Edit 修改 → 最后 Bash 运行测试"这样一个多工具执行序列。

### 三大组件如何协作

```
用户: "修复登录页面的 Bug"

Planning（规划）:
  Thought: "我需要先找到登录页面代码，然后分析 Bug，最后修复"
  Plan: Grep搜索 → Read代码 → 分析问题 → Edit修复 → Bash测试

Memory（记忆）:
  短期记忆: 当前对话 + CLAUDE.md 中的项目架构
  长期记忆: MEMORY.md 中记录的"上次修过一个类似的表单验证 Bug"

Tool Use（工具使用）:
  Step 1: Grep("login") → 找到 src/pages/login.tsx
  Step 2: Read("src/pages/login.tsx") → 看到验证逻辑
  Step 3: Edit(old="||", new="&&") → 修复逻辑错误
  Step 4: Bash("npm test") → 验证修复

Self-Reflection（自我反思）:
  测试通过 → 结束
  测试失败 → 重新分析，修改方案
```

**这就是 Claude Code 每天在做的事。** 理解了 Planning + Memory + Tool Use 这三个组件，你就能理解 Claude Code 的每一个行为背后的逻辑。

## 8.2 ReAct 模式（Reasoning + Acting）

ReAct 是最经典的 Agent 模式，核心循环是：**思考 → 行动 → 观察 → 思考 → ...**

```
用户: "帮我规划明天的杭州一日游"

Thought 1: 我需要先查明天杭州的天气
Action 1:  get_weather("杭州", "明天")
Observation 1: "晴天，18°C"

Thought 2: 天气不错，适合户外。我查一下户外景点
Action 2:  get_attractions(city="杭州", category="outdoor")
Observation 2: ["西湖", "灵隐寺", "西溪湿地"]

Thought 3: 有了景点，再查附近的餐厅
Action 3:  get_restaurants(area="西湖附近")
Observation 3: ["楼外楼", "知味观", "外婆家"]

Thought 4: 信息齐全了，可以生成行程
Final Answer: "明天杭州天气晴朗，推荐行程：
  上午：西湖骑行
  中午：楼外楼午餐
  下午：灵隐寺
  晚上：西溪湿地夜游"
```

**ReAct 的优势**：灵活。如果中间发现天气变了，可以立即调整方案。

> **动手练习** → [07-agent-patterns.http](../examples/http/07-agent-patterns.http)：
> - ReAct 三轮完整流程（天气 → 景点 → 餐厅）
> - 发现下雨后动态切换为室内景点
>
> **Python 实现** → [examples/python/01_react_agent.py](../examples/python/01_react_agent.py)：完整的 ReAct 循环实现，含 Thought/Action/Observation 打印，可直接运行观察每一步决策过程

## 8.3 Plan-and-Execute 模式

先制定完整计划，再按计划逐步执行。

```
用户: "写一篇关于杭州的旅游博客"

Phase 1 - 规划:
  "我的计划:
   Step 1: 获取天气信息
   Step 2: 获取热门景点
   Step 3: 获取美食推荐
   Step 4: 综合写作"

Phase 2 - 执行:
  Step 1: get_weather("杭州") → 晴，18°C
  Step 2: get_attractions("杭州") → [西湖, 灵隐寺, ...]
  Step 3: get_restaurants("杭州") → [楼外楼, ...]
  Step 4: 综合所有信息，撰写博客
```

### ReAct vs Plan-and-Execute

| 方面 | ReAct | Plan-and-Execute |
|------|-------|-----------------|
| **灵活性** | 高（随时调整） | 低（按计划执行） |
| **效率** | 中（可能走弯路） | 高（预优化路径） |
| **适用场景** | 动态/对话式任务 | 目标明确的任务 |
| **Claude Code 对应** | 普通对话模式 | **Plan Mode（Shift+Tab×2）** |

> **关键联系**：Claude Code 的 Plan Mode 就是 Plan-and-Execute 模式的实现——先 read-only 探索，制定计划，用户确认后再执行。
>
> **Python 实现** → [examples/python/02_plan_execute_agent.py](../examples/python/02_plan_execute_agent.py)：先生成完整执行计划再逐步运行，对比 ReAct 的交替决策，直观展示两种模式的差异

## 8.4 Self-Reflection 模式（自我反思）

Agent 执行后会**验证自己的结果**，发现错误则自动修正。

```
Thought: 用户要算斐波那契第 20 项
Action: execute_code("fib(20)")
Observation: 6765

Thought: 让我验证一下——用另一种方法计算
Action: calculator("verify fib(20)")
Observation: 6765 ✓

Thought: 两种方法结果一致，答案可信
Final Answer: 斐波那契第 20 项是 6765
```

参见 Lilian Weng 论文中提到的具体机制：
- **Reflexion**（[Shinn & Labash, 2023](https://arxiv.org/abs/2303.11366)）：动态记忆 + 自我反思，使用启发式函数检测低效规划和幻觉
- **Chain of Hindsight (CoH)**：呈现过去的输出序列，每个都标注反馈，实现迭代改进

> **Claude Code 对应**：当 Claude Code 写完代码后运行测试失败，它会自动分析错误、修改代码、重新运行——这就是 Self-Reflection 模式。
>
> **Python 实现** → [examples/python/03_self_reflection_agent.py](../examples/python/03_self_reflection_agent.py)：执行后自动验证结果，检测到错误则重新规划修正，演示 Reflexion 机制的最小实现

## 8.5 Agent 的核心挑战

Lilian Weng 在论文中总结了三个关键限制，至今仍然适用：

**1. 有限的上下文长度**
> "向量存储和检索可以提供对更大知识池的访问，但其表示能力不如完整注意力那么强大。"

这就是为什么 Claude Code 需要 SubAgent（每个子代理有独立的上下文窗口）。

**2. 长期规划困难**
> "LLM 在面对意外错误时难以调整计划，使其与从试错中学习的人类相比，鲁棒性较差。"

这就是为什么 Boris Cherny 强调**反馈循环**——总是给 Claude 提供验证方法（测试结果、截图、实际输出）。

**3. 自然语言接口的可靠性**
> "当前 Agent 系统依赖自然语言作为接口...模型输出的可靠性存疑，LLM 可能会出现格式错误。"

这就是为什么原生 Function Calling 比传统 Text ReAct 更可靠——结构化输出减少了格式错误。

## 8.6 Hugging Face Agents 课程 —— 动手实践

理论看够了，想动手构建 Agent？推荐 [Hugging Face AI Agents 课程](https://huggingface.co/learn/agents-course/en/unit0/introduction)（Burtenshaw et al., 2025，免费课程）。

### 课程大纲

| 单元 | 主题 | 内容 |
|------|------|------|
| Unit 0 | 入门 | 环境设置、工具和平台 |
| Unit 1 | Agent 基础 | Tools、Thoughts、Actions、Observations 及其格式；LLM、消息、特殊 Token 和聊天模板 |
| Unit 2 | 框架实战 | smolagents、LangGraph、LlamaIndex 三大框架对比实现 |
| Unit 3 | 真实用例 | 社区贡献的实际应用场景 |
| Unit 4 | 期末作业 | 在基准测试上构建并评估你的 Agent |
| Bonus 1 | 微调 | 微调 LLM 实现 Function Calling |
| Bonus 2 | 可观测性 | Agent 的监控和评估 |
| Bonus 3 | 游戏 Agent | 构建宝可梦对战 Agent |

### smolagents —— 代码优先的 Agent 框架

HF 课程重点使用的 [smolagents](https://huggingface.co/docs/smolagents/en/index) 框架，核心理念是 **CodeAgent**——Agent 通过生成代码来执行动作，而不是生成 JSON 工具调用：

```python
from smolagents import CodeAgent, DuckDuckGoSearchTool, InferenceClientModel, tool
import datetime
import pytz

@tool
def get_current_time_in_timezone(timezone: str) -> str:
    """获取指定时区的当前时间
    Args:
        timezone: 有效的时区字符串（如 'Asia/Shanghai'）
    """
    tz = pytz.timezone(timezone)
    local_time = datetime.datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
    return f"{timezone} 当前时间: {local_time}"

model = InferenceClientModel(model_id='Qwen/Qwen2.5-Coder-32B-Instruct')
agent = CodeAgent(
    model=model,
    tools=[get_current_time_in_timezone, DuckDuckGoSearchTool()],
    max_steps=6,
)
```

**CodeAgent vs Function Calling Agent 的区别**：

| 方面 | CodeAgent（smolagents） | Function Calling Agent |
|------|------------------------|----------------------|
| 动作表达 | 生成 Python 代码 | 生成 JSON 工具调用 |
| 灵活性 | 高（可以写循环、条件判断） | 低（只能调用预定义工具） |
| 安全性 | 需要沙箱（受限 Python 解释器） | 较安全（结构化调用） |
| 适用场景 | 复杂数据处理、多步计算 | 标准化工具编排 |

### 与 DeepLearning.AI 联合课程

Andrew Ng 与 Hugging Face 合作推出了 [Building Code Agents with Hugging Face smolagents](https://learn.deeplearning.ai/courses/building-code-agents-with-hugging-face-smolagents/)（Thomas Wolf & Aymeric Roucher 授课），深入讲解：
- Code Agent vs Function-Calling Agent 的取舍
- 安全执行（受限 Python 解释器、E2B 沙箱）
- Agent 的追踪、调试和评估
- 多 Agent 研究系统的构建

## 8.7 Claude Code 就是一个 Agent

把前面的理论拉回来——**Claude Code 本身就是一个完整的 Agent 系统**：

| Agent 组件 | Claude Code 实现 |
|-----------|-----------------|
| **LLM 核心** | Claude Opus 4.6 |
| **Planning** | Plan Mode（Shift+Tab×2）、Extended Thinking |
| **短期记忆** | 200K 上下文窗口 |
| **长期记忆** | CLAUDE.md、MEMORY.md、向量知识库 |
| **工具使用** | Bash、Read、Write、Edit、Glob、Grep、WebFetch... |
| **自我反思** | 运行测试 → 分析失败 → 修改代码 → 重试 |
| **子代理** | SubAgent（独立上下文窗口的子任务执行器） |
| **工具扩展** | MCP（Model Context Protocol） |

**ReAct 循环在 Claude Code 中的体现**：

```
用户: "修复登录页面的 Bug"

Thought: 我需要先看登录页面的代码
Action: Read("src/pages/login.tsx")
Observation: [文件内容]

Thought: 看到了问题——表单验证逻辑有误
Action: Edit("src/pages/login.tsx", old="...", new="...")
Observation: [编辑成功]

Thought: 修改完了，跑一下测试验证
Action: Bash("npm test -- --grep login")
Observation: [测试通过]

Final Answer: "Bug 已修复：登录表单验证逻辑从 OR 改为 AND..."
```

这不是类比——这就是 Claude Code 实际在做的事。理解了 Agent 理论，你就能**预测 Claude Code 的行为**，知道什么时候该给它更多上下文，什么时候该让它自己探索。

## 8.8 Multi-Agent：每个 SubAgent 有自己的 Prompt、Tools 和上下文

Claude Code 不只是一个 Agent——它是一个**多 Agent 系统的 Orchestrator（编排者）**。当任务复杂到一个上下文窗口装不下时，它可以用 `Task` 工具启动 SubAgent，把工作拆给多个独立的子代理并行完成。

```
Claude Code（主 Agent）
  ├── 启动 SubAgent A：搜索代码库（专注搜索任务）
  ├── 启动 SubAgent B：分析测试报告（专注分析任务）
  └── 启动 SubAgent C：生成文档（专注写作任务）
       ↓ 全部完成后
  主 Agent 汇总结果
```

**SubAgent 的三个独立性，这是关键：**

| 独立性 | 含义 | 为什么重要 |
|--------|------|-----------|
| **独立 System Prompt** | 每个 SubAgent 收到的提示词只描述它自己的任务 | 专注。不带主 Agent 的历史干扰，判断更准确 |
| **独立 Tools** | 每个 SubAgent 只配备完成其任务所需的工具 | 不会误用。搜索 Agent 不给写文件权限，防止乱改代码 |
| **独立 Context Window** | 每个 SubAgent 有自己的 200K 上下文，互不共享 | 解决上下文溢出。主 Agent 快满了，开子代理相当于开了新的内存空间 |

**最直接的例子——Code Review Agent**：

```
Code Review Agent
  ├── System Prompt: "你是一个代码审查专家，只负责发现问题，不修改代码"
  ├── Tools:   Glob ✅  Grep ✅  Read ✅
  │            Edit ❌  Write ❌  Bash ❌
  └── Context: 只有当前 PR 的文件列表 + 审查标准

为什么不给 Edit/Write？
  → 审查就是审查，不是修复。给了写权限，模型会"顺手"改代码，
    改出 bug 你还不知道。职责单一，出了问题好排查。
```

**具体到 Claude Code 的实现**——`Task` 工具启动子代理时：

```
主 Agent 调用：Task(
  subagent_type="Explore",   // 指定专门的代理类型（只读）
  prompt="审查 src/auth/ 目录下的所有文件，找出 SQL 注入风险",
  // 子代理只有 Glob/Grep/Read 工具，没有 Edit/Bash
)
```

子代理运行时：
- 它的上下文窗口里**只有**这一个任务描述，看不到主 Agent 的对话历史
- 它的工具集**只包含**搜索相关的工具（Glob、Grep、Read）
- 它完成后返回结果，**销毁自己的上下文**

这就是为什么 Boris Cherny 建议"尽可能让 Claude Code 自己探索"——因为探索任务往往会交给 SubAgent，不会污染主 Agent 的上下文。

**HTTP 示例对应** → [07-agent-patterns.http](../examples/http/07-agent-patterns.http)：

```
# 07 示例演示了 Agent 模式的基础：
# Thought/Action/Observation 循环
# 这是 Multi-Agent 的底层机制
#
# 真正的 Multi-Agent 编排在 Claude Code 层面发生，
# 不是通过 HTTP API 直接演示的——
# 因为 Orchestrator 本身就是 Claude Code
```

> **[Tutorial perspective]** Multi-Agent 是解决上下文限制的最直接方案。理解"每个 SubAgent 是一张白纸"这个概念，你就能理解为什么大任务要拆成小任务分给子代理——不是为了并行提速，首先是为了**干净的上下文**。


# 九、原生多模态 vs 非原生多模态

**重要说明**：Claude Code 的某些功能依赖模型的多模态能力。

## 9.1 什么是原生多模态？

原生多模态模型（如 Claude Opus 4.6、GPT-4o、Gemini）可以直接处理图片：
- 图片直接输入模型
- 模型原生理解图片内容
- 无需额外的 OCR 或描述转换

## 9.2 非原生多模态模型

非原生多模态模型（如 StepFun、DeepSeek、智谱 GLM）处理图片的方式不同：
- 可能通过 OCR 提取文字
- 可能通过描述模型转换
- 图片理解能力可能受限

## 9.3 功能兼容性

| 功能 | 原生多模态 | 非原生多模态 |
|------|-----------|-------------|
| Alt+V 粘贴图片 | ✅ 完全支持 | ⚠️ 可能不支持 |
| 截图调试 | ✅ 直接分析 | ❌ 需复制文字 |
| UI 截图分析 | ✅ 可识别 | ❌ 需描述 |

## 9.4 替代方案

如果使用非原生多模态模型：
1. **错误信息**: 复制错误文字，不要截图
2. **UI 问题**: 描述问题或提供 HTML 代码
3. **设计稿**: 使用 Figma MCP 获取结构化信息


# 十、模型选择建议

## 10.1 综合推荐

| 场景 | 推荐模型 |
|------|---------|
| 日常开发 | Claude Opus 4.6 > GPT-5.3 > GLM ≈ StepFun |
| 成本敏感 | StepFun step-3.5-flash、DeepSeek |
| 隐私合规 | 内网部署 StepFun 开源版 |
| 中文任务 | DeepSeek、GLM 表现不错 |

> MiniMax M2.1 在编码场景表现垃圾

> StepFun step-3.5-flash 值得关注：2026 年 2 月发布，稀疏 MoE（总参 196B，激活约 11B），推理速度可达 350 tokens/秒，上下文窗口 256K。注意力机制采用 **3:1 混合设计**——3 层滑动窗口注意力（SWA）+ 1 层全注意力，兼顾效率与长距离依赖。在多个 coding benchmark 上表现优于 GLM-4.7 和 DeepSeek v3.2。（来源：[StepFun 官方博客](https://static.stepfun.com/blog/step-3.5-flash/)、[arXiv 论文](https://www.arxiv.org/pdf/2602.10604)）

## 10.2 模型选择 = 注意力机制 + 实际表现

不要只看参数量或基准跑分。编码场景的关键指标是：
1. **长距离依赖准确率**：import 到使用之间的距离
2. **上下文利用率**：200K 窗口真正能"用"多少
3. **格式遵循能力**：能否稳定输出 JSON、遵循 CLAUDE.md 规则
4. **工具调用可靠性**：Function Calling 的成功率


# 十一、从零实现简易版

想深入理解 LLM 和 Agent 如何工作？看这些项目和资源：

### 代码实现

**[minimal-mcp](https://github.com/young1lin/minimal-mcp)** —— 本教程配套项目，展示了：
- OpenAI 格式的 HTTP 请求结构
- Function Calling 底层实现
- 为什么需要 MCP 协议

### HTTP 示例全集

本教程的 9 个 HTTP 文件（128+ 示例）是最好的实践材料：

**入门路径**（零基础）：
```
01-main.http → 02-limitations.http → 03-practical-scenarios.http
```

**进阶路径**（有 API 经验）：
```
04-function-calling-advanced.http → 05-prompt-engineering.http → 06-parameter-experiments.http
```

**高级路径**（想理解 Agent）：
```
07-agent-patterns.http → 08-legacy-tool-calling.http → 09-api-protocol-compatibility.http
```


# 十二、延伸阅读与参考资料

这里学习的都是 LLM，那种一句话生成图片视频的，主要用的是扩散模型，在 Huggingface 上也有扩散模型的相关课程。

## 核心论文与文章

| 资源 | 作者 | 年份 | 核心内容 | 重要程度 |
|------|------|------|---------|---------|
| [Attention Is All You Need](https://arxiv.org/abs/1706.03762) | Vaswani et al. | 2017 | Transformer 架构原始论文 | ⭐⭐⭐⭐⭐ |
| [LLM Powered Autonomous Agents](https://lilianweng.github.io/posts/2023-06-23-agent/) | Lilian Weng | 2023-06 | Agent 系统综述（Planning + Memory + Tool Use） | ⭐⭐⭐⭐⭐ |
| [ReAct: Synergizing Reasoning and Acting](https://arxiv.org/abs/2210.03629) | Yao et al. | 2022 | ReAct 模式原始论文 | ⭐⭐⭐⭐ |
| [Chain-of-Thought Prompting](https://arxiv.org/abs/2201.11903) | Wei et al. | 2022 | CoT 提示词原始论文 | ⭐⭐⭐⭐ |
| [Reflexion](https://arxiv.org/abs/2303.11366) | Shinn & Labash | 2023 | Agent 自我反思机制 | ⭐⭐⭐ |
| [Tree of Thoughts](https://arxiv.org/abs/2305.10601) | Yao et al. | 2023 | 多路径推理 | ⭐⭐⭐ |
| [What Does BERT Look At?](https://arxiv.org/abs/1906.04341) | Clark et al. | 2019 | 注意力头功能分析 | ⭐⭐⭐ |
| [Flash Attention](https://arxiv.org/abs/2205.14135) | Tri Dao | 2022 | IO 感知注意力优化 | ⭐⭐⭐ |

## 免费课程

| 课程 | 平台 | 内容 | 链接 |
|------|------|------|------|
| Deep Dive into LLMs Like ChatGPT | YouTube | LLM 基础全面讲解 | Andrej Karpathy 视频 |
| AI Agents Course | Hugging Face | Agent 从入门到实战（smolagents + LangGraph + LlamaIndex） | [huggingface.co/learn/agents-course](https://huggingface.co/learn/agents-course/en/unit0/introduction) |
| Building Code Agents | DeepLearning.AI | Code Agent 构建（Hugging Face smolagents） | [learn.deeplearning.ai](https://learn.deeplearning.ai/courses/building-code-agents-with-hugging-face-smolagents/) |
| Claude Code 入门 | DeepLearning.AI | Claude Code 实战（Elie Schoppik 授课） | 见 research/03 |
| Prompt Engineering Guide | promptingguide.ai | 提示词工程大全 | [promptingguide.ai](https://www.promptingguide.ai/) |

## 本教程相关材料

| 文件 | 内容 |
|------|------|
| [research/00-research-summary.md](../research/00-research-summary.md) | 全部研究材料汇总 |
| [research/01-claude-code-best-practices-anthropic-official.md](../research/01-claude-code-best-practices-anthropic-official.md) | Boris Cherny 最佳实践（T1） |
| [research/03-andrew-ng-course-outline.md](../research/03-andrew-ng-course-outline.md) | Andrew Ng 课程大纲 |
| [research/04-addy-osmani-2026-workflow.md](../research/04-addy-osmani-2026-workflow.md) | Addy Osmani 2026 工作流 |
| [examples/http/](../examples/http/) | 128+ 可执行 HTTP 示例 |
| [examples/python/](../examples/python/) | 4 个 Agent 模式 Python 实现（Function Calling / ReAct / Plan-and-Execute / Self-Reflection） |


# 本层小结

```
第一层 理论基础（认知地基）—— 你现在在这里

  LLM 基础 ───→ 理解 Token、上下文窗口、概率预测
       │
  LLM 局限性 ──→ 数学、幻觉、逻辑、知识截止、注意力偏差
       │
  实战场景 ───→ 代码审查、文本处理、数据提取
       │
  Function Calling ──→ LLM 的"手"，从聊天到工具调用
       │
  Prompt Engineering ──→ Few-Shot、CoT、结构化输出、角色扮演
       │
  参数调优 ───→ Temperature、Top-P、Penalties
       │
  注意力机制 ──→ Full/SWA/Linear/Mixed，理解模型差异
       │
  Agent 模式 ──→ ReAct、Plan-and-Execute、Self-Reflection
       │                ↑ Lilian Weng 论文
       │                ↑ HF Agents 课程
       │
  多模态 + 模型选择 ──→ 选对工具

  ══════════════════════════════════════
  下一层 → 第二层：环境搭建（安装与配置）
```

理解了这些理论基础，你就知道了 Claude Code 的每个功能**为什么存在**——不是凭空冒出来的产品特性，而是在解决 LLM 固有的限制。这是后面六层内容的认知地基。****
