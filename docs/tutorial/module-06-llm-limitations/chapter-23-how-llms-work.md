# Chapter 23: LLM 真实工作原理

## 学习目标

完成本章后，你将能够：

- 理解 LLM 的本质是什么
- 了解 Transformer 架构的基础知识
- 理解"预测下一个 Token"的工作机制
- 认识 LLM 的能力边界
- 更好地使用 Claude Code

## 前置知识

- [Chapter 1-4: 基础知识](../module-01-fundamentals/)
- 基本的编程概念
- 对 AI 的基本了解

---

## 23.1 LLM 的本质

### 23.1.1 LLM 是什么

```
┌─────────────────────────────────────────────────────────────┐
│                    LLM 的本质                                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  LLM = Large Language Model = 大型语言模型                  │
│                                                             │
│  核心本质：一个极其复杂的"预测下一个词"的函数                │
│                                                             │
│  Input:  "The quick brown fox jumps over the"               │
│  Output: "dog" (概率最高的下一个词)                          │
│                                                             │
│  它不是：                                                   │
│  ❌ 一个搜索引擎                                            │
│  ❌ 一个数据库                                              │
│  ❌ 一个有意识的智能体                                       │
│  ❌ 一个真正"理解"语言的系统                                 │
│                                                             │
│  它是：                                                     │
│  ✅ 一个基于统计学的模式匹配器                               │
│  ✅ 一个压缩了大量文本知识的函数                             │
│  ✅ 一个在 Token 空间中游走的随机过程                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 23.1.2 简化类比：自动补全

```typescript
/**
 * LLM 本质上是一个超级强大的自动补全系统
 */

/**
 * 示例 1: 简单的 N-gram 模型
 * 这是最简单的语言模型，LLM 的"祖先"
 */

class SimpleLanguageModel {
  private ngrams: Map<string, string[]> = new Map();

  train(text: string): void {
    const words = text.toLowerCase().split(/\s+/);

    for (let i = 0; i < words.length - 2; i++) {
      const context = `${words[i]} ${words[i + 1]}`;
      const next = words[i + 2];

      if (!this.ngrams.has(context)) {
        this.ngrams.set(context, []);
      }
      this.ngrams.get(context)!.push(next);
    }
  }

  predict(context: string): string[] {
    return this.ngrams.get(context.toLowerCase()) || [];
  }
}

// 使用示例
const model = new SimpleLanguageModel();
model.train("The quick brown fox jumps over the lazy dog");

console.log(model.predict("the quick"));
// 可能输出: ["brown"]

console.log(model.predict("quick brown"));
// 可能输出: ["fox"]

/**
 * 示例 2: LLM 是什么？
 *
 * LLM = 这个简单模型的数百万倍复杂版本
 *
 * 区别：
 * - 简单模型：看前 2 个词 → 预测下一个
 * - LLM：看前数千个 Token → 预测下一个
 * - 简单模型：手动统计词频
 * - LLM：数十亿参数的神经网络
 * - 简单模型：精确匹配
 * - LLM：语义理解（通过向量空间）
 */
```

---

## 23.2 Transformer 架构基础

### 23.2.1 注意力机制

```
┌─────────────────────────────────────────────────────────────┐
│                  Attention 机制                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  核心思想：每个词都应该"关注"上下文中的其他词               │
│                                                             │
│  示例句子："The animal didn't cross the street because      │
│             it was too tired"                               │
│                                                             │
│  "it" 应该关注什么？                                        │
│  ├─ "animal" (关系强度: 0.8)  ← 主语                       │
│  ├─ "street" (关系强度: 0.1)                               │
│  └─ "tired"  (关系强度: 0.9)  ← 原因                       │
│                                                             │
│  Self-Attention 让模型学会：                                │
│  - 代词指代什么                                             │
│  - 词语之间的语义关系                                       │
│  - 上下文的重要性                                           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 23.2.2 Transformer 简化架构

