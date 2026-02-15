# HTTP 示例集合

这个目录包含了全面的大语言模型 API 使用示例，重点使用 **StepFun** 模型，涵盖基础用法、高级特性和实战场景。

## 📁 文件列表

### 1. `01-main.http` - 基础功能
**涵盖内容**：
- ✅ API 配置和认证
- ✅ 单次对话和多轮对话
- ✅ 流式响应 (SSE)
- ✅ 语言控制（强制返回指定语言）
- ✅ 基础 Function Calling
- ✅ Temperature 参数实验

**适用对象**：初学者，快速上手 API 基本用法

---

### 2. `02-limitations.http` - 大模型局限性 ⚠️
**涵盖内容**：
- ❌ 数学计算错误（大数乘法、复杂算术）
- ❌ 知识截止日期（无法获取最新信息）
- ❌ 逻辑推理局限（否定运算、传递性关系、悖论）
- ❌ 幻觉问题（事实混淆、虚假引用、技术幻觉）
- ❌ 上下文长度限制（首尾效应）
- ✅ 解决方案：Function Calling + 外部工具

**学习目标**：
- 理解 LLM 的工作原理（概率预测 vs 符号推理）
- 认识到 LLM 的边界和不适用场景
- 掌握如何通过工具调用弥补局限性

**关键启示**：
> LLM 是"理解和生成语言的专家"，而非"知识库"或"计算器"。应该将 LLM 作为"协调者"（Agent），调用专业工具完成具体任务。

---

### 3. `03-practical-scenarios.http` - 实用场景 💼
**涵盖内容**：
- 💻 **代码审查与重构**
  - Bug 发现、性能优化
  - 代码重构、可读性提升
  - 代码解释、单元测试生成

- 📄 **文本摘要**
  - 新闻摘要、技术文档摘要
  - 会议记录、行动项提取

- 😊 **情感分析**
  - 简单分类（正面/负面/中性）
  - 多维度评分（质量/服务/价格）
  - 批量分析、趋势统计

- 🌐 **文本翻译**
  - 基础翻译、专业术语翻译
  - 文化适配、风格保留

- 📊 **数据提取与结构化**
  - 实体提取（NER）
  - 表格数据生成
  - 简历解析、信息抽取

- ✍️ **内容生成**
  - 商务邮件、社交媒体文案
  - FAQ 生成、产品描述

**学习目标**：
- 理解 LLM 在实际业务中的应用
- 掌握不同场景的最佳实践
- 学会集成 LLM 到工作流

---

### 4. `04-function-calling-advanced.http` - Function Calling 高级用法 🔧
**涵盖内容**：
- 🔗 多工具组合调用（天气 + 日程管理）
- ⚡ 并行工具调用（同时查询多个城市）
- 🛠️ 错误处理和恢复
- 🎯 条件工具调用（基于上下文智能选择）
- 📦 复杂参数设计（嵌套对象、数组）
- 🌊 流式响应中的 Function Calling
- 💻 实战场景：代码执行器

**学习目标**：
- 设计高质量的工具接口（JSON Schema）
- 处理多工具协同和错误恢复
- 理解工具调用的最佳实践

**设计原则**：
- 工具描述要清晰准确
- 参数类型和约束要明确（使用 `enum`、`required`）
- 工具应该是原子性的，一个工具只做一件事
- 返回的错误信息要结构化

---

### 5. `05-prompt-engineering.http` - 提示词工程 📝
**涵盖内容**：
- 📚 **Few-Shot Learning**（少样本学习）
  - Zero-Shot vs Few-Shot 对比
  - 情感分析、代码生成、实体提取

- 🧠 **Chain-of-Thought**（思维链）
  - Zero-Shot CoT："Let's think step by step"
  - Few-Shot CoT：提供推理示例
  - 数学应用题、逻辑推理、代码调试

- 📋 **结构化输出**
  - JSON 输出（带 Schema）
  - Markdown 文档和表格生成

- 🎭 **角色扮演**
  - 专家角色设定
  - 创意角色（诗人、作家）

- 🚫 **Negative Prompting**
  - 避免特定行为
  - 控制输出风格和长度

- 🔄 **In-Context Learning**
  - 从对话历史中学习
  - 保持风格一致性

**学习目标**：
- 掌握提示词优化技术
- 理解不同提示词模式的适用场景
- 学会设计高效的提示词

---

### 6. `06-parameter-experiments.http` - 参数实验 🔬
**涵盖内容**：
- 🌡️ **Temperature**（创造性控制）
  - 0（完全确定）→ 2.0（极高随机）
  - 不同场景的最佳配置

- 🎯 **Top-P**（核采样）
  - 0.1（保守）→ 1.0（无限制）
  - Temperature vs Top-P 对比

