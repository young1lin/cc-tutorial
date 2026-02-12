# 第一层：理论基础（认知地基）

# 大语言模型基础

要想充分发挥 Claude Code 能力，必须要理解什么是大语言模型，以及它的局限性是什么。上下文，提示词等基础概念非常重要，对于后面所有的所谓的各种各样的概念，本质都是为了解决上下文有限的问题。如果你已经看完了 Andrej Karpathy 的 *Deep Dive into LLMs Like ChatGPT* 视频，可以跳过下面的大语言模型基础介绍，直接去 Claude Code 使用那一节，我的截图的 Token 的图片也是来自他的视频。

现在的 LLM 也就是 Large Language Model 大语言模型的本质，就是输入一串文本/图片/音频，将输入向量化（转成一组数字称之为 Token），预测下一个 Token，一个个输出，输入的 Token 数量 + 输出的 Token 数量不能超过 200k 或者 1M。

查看这个网页，深入了解什么是 Token https://tiktokenizer.vercel.app/?model=gpt-4o

## Context Window 上下文窗口

**Token ≠ 字符，Token ≠ 单词**

直观体验：打开 [TikTokenizer](https://tiktokenizer.vercel.app/?model=gpt-4o)，输入任意文本，看看它被切分成多少个 Token。

上下文窗口是一个固定长度的数组，根据前面输入的内容，一个个 Token 输出，直到数组被填满。比如 Claude Opus 4.6 的上下文窗口是 200K Token。

### 动手练习

| 主题 | 示例文件 |
|------|----------|
| Token 概念演示 | [01-main.http](docs/examples/http/01-main.http) - "字数不等于 Token" 示例 |
| 大模型局限性（数学、幻觉、逻辑） | [02-limitations.http](docs/examples/http/02-limitations.http) - 15 个局限性演示 |
| Function Calling 基础 | [01-main.http](docs/examples/http/01-main.http) - 工具调用完整流程 |
| Prompt Engineering | [05-prompt-engineering.http](docs/examples/http/05-prompt-engineering.http) - Few-Shot、CoT 等 |

### 核心要点

1. **上下文窗口有限**：总共 200K Token，输入 + 输出不能超过
2. **Prompt Engineering**：参考 [promptingguide.ai](https://www.promptingguide.ai/) 学习如何写好提示词
3. **模型选择**：Claude Opus 4.6 > GPT-4o > GLM-4.7 > StepFun step-3.5-flash

后面一切的内容——CLAUDE.md、MCP、Skills、SubAgent、LSP、`/compact`——都是围绕一个核心问题：**在有限的上下文窗口中，尽可能实现功能**。

## 注意力机制 —— LLM 的核心引擎

上下文窗口是"能装多少"，注意力机制决定的是"怎么看这些内容"。Transformer 架构的核心就是注意力机制，理解它才能理解后面为什么不同模型在编码场景差异巨大。

### Self-Attention（自注意力）与 O(n²) 的代价

最原始的注意力机制叫 **Full Self-Attention**：对于输入的每一个 Token，都要计算它和**所有其他 Token** 之间的关联度。

```
输入 Token 序列：[我, 今天, 写了, 一个, 函数, 它, 返回, 空值]

"它" 需要计算和前面每个 Token 的关联度：
  它 ↔ 我      → 0.02（弱关联）
  它 ↔ 今天    → 0.01（弱关联）
  它 ↔ 写了    → 0.05
  它 ↔ 一个    → 0.03
  它 ↔ 函数    → 0.82（强关联！"它"指的就是"函数"）
  它 ↔ 返回    → 0.15
  它 ↔ 空值    → 0.10
```

每个 Token 都要和其他所有 Token 两两计算，所以计算量是 **O(n²)**——Token 数量翻倍，计算量翻四倍。这就是为什么 200K 上下文窗口极其昂贵：200,000 × 200,000 = 400 亿次注意力计算。

### 多头注意力（Multi-Head Attention）

实际的 Transformer 不是只算一组注意力，而是**同时运行多组**，每组叫一个"头"（Head）。比如 Claude 可能有 128 个头并行工作。

**为什么要多个头？** 因为语言中的关联关系不止一种。单独一组注意力很难同时捕捉所有维度的关系，多个头各自分工，最后把结果拼起来。

**每个头学到了什么？** 研究发现（参见 Vaswani et al. 2017 "Attention Is All You Need"、Clark et al. 2019 "What Does BERT Look At?"），不同的头会**自发地**学会关注不同类型的语言关系：

| 头的类型 | 关注什么 | 示例 |
|---------|---------|------|
| **语法结构头** | 主谓宾、修饰关系 | "用户**提交**了表单" → 识别"用户"是主语、"表单"是宾语 |
| **指代消解头** | 代词指向谁 | "函数返回空值，**它**需要修复" → "它" = "函数" |
| **语义关联头** | 意思相近的词 | "bug"和"defect"关联度高 |
| **位置关系头** | 相邻 Token 的局部模式 | 关注前后 2-3 个词的搭配 |
| **长距离依赖头** | 跨越很远的关联 | 函数开头的参数定义 ↔ 函数末尾的 return 语句 |

**重要：这不是人为设计的分工，而是训练过程中自发涌现的。** 没有人告诉模型"第 7 个头负责语法"。模型在海量文本上训练时，不同的头自然演化出了不同的专长。这也意味着不是每个头都有清晰的功能——有些头的行为模式至今研究者也没有完全理解。

### 注意力机制的变体

Full Self-Attention 效果最好，但 O(n²) 太贵了。为了支持更长的上下文，各家模型做出了不同的取舍：

**1. 标准 Full Attention（因果）**
- 每个 Token 只看它前面的所有 Token（不偷看未来）
- 计算量 O(n²)，但效果最精确
- 短上下文（≤32K）的经典方案，代表：早期 GPT 系列

**2. 滑动窗口注意力（Sliding Window Attention, SWA）**
- 每个 Token 只看它前后固定范围内的 Token（比如前后 4096 个）
- 计算量降到 O(n·w)，w 是窗口大小
- 代价：超出窗口范围的信息会"看不到"

```
Full Attention（n=8）：每个 Token 看所有前面的
Token:  [1] [2] [3] [4] [5] [6] [7] [8]
  8看→   1   2   3   4   5   6   7   ✓（全部都看）

滑动窗口（w=3）：每个 Token 只看前面 3 个
Token:  [1] [2] [3] [4] [5] [6] [7] [8]
  8看→   ×   ×   ×   ×   5   6   7   ✓（只看最近 3 个）
```

**3. 滑动窗口 + Full Attention 混合**
- 大部分层用滑动窗口（省计算），每隔几层插一层 Full Attention（补回全局信息）
- 代表：**StepFun step-3.5-flash**（每 3 层 SWA + 1 层 Full Attention）
- 效果：靠 Full Attention 层"中继"全局信息，让滑动窗口也能"间接看到"远处的内容

**4. 线性注意力（Lightning Attention）**
- 将 O(n²) 近似降到 O(n)
- 代价：注意力权重被"模糊化"，精确记忆能力下降
- 代表：**MiniMax M2.1**（7 层线性 + 1 层 Full Attention）

**5. 双向非因果注意力**
- 每个 Token 可以同时看过去和未来
- 代表：**GLM-4.7**

**6. 工程优化技术（不改变注意力模式，但让长上下文可行）**
- **Flash Attention**（Tri Dao, 2022）：通过 IO 感知的分块计算，将显存从 O(n²) 降到 O(n)，但计算量仍是 O(n²)。几乎所有现代模型都在用。
- **Ring Attention**：将长序列切片分布到多张 GPU 上，每张卡只处理一段，卡间环形传递 KV。使百万级上下文在工程上可行。
- **GQA（Grouped Query Attention）/ MQA（Multi-Query Attention）**：多个注意力头共享同一组 Key 和 Value，大幅减少 KV Cache 的显存占用。Llama 2/3、Mistral 等公开采用。

### Claude 的注意力机制：未知

**[Author's analysis]** Anthropic 至今没有发布 Claude 系列（包括 Claude Opus 4.6）的架构论文或技术报告，具体的注意力机制属于未公开信息。

但有一点可以确定：**Claude Opus 4.6 支持 200K~1M Token 上下文，不可能是纯粹的 Full Self-Attention。** 原因很简单——1M token 的完整注意力矩阵是 10^12 个元素，单层单头 FP16 就需要约 2TB 显存，这在工程上不可行。

它几乎一定使用了上述优化技术的某种组合（Flash Attention + Ring Attention + GQA/MQA，以及可能的稀疏/混合注意力模式），但具体方案外界无从得知。GPT-4o 同理——OpenAI 也没有公开其架构细节。

**对我们的实际意义：** 不需要知道 Claude 的具体架构，只需要知道它在编码任务中的**实际表现**——长距离代码依赖的准确率、上下文利用率、在接近窗口上限时的质量衰减程度。这些可以通过实测评估，比架构猜测更有价值。

### 对编码场景的影响

为什么这些差异对 AI 编程很重要？因为写代码需要**精确的长距离记忆**：

- 文件开头 import 了什么 → 文件末尾能不能用
- 第 50 行定义的变量类型 → 第 300 行使用时类型要匹配
- 函数 A 的返回值 → 函数 B 调用时的参数校验

**已公开架构的模型**中，Full Attention 能精确记住这些关系，线性注意力会"模糊"掉，滑动窗口可能直接"看不到"。未公开架构的模型（Claude、GPT 等），则需要通过实际编码测试来评估其长距离记忆能力——从实测结果看，Claude Opus 4.6 在这方面表现优秀，但我们无法将其归因于某种具体的注意力机制。

## 从零实现简易版

想深入理解 LLM 如何工作？看这个项目：[minimal-mcp](https://github.com/young1lin/minimal-mcp)

展示了：
- OpenAI 格式的 HTTP 请求结构
- Function Calling 底层实现
- 为什么需要 MCP 协议

## 原生多模态 vs 非原生多模态

**重要说明**：Claude Code 的某些功能依赖模型的多模态能力。

### 什么是原生多模态？

原生多模态模型（如 Claude Opus 4.6、GPT-4o、Gemini）可以直接处理图片：
- 图片直接输入模型
- 模型原生理解图片内容
- 无需额外的 OCR 或描述转换

### 非原生多模态模型

非原生多模态模型（如 StepFun、DeepSeek、智谱 GLM）处理图片的方式不同：
- 可能通过 OCR 提取文字
- 可能通过描述模型转换
- 图片理解能力可能受限

### 功能兼容性

| 功能 | 原生多模态 | 非原生多模态 |
|------|-----------|-------------|
| Alt+V 粘贴图片 | ✅ 完全支持 | ⚠️ 可能不支持 |
| 截图调试 | ✅ 直接分析 | ❌ 需复制文字 |
| UI 截图分析 | ✅ 可识别 | ❌ 需描述 |

### 替代方案

如果使用非原生多模态模型：
1. **错误信息**: 复制错误文字，不要截图
2. **UI 问题**: 描述问题或提供 HTML 代码
3. **设计稿**: 使用 Figma MCP 获取结构化信息

### 模型选择建议

| 场景 | 推荐模型 |
|------|---------|
| 日常开发 | Claude Opus 4.6 > GPT-5.3 > GLM ≈ StepFun |
| 成本敏感 | StepFun step-3.5-flash、DeepSeek |
| 隐私合规 | 内网部署 StepFun 开源版 |
| 中文任务 | DeepSeek、GLM 表现不错 |

> **编码环境慎用 MiniMax M2.1**：线性注意力为主（7 层 Lightning + 1 层 Full），编码任务中会"模糊"早期信息。详见上方"注意力机制的变体"。

> **StepFun step-3.5-flash 值得关注**：SWA + Full Attention 混合架构，2026 年 2 月发布，稀疏 MoE（总参 96B-196B，激活约 11B），推理速度 350 tokens/秒，通过强推理弥补滑动窗口局限。详见上方"注意力机制的变体"。