```typescript
/**
 * Transformer 简化架构（概念性）
 */

/**
 * Step 1: Tokenization (分词)
 * 将文本转换为数字序列
 */
function tokenize(text: string): number[] {
  const vocab = {
    "the": 1,
    "quick": 2,
    "brown": 3,
    "fox": 4,
    "jumps": 5,
    "over": 6,
    "lazy": 7,
    "dog": 8,
    ".": 9
  };

  return text.toLowerCase()
    .split(/\s+/)
    .map(word => vocab[word] || 0);
}

console.log(tokenize("The quick brown fox"));
// 输出: [1, 2, 3, 4]

/**
 * Step 2: Embedding (嵌入)
 * 将 Token ID 转换为向量（语义表示）
 */
interface EmbeddingVector {
  dimensions: number[];
}

function embed(tokenId: number): EmbeddingVector {
  // 简化：实际是数千维的向量
  // 每个维度代表一个语义特征
  return {
    dimensions: [
      /* 动物性 */ 0.8,
      /* 快速性 */ 0.6,
      /* 颜色 */ 0.3,
      /* 大小 */ 0.2,
      // ... 数千个维度
    ]
  };
}

/**
 * Step 3: Self-Attention (自注意力)
 * 让每个 Token 关注其他所有 Token
 */
interface AttentionWeight {
  tokenIndex: number;
  weight: number; // 0-1 之间
}

function selfAttention(
  tokens: number[],
  position: number
): AttentionWeight[] {
  // 简化：实际通过 Query, Key, Value 计算得出
  const weights: AttentionWeight[] = [];

  for (let i = 0; i < tokens.length; i++) {
    // 计算当前 position 的词与第 i 个词的关系强度
    let relevance = 0;

    // 相近的词相关性更高
    const distance = Math.abs(position - i);
    relevance += 1 / (1 + distance);

    // 语法关系（主谓宾等）
    // ... (实际通过神经网络学习)

    weights.push({
      tokenIndex: i,
      weight: relevance
    });
  }

  // 归一化
  const sum = weights.reduce((s, w) => s + w.weight, 0);
  return weights.map(w => ({
    tokenIndex: w.tokenIndex,
    weight: w.weight / sum
  }));
}

/**
 * Step 4: Feed-Forward Network (前馈网络)
 * 处理聚合后的信息
 */
function feedForward(attentionResult: number[]): number {
  // 简化：实际是多层神经网络
  // 这里只是一个概念性表示
  return attentionResult.reduce((sum, val) => sum + val, 0);
}

/**
 * Step 5: Output Probability (输出概率分布)
 * 预测下一个 Token
 */
function predictNextToken(context: number[]): Map<number, number> {
  // 简化：实际通过 Softmax 函数得到概率分布
  const probabilities = new Map<number, number>();

  // 假设词汇表有 10 个 Token
  for (let i = 1; i <= 10; i++) {
    // 每个Token被预测为下一个的概率
    probabilities.set(i, Math.random());
  }

  // 归一化
  const sum = Array.from(probabilities.values()).reduce((s, v) => s + v, 0);
  for (const [token, prob] of probabilities) {
    probabilities.set(token, prob / sum);
  }

  return probabilities;
}

/**
 * Step 6: Sampling (采样)
 * 根据概率选择下一个 Token
 */
function sampleNextToken(probabilities: Map<number, number>): number {
  const random = Math.random();
  let cumulative = 0;

  for (const [token, prob] of probabilities) {
    cumulative += prob;
    if (random <= cumulative) {
      return token;
    }
  }

  // 默认返回最高概率的
  return Array.from(probabilities.entries())
    .sort((a, b) => b[1] - a[1])[0][0];
}

/**
 * 完整的生成过程（简化版）
 */
function generateText(
  prompt: string,
  maxTokens: number = 10
): string {
  // 1. Tokenize
  let tokens = tokenize(prompt);

  // 2. 逐个生成 Token
  for (let i = 0; i < maxTokens; i++) {
    // 3. 计算注意力
    // 4. 前馈网络
    // 5. 预测概率
    const probabilities = predictNextToken(tokens);

    // 6. 采样
    const nextToken = sampleNextToken(probabilities);

    // 7. 添加到序列
    tokens.push(nextToken);

    // 如果生成了结束符，停止
    if (nextToken === 0) break; // 假设 0 是 EOS
  }

  // 8. 解码回文本
  return decode(tokens);
}

function decode(tokens: number[]): string {
  const vocab = {
    1: "the",
    2: "quick",
    3: "brown",
    4: "fox",
    5: "jumps",
    6: "over",
    7: "lazy",
    8: "dog",
    9: "."
  };

  return tokens
    .map(id => vocab[id] || "<UNK>")
    .join(" ");
}

/**
 * 重要理解：
 *
 * 1. LLM 不是一次性"思考"整个答案
 *    - 它是逐个 Token 生成的
 *    - 每次只预测"下一个最可能的词"
 *
 * 2. LLM 没有内部状态或记忆
 *    - 所有上下文都在输入中
 *    - 这就是为什么有"上下文窗口"限制
 *
 * 3. LLM 不是确定性输出
 *    - 使用采样（温度参数）
 *    - 同样的输入可能产生不同的输出
 *
 * 4. LLM 的"智能"来自：
 *    - 训练数据的规模和质量
 *    - 模型参数的数量
 *    - 架构的设计（Transformer）
 */
```