- 📏 **Max Tokens**（长度控制）
  - 短回答 vs 详细阐述
  - 成本优化

- 🔁 **Frequency Penalty**（重复惩罚）
  - 避免词汇重复
  - 提升内容多样性

- 🌈 **Presence Penalty**（话题发散）
  - 鼓励引入新话题
  - 内容丰富度控制

- 🆚 **模型对比**
  - StepFun vs DeepSeek
  - 代码生成、创意写作、多语言

**学习目标**：
- 理解各参数对输出的影响
- 掌握不同场景的参数配置
- 学会平衡质量、成本、速度

**推荐配置**：
```
📝 技术文档：temperature=0, max_tokens=1000
🎨 创意写作：temperature=0.8, frequency_penalty=0.5
💡 头脑风暴：temperature=1.2, presence_penalty=1.5
💬 客户服务：temperature=0.3, max_tokens=300
```

---

### 7. `07-agent-patterns.http` - Agent 设计模式 🤖
**涵盖内容**：
- 🔄 **ReAct 模式**（Reasoning + Acting）
  - Thought（思考）→ Action（行动）→ Observation（观察）循环
  - 适用于动态环境、需要根据反馈调整的任务
  - 示例：旅游规划（根据天气调整景点）

- 📋 **Plan-and-Execute 模式**
  - 先制定完整计划，再逐步执行
  - 适用于目标明确、步骤可预见的任务
  - 示例：博客文章创作（收集信息 → 整合内容）

- 🔍 **Self-Reflection 模式**（自我反思）
  - 执行后自我检查结果是否合理
  - 适用于需要高准确性的任务
  - 示例：数学计算验证

**学习目标**：
- 理解不同 Agent 模式的优劣和适用场景
- 掌握如何通过 System Prompt 引导模型思考
- 学会设计原子化的工具便于组合

**对比总结**：

| 模式 | 优势 | 劣势 | 适用场景 |
|------|------|------|----------|
| **ReAct** | 灵活、自适应 | 效率较低 | 客服对话、问题诊断 |
| **Plan-and-Execute** | 全局优化、高效 | 缺乏灵活性 | 内容创作、批量处理 |
| **Self-Reflection** | 提高准确性 | 额外开销 | 代码生成、事实核查 |

---

### 8. `08-legacy-tool-calling.http` - 传统工具调用方法 ⏳
**涵盖内容**：
- 📜 **历史背景**
  - 在原生 Function Calling 出现之前的工具调用方法
  - 理解技术演进：文本解析 → 结构化 API

- 🔤 **文本 ReAct 格式**（LangChain 风格）
  - 使用 "Thought/Action/Action Input/Observation" 文本格式
  - 通过正则表达式解析工具调用
  - 示例：天气查询、多步推理

- 🏷️ **XML 格式**（Anthropic Claude 2.x 风格）
  - 使用 `<function_calls>` 和 `<invoke>` 标签
  - 结构化但需要 XML 解析
  - 适合复杂嵌套参数

- 📋 **JSON 格式**（早期实现）
  - 在回复中嵌入 JSON 对象
  - 需要从自然语言中提取 JSON
  - 容易受格式错误影响

- 🆚 **对比现代 Function Calling**
  - 可靠性对比（解析准确性）
  - 开发体验对比（调试难度）
  - 为什么现代 API 更优

**学习目标**：
- 理解工具调用技术的演进历史
- 认识传统方法的局限性
- 体会原生 Function Calling 的优势

**关键启示**：
> 传统方法依赖"提示词工程 + 文本解析"，容易出错且难以调试。现代 Function Calling 通过 API 原生支持，提供了类型安全、错误提示和结构化响应，是更好的选择。

---

### 9. `09-api-protocol-compatibility.http` - API 协议兼容性 🔄
**涵盖内容**：
- 🔀 **OpenAI vs Anthropic 协议差异**
  - 请求格式对比（messages、tools、system）
  - 响应格式对比（choices、content、tool_calls）
  - 参数命名差异

- 🎯 **GLM-4.7 使用 Anthropic 协议**
  - 智谱 GLM API 采用 Anthropic 格式
  - System Prompt 的位置差异
  - 工具调用格式差异

- 🛠️ **为什么需要协议转换**
  - 多模型集成需求
  - 代码复用和统一接口
  - 不同 SDK 的兼容性

- 💡 **最佳实践**
  - 使用适配器模式封装 API 差异
  - 统一的内部数据结构
  - 配置化的模型切换

**学习目标**：
- 理解不同 AI 厂商的 API 协议差异
- 掌握如何设计兼容多种协议的系统
- 学会使用适配器模式处理协议转换