---

## 23.3 预测下一个 Token 的机制

### 23.3.1 概率分布

```
示例：预测 "The capital of France is" 的下一个词

                    ┌──────────────────┐
                    │   Paris    0.72  │ ← 概率最高
                    ├──────────────────┤
                    │   London   0.12  │
                    ├──────────────────┤
                    │   Berlin   0.08  │
                    ├──────────────────┤
                    │   Rome     0.05  │
                    ├──────────────────┤
                    │   ...      0.03  │
                    └──────────────────┘

采样策略：
- Greedy (贪婪): 直接选 Paris (概率 0.72)
- Top-k: 从前 k 个中随机选
- Top-p (nucleus): 从累积概率达 p 的词中随机选
- Temperature: 控制随机性（越低越确定性）
```

### 23.3.2 温度参数的影响

```typescript
/**
 * Temperature 参数控制输出的随机性
 */

/**
 * Softmax 函数（带温度）
 */
function softmax(logits: number[], temperature: number): number[] {
  // 应用温度
  const scaledLogits = logits.map(l => l / temperature);

  // 计算指数
  const expLogits = scaledLogits.map(l => Math.exp(l));

  // 归一化
  const sum = expLogits.reduce((s, e) => s + e, 0);

  return expLogits.map(e => e / sum);
}

/**
 * 示例：温度对概率分布的影响
 */
const logits = [2.5, 1.0, 0.5, 0.0]; // 原始 logits

// 低温度 (0.1) → 更确定性
const lowTemp = softmax(logits, 0.1);
// [0.98, 0.015, 0.004, 0.001] ← 几乎总是选第一个

// 中等温度 (1.0) → 标准分布
const midTemp = softmax(logits, 1.0);
// [0.72, 0.18, 0.07, 0.03] ← 有一定随机性

// 高温度 (2.0) → 更随机
const highTemp = softmax(logits, 2.0);
// [0.45, 0.30, 0.15, 0.10] ← 随机性很高

/**
 * 实际应用：
 *
 * - Code Generation: 低温度 (0.1-0.3)
 *   → 需要确定性输出
 *
 * - Creative Writing: 高温度 (0.8-1.2)
 *   → 需要创造性和多样性
 *
 * - Chat Assistant: 中等温度 (0.5-0.7)
 *   → 平衡确定性和自然性
 */
```

---

## 23.4 LLM 的能力边界

### 23.4.1 LLM 能做什么

```
┌─────────────────────────────────────────────────────────────┐
│                  LLM 的能力范围                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ✅ 擅长的任务：                                             │
│                                                             │
│  1. 模式匹配与识别                                           │
│     - 代码补全                                              │
│     - 语法修正                                              │
│     - 格式转换                                              │
│                                                             │
│  2. 知识检索（训练数据中）                                    │
│     - API 文档查询                                          │
│     - 历史事实                                              │
│     - 编程概念                                              │
│                                                             │
│  3. 文本生成与转换                                           │
│     - 代码重构                                              │
│     - 文档编写                                              │
│     - 翻译                                                  │
│                                                             │
│  4. 逻辑推理（简单）                                         │
│     - 数学分步计算                                          │
│     - 简单算法实现                                          │
│                                                             │
│  ❌ 不擅长的任务：                                           │
│                                                             │
│  1. 长期推理                                                 │
│     - 多步骤逻辑链                                          │
│     - 复杂系统设计                                          │
│                                                             │
│  2. 实时信息                                                 │
│     - 当前新闻                                              │
│     - 最新 API 变化                                         │
│                                                             │
│  3. 真正的理解                                               │
│     - 它不知道自己在说什么                                  │
│     - 只是统计模式                                          │
│                                                             │
│  4. 确定性保证                                               │
│     - 可能产生幻觉                                          │
│     - 可能犯错                                              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 23.4.2 知识截止日期

```typescript
/**
 * LLM 的知识限制
 */

/**
 * 限制 1: 知识截止日期
 *
 * LLM 只知道训练截止日期之前的信息
 */
const TRAINING_CUTOFF_DATE = {
  "GPT-4": "2023-09",
  "Claude 3 Opus": "2024-01",
  "Claude 4 Opus": "2026-01" // 假设
};

// 示例：询问 LLM 关于新特性
// ❌ 错误：期望 LLM 知道最新的 API
user: "如何使用 React 19 的新特性？"
llm: "我可能不知道 React 19 的新特性..."
     // 如果训练数据中没有，它会说不知道或产生幻觉

// ✅ 正确：提供上下文
user: `这是 React 19 的一些新特性：
     [提供文档片段]

     如何使用这些特性重构这段代码？
     [代码]`
llm: "基于您提供的信息，我可以帮您重构..."

/**
 * 限制 2: 无法访问外部信息
 */
// ❌ 错误：期望 LLM 查询实时数据
user: "当前比特币价格是多少？"
llm: "我无法访问实时数据..." // 或给出过时信息

// ✅ 正确：提供数据或使用工具
user: "比特币价格是 $50,000。这比昨天高还是低？"
llm: "这取决于昨天的价格..."

// 或使用 MCP 工具
user: "使用 get_crypto_price 工具查询比特币价格"
llm: [调用工具] "当前价格是 $50,000"

/**
 * 限制 3: 无法记住之前的对话
 */
// 每个 API 调用都是独立的
// 需要在每次请求中包含完整上下文
const messages = [
  { role: "user", content: "我叫 Alice" },
  { role: "assistant", content: "你好 Alice！" },
  { role: "user", content: "我叫什么名字？" }
  // 如果不包含前面的消息，LLM 不知道名字
];
```

---

## 23.5 为什么 LLM 会犯错

### 23.5.1 概率性本质

```
LLM 的输出本质上是概率性的，不是确定性的。

示例：计算 "2 + 2"

人类：2 + 2 = 4（确定性）
LLM：
  - 99.99% 的概率输出 "4"
  - 0.01% 的概率输出其他（幻觉）

这就是为什么：
- LLM 可能算错简单的数学
- LLM 可能产生不存在的代码
- LLM 可能编造事实
```

### 23.5.2 幻觉现象

```typescript
/**
 * LLM 幻觉 (Hallucination)
 *
 * 幻觉 = LLM 自信地输出错误信息
 */

/**
 * 原因 1: 训练数据中的噪声
 */
// 如果训练数据中有错误信息
// LLM 也会学到这些错误