**设计建议**：
```typescript
// 统一接口示例
interface UnifiedChatRequest {
  model: string;
  messages: Message[];
  tools?: Tool[];
  temperature?: number;
}

// 适配器
class OpenAIAdapter implements ChatProvider { ... }
class AnthropicAdapter implements ChatProvider { ... }
```

---

## ⚠️ 模型能力差异说明

本示例集合主要使用 **StepFun** 模型进行演示。不同模型的能力存在差异：

### 核心能力对比

| 模型 | 上下文窗口 | Function Calling | 多模态 | 推荐场景 |
|------|-----------|-----------------|--------|---------|
| **Claude Opus 4.6** | 200K | ✅ 原生支持 | ✅ 原生多模态 | 复杂任务、代码生成 |
| **GPT-4o** | 128K | ✅ 原生支持 | ✅ 原生多模态 | 通用场景 |
| **StepFun step-3.5-flash** | 32K | ✅ 原生支持 | ⚠️ 非原生 | 成本敏感、中文任务 |
| **DeepSeek V3** | 64K | ✅ 原生支持 | ❌ 无 | 代码生成、推理 |
| **智谱 GLM-4** | 128K | ✅ Anthropic 格式 | ⚠️ 非原生 | 中文任务 |

### API 协议差异

不同模型厂商的 API 格式存在差异：

1. **OpenAI 格式**（最通用）
   - StepFun、DeepSeek、OpenAI 系列
   - 请求格式：`{"messages": [...], "tools": [...]}`

2. **Anthropic 格式**
   - Claude 系列、智谱 GLM
   - 请求格式：`{"messages": [...], "system": "...", "tools": [...]}`

3. **协议转换**
   - 可使用 Claude Code Router 进行格式转换
   - 详见 `09-api-protocol-compatibility.http`

### 本示例集的模型选择

- **主要使用**: StepFun step-3.5-flash（性价比高）
- **对比测试**: DeepSeek V3、GLM-4
- **原因**:
  - StepFun 对 Function Calling 支持良好
  - 成本相对较低
  - 中文处理能力优秀

### 使用其他模型的注意事项

1. **切换 API 地址**: 修改 `@baseUrl` 变量
2. **更换 API Key**: 修改对应的 `@apiKey` 变量
3. **检查参数兼容性**: 部分模型不支持所有参数（如 `frequency_penalty`）
4. **测试 Function Calling**: 不同模型的工具调用格式可能略有差异

---

## 🚀 使用方法

### 1. 环境配置

创建 `.env` 文件，添加 API Keys：

```env
STEPFUN_API_KEY=sk-xxxxx
DEEPSEEK_API_KEY=sk-xxxxx
```

确保 `.env` 在 `.gitignore` 中。

### 2. 工具推荐

**VS Code** + **REST Client 插件**：
- 安装：在 VS Code 中搜索 "REST Client"
- 使用：打开 `.http` 文件，点击 "Send Request"
- 优势：支持变量、环境管理、响应预览

**JetBrains IDE**（IntelliJ IDEA / WebStorm）：
- 内置 HTTP Client
- 打开 `.http` 文件，点击左侧的绿色箭头
- 支持环境变量和响应历史

### 3. 学习路径

**初学者**（入门路径）：
1. `01-main.http` - 理解基本 API 用法
2. `02-limitations.http` - 认识 LLM 的边界
3. `03-practical-scenarios.http` - 学习实用场景

**进阶者**（深入学习）：
1. `04-function-calling-advanced.http` - 掌握工具调用
2. `05-prompt-engineering.http` - 优化提示词技术
3. `06-parameter-experiments.http` - 理解参数影响

**专家**（系统设计）：
1. `07-agent-patterns.http` - 理解 Agent 设计模式
2. `08-legacy-tool-calling.http` - 了解技术演进历史
3. `09-api-protocol-compatibility.http` - 掌握多协议兼容
4. 组合不同技术（如 Few-Shot + CoT + Function Calling）
5. 设计完整的 AI 工作流

---

## 📚 参考资料