/**
 * 原因 2: 模式匹配过度
 */
// LLM 可能"模仿"真实文档的格式
// 但内容是编造的

user: "如何使用 TypeScript 的 @readonly 装饰器？"
llm: "可以这样使用：
     @readonly
     class MyClass { }

     配置 tsconfig.json：
     {
       'experimentalDecorators': true,
       'readonlyDecorators': true  // ← 这个选项不存在！
     }"
// LLM 看起来很自信，但信息是错误的

/**
 * 原因 3: 概率采样
 */
// 在高温下，LLM 可能选择不太可能的词
// 这可能导致奇怪的输出

/**
 * 如何减少幻觉：
 */
const REDUCE_HALLUCINATION_TIPS = [
  "提供具体的上下文",
  "要求 LLM 引用来源",
  "使用较低的 Temperature",
  "验证 LLM 的输出",
  "提供参考资料",
  "分步验证",
  "使用工具（如 MCP）获取真实信息"
];
```

---

## 23.6 理解 LLM 对使用 Claude Code 的帮助

### 23.6.1 合理的期望

```typescript
/**
 * 理解 LLM → 合理使用 Claude Code
 */

/**
 * 1. 把 Claude Code 当作助手，而不是替代
 */

// ✅ 好的使用方式
const goodWorkflow = {
  step1: "自己设计解决方案",
  step2: "用 Claude Code 生成样板代码",
  step3: "审查 Claude Code 的输出",
  step4: "测试和验证",
  step5: "自己负责最终质量"
};

// ❌ 不好的使用方式
const badWorkflow = {
  step1: "让 Claude Code 做所有事",
  step2: "信任 Claude Code 的所有输出",
  step3: "不理解代码就提交"
};

/**
 * 2. 提供足够的上下文
 */

// ❌ 上下文不足
user: "修复这个 bug"
// Claude Code 不知道：项目背景、错误信息、期望行为

// ✅ 上下文充分
user: `
  # 项目背景
  这是一个 React 组件，用于管理用户列表。

  # 问题描述
  当用户删除列表中的最后一项时，页面崩溃。

  # 错误信息
  Error: Cannot read property 'map' of undefined

  # 期望行为
  删除最后一项后，应该显示"暂无数据"

  # 相关代码
  [粘贴代码]

  请帮我修复这个 bug。
`

/**
 * 3. 使用 Plan Mode
 */

// ✅ 使用 Plan Mode 让 Claude 先思考
// Shift+Tab (两次)

// Claude 会：
// 1. 分析问题
// 2. 提出方案
// 3. 列出步骤
// 4. 等待你确认

// 而不是直接开始写可能错误的代码

/**
 * 4. 验证 Claude Code 的输出
 */

// ✅ 总是验证
const checklist = [
  "代码能否运行？",
  "是否符合项目规范？",
  "有没有安全问题？",
  "有没有性能问题？",
  "是否需要调整？"
];
```

### 23.6.2 CLAUDE.md 的重要性

```markdown
# CLAUDE.md

## 为什么重要？

LLM 有上下文窗口限制和知识截止。
CLAUDE.md 提供了项目特定的"长期记忆"。

## 应该包含什么？

1. 项目概述
2. 架构决策
3. 编码规范
4. 常用命令
5. 已知问题

这相当于给 Claude Code 提供了"项目手册"，
让它能够更好地理解你的项目。
```

---

## 23.7 练习

### 练习 1：理解概率输出

给定以下概率分布，解释在不同 Temperature 下的行为：

```
Token:   " Paris"  " London"  " Berlin"  " Rome"
Logit:      3.0       1.5       0.5      -1.0
```

### 练习 2：识别幻觉

以下哪些可能是 LLM 的幻觉？

A. "Python 的 sort() 方法时间复杂度是 O(n log n)"
B. "TypeScript 3.0 引入了可选链操作符"
C. "Vue 4 将在下周发布"
D. "JavaScript 有一个内置的 debounce 函数"

### 练习 3：改进 Prompt

改进以下 Prompt，减少产生错误的可能性：

```
"写一个函数计算斐波那契数列"
```

---

## 23.8 进一步阅读

- [Attention Is All You Need (原始论文)](https://arxiv.org/abs/1706.03762)
- [The Illustrated Transformer](http://jalammar.github.io/illustrated-transformer/)
- [Chapter 24: AI 失败案例](chapter-24-ai-failures.md) - 下一章

---

## 视频脚本

### Episode 23: LLM 真实工作原理 (16 分钟)

#### [0:00-1:00] 引入
**视觉元素**：
- 标题："LLM 本质：超级强大的自动补全"
- 代码对比：简单 N-gram vs LLM

**内容**：
> LLM 是什么？很多人认为它是"人工智能"，甚至"有意识"。但事实上，LLM 本质上只是一个极其复杂的"预测下一个词"的函数。
>
> 理解这一点，你就能更好地使用 Claude Code。

#### [1:00-3:00] 自动补全类比
**视觉元素**：
- 简单 N-gram 模型演示
- 代码示例

**内容**：
> 让我们从一个简单的语言模型开始。这个模型只知道两个词的上下文：
>
> [演示 SimpleLanguageModel]
>
> "the quick" → 可能是 "brown"
> "quick brown" → 可能是 "fox"
>
> LLM 就是这个简单模型的数百万倍复杂版本！它看数千个 Token 的上下文，使用数十亿参数的神经网络，但核心逻辑是一样的：**预测下一个词**。

#### [3:00-7:00] Transformer 简化版
**视觉元素**：
- Transformer 架构动画
- 注意力机制可视化

**内容**：
> LLM 使用 Transformer 架构。核心是 Self-Attention 机制。
>
> [演示注意力机制]
>
> 在句子 "The animal didn't cross the street because it was too tired" 中，"it" 应该关注什么？
> - "animal" (主语) - 相关性 0.8
> - "tired" (原因) - 相关性 0.9
>
> Self-Attention 让模型学会代词指代、语法关系、上下文重要性。

#### [7:00-10:00] 概率分布与采样
**视觉元素**：
- 概率分布图
- Temperature 参数对比

**内容**：
> LLM 不直接"选择"下一个词，而是输出一个概率分布。
>
> [演示概率分布]
>
> "The capital of France is"：
> - Paris: 72%
> - London: 12%
> - Berlin: 8%
>
> Temperature 参数控制随机性：
> - 低温度 (0.1) → 几乎总是选 Paris
> - 高温度 (1.0) → 有一定随机性
>
> 这就是为什么代码生成用低温度（需要确定性），创意写作用高温度（需要多样性）。

#### [10:00-13:00] LLM 的限制
**视觉元素**：
- 能力边界列表
- 知识截止日期说明

**内容**：
> 理解 LLM 的限制很重要：
>
> **1. 知识截止日期**
> - LLM 只知道训练数据截止日期之前的信息
> - 无法知道最新的 API、新闻、事件
>
> **2. 概率性本质**
> - 不是确定性输出
> - 可能产生"幻觉"（自信地输出错误信息）
>
> **3. 无真正理解**
> - 不知道自己在说什么
> - 只是统计模式匹配

#### [13:00-16:00] 实践建议
**视觉元素**：
- 好的使用方式 vs 不好的使用方式
- CLAUDE.md 重要性

**内容**：
> 理解 LLM 的本质，让我们更好地使用 Claude Code：
>
> ✅ **好的方式**：
> - 把 Claude 当作助手，不是替代
> - 提供充分的上下文
> - 使用 Plan Mode
> - 验证输出
>
> ❌ **不好的方式**：
> - 让 Claude 做所有事
> - 不加审查地信任输出
> - 不理解代码就提交
>
> 记住：Claude Code 是一个强大的工具，但你仍然是工程师，你是负责人。
>
> 下一章，我们将看一个具体的 AI 失败案例，了解这些限制的后果。