### 官方文档
- [StepFun Tool Call 文档](https://platform.stepfun.com/docs/guide/tool_call)
- [StepFun Chat Completion 文档](https://platform.stepfun.com/docs/api-reference/chat/chat-completion-create)

### 提示词工程
- [Chain-of-Thought Prompting Guide](https://www.promptingguide.ai/techniques/cot)
- [Few-Shot Prompting Guide](https://www.promptingguide.ai/techniques/fewshot)
- [Prompt Engineering Guide 2026](https://www.lakera.ai/blog/prompt-engineering-guide)

### Agent 模式
- [ReAct Paper (arXiv)](https://arxiv.org/abs/2210.03629)
- [ReAct Prompting Guide](https://www.promptingguide.ai/techniques/react)
- [IBM ReAct Agent](https://www.ibm.com/think/topics/react-agent)
- [ReAct vs Plan-and-Execute](https://dev.to/jamesli/react-vs-plan-and-execute-a-practical-comparison-of-llm-agent-patterns-4gh9)

### LLM 局限性研究
- [大模型的科学解释和逻辑增强](https://www.caa.org.cn/article/345/5045.html)
- [大模型幻觉及其价值风险](http://www.news.cn/tech/20250411/250a24bfd95c4551869630f53e9584d6/c.html)
- [大模型推理综述](https://hub.baai.ac.cn/view/33739)

---

## 💡 核心概念总结

### 1. LLM 的本质
- LLM 是基于**概率预测**的语言模型，不是符号推理系统
- 擅长：语言理解、生成、模式识别
- 不擅长：精确计算、严格逻辑、实时信息

### 2. Function Calling 是关键
- Function Calling 是弥补 LLM 局限性的核心技术
- 将 LLM 作为"协调者"，调用专业工具完成具体任务
- 工具设计原则：原子化、清晰的接口、结构化的错误

### 3. Agent = LLM + Tools + Patterns
- Agent 不是单一技术，而是设计模式
- 核心：让 LLM 自主决策工具调用的顺序和参数
- 关键：通过 System Prompt 引导思考过程

### 4. 提示词工程的重要性
- 好的提示词可以显著提升模型表现
- 技术：Few-Shot、Chain-of-Thought、Self-Reflection
- 原则：清晰、具体、包含示例

---

## 🎯 实战建议

### 开发流程
1. **先设计工具接口**：使用 JSON Schema 定义参数
2. **编写测试用例**：覆盖正常流程和边界情况
3. **迭代优化提示词**：根据实际表现调整 System Prompt
4. **记录调用日志**：便于调试和分析

### 性能优化
- 使用 `temperature=0` 提高确定性
- 并行调用独立工具，减少延迟
- 对于长任务，使用流式响应提升用户体验
- 缓存常用的工具结果

### 成本控制
- 优先使用高效模型（如 `step-3.5-flash`）
- 避免不必要的工具调用
- 使用 `max_tokens` 限制输出长度
- 在提示词中明确"只调用必要的工具"

---

## 📊 示例统计

| 文件 | 示例数 | 难度 | 预计学习时间 | 状态 |
|------|--------|------|--------------|------|
| `01-main.http` | 7 | ⭐ 入门 | 30 分钟 | ✅ |
| `02-limitations.http` | 15 | ⭐⭐ 进阶 | 1 小时 | ✅ |
| `03-practical-scenarios.http` | 18 | ⭐⭐ 进阶 | 2 小时 | ✅ |
| `04-function-calling-advanced.http` | 13 | ⭐⭐⭐ 高级 | 1.5 小时 | ✅ |
| `05-prompt-engineering.http` | 20 | ⭐⭐ 进阶 | 1.5 小时 | ✅ |
| `06-parameter-experiments.http` | 29 | ⭐⭐⭐ 高级 | 2 小时 | ✅ |
| `07-agent-patterns.http` | 9 | ⭐⭐⭐⭐ 专家 | 2 小时 | ✅ |
| `08-legacy-tool-calling.http` | 17 | ⭐⭐⭐ 高级 | 1.5 小时 | ✅ |
| `09-api-protocol-compatibility.http` | - | ⭐⭐ 进阶 | 30 分钟 | ✅ |
| **总计** | **128** | - | **12.5 小时** | ✅ |

---

## 🤝 贡献

如果你有新的示例或改进建议，欢迎贡献！

---

## 📝 更新日志

### 2026-02-09（晚）- 完整版发布 🎉
- ✅ **P0 完成**：大模型局限性、Function Calling 高级、Agent 模式（37 个示例）
- ✅ **P1 完成**：提示词工程（Few-Shot、CoT、结构化输出、角色扮演）（20 个示例）
- ✅ **P2 完成**：参数实验（Temperature、Top-P、Max Tokens、Frequency/Presence Penalty、模型对比）（29 个示例）
- ✅ **P3 完成**：实用场景（代码审查、摘要、情感分析、翻译、数据提取、内容生成）（18 个示例）
- ✅ **补充内容**：传统工具调用方法（文本 ReAct、XML、JSON 格式）（17 个示例）
- ✅ **补充内容**：API 协议兼容性（OpenAI vs Anthropic 格式差异）
- ✅ 总计 **128+ 个高质量示例**，涵盖从入门到专家的完整学习路径
- ✅ 所有示例使用 **StepFun** 模型（主要）+ DeepSeek、GLM（对比）
- ✅ 文件采用数字前缀（01-09）便于 IDE 中按顺序浏览
- ✅ 包含详细注释、最佳实践和完整的参考资料

---

**Happy Coding! 🚀**
