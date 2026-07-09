# Token Efficiency And Input Cache

## 先说结论

省 token，靠的不是“让模型更省着说话”。靠的是减少重复 prefill。

每次请求里最贵、最慢的部分，往往不是生成最后几十个 token，而是把前面那一大坨提示词、工具定义、历史消息、检索上下文重新过一遍模型。你每次都重喂一遍，模型每次都重算一遍。钱和延迟就这么烧掉。

`T1` Anthropic 和 OpenAI 都明确提供了 prompt/input cache 机制，用来减少这部分重复成本。[Anthropic prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching) [OpenAI prompt caching](https://platform.openai.com/docs/guides/prompt-caching)

## 什么是 input cache token

### Anthropic

`T1` Anthropic 在响应里提供：

- `cache_read_input_tokens`
- `cache_creation_input_tokens`
- `input_tokens`

并明确给出总输入公式：

```text
total_input_tokens = cache_read_input_tokens + cache_creation_input_tokens + input_tokens
```

含义不是玄学：

- `cache_read_input_tokens`：这次直接从缓存读出来的前缀 token
- `cache_creation_input_tokens`：这次新写入缓存的前缀 token
- `input_tokens`：断点之后没被缓存的 token

来源：[Anthropic prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)

### OpenAI

`T1` OpenAI 在 `usage.prompt_tokens_details.cached_tokens` 里返回命中的缓存 token 数。[OpenAI prompt caching](https://platform.openai.com/docs/guides/prompt-caching)

这和 Anthropic 的字段名不同，但本质一样：告诉你这次请求里，有多少前缀没有重新完整计算。

## 从顶层 JSON 到底层 Attention 机制

顶层 API 返回的缓存字段，往下落到实现层，核心不是“缓存字符串”。核心是缓存 prefill 阶段算出来的中间表示。

`T1` OpenAI 官方明确写了，Extended Prompt Caching 会把 attention layers 在 prefill 阶段产生的 key/value tensors 持久到 GPU 本地存储；原始客户文本并不会以同样方式持久化。[OpenAI prompt caching](https://platform.openai.com/docs/guides/prompt-caching)

`T2` Hugging Face 文档解释得更直接：KV cache 保存的是用于 attention 计算的 key/value 向量，避免模型在自回归生成时对先前 token 重复做同样的计算。[HF KV cache docs](https://huggingface.co/docs/transformers/main/en/kv_cache)

所以链条是这样的：

1. 你在 JSON 里发了一大段固定前缀
2. 模型先做 prefill，把这些 token 过一遍 Transformer
3. 每一层 attention 都产出对应 token 的 key/value 表示
4. 这些 K/V 就是后续 token 继续生成时要反复用到的“历史记忆”
5. 如果下一次请求前缀完全一致，系统就没必要把这段前缀重新完整 prefill 一次
6. 于是 API 层把这部分记成 cached input tokens

**[Author's analysis]** 你可以把它理解成：缓存命中的不是“这段话的语义总结”，而是“这段前缀已经走过网络之后留下的可继续计算的中间产物”。

## 为什么缓存之前算好的向量

因为 attention 的代价不低，重复前缀的重复计算纯属浪费。

`T2` Hugging Face 明确说，自回归模型是一 token 一 token 预测，每一步都依赖之前 token；没有 KV cache，就会反复计算已经看过的历史 token。[HF KV cache docs](https://huggingface.co/docs/transformers/main/en/kv_cache)

这也是 prompt cache 真正值钱的地方：

- 降低延迟
- 降低重复 input 成本
- 让长 system prompt、长工具定义、长代码上下文不必每轮重算

## 为什么把静态内容放前面

`T1` OpenAI 官方说得很死：只有 exact prefix match 才可能命中缓存，所以静态内容应该放前面，动态内容放后面。[OpenAI prompt caching](https://platform.openai.com/docs/guides/prompt-caching)

`T1` Anthropic 也明确建议把稳定内容放在提示开头，并按 `tools -> system -> messages` 的层级形成缓存前缀。[Anthropic prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)

所以真正省 token 的提示结构，应该像这样：

1. 工具定义
2. 长期稳定的 system instruction
3. 长期稳定的项目背景
4. 可复用示例
5. 这次新来的用户问题
6. 这次动态检索到的上下文

不是反过来。

## 为什么 LangChain 式 RAG 容易打爆缓存

先说准一点。不是“LangChain 必然让缓存失效”。是 LangChain 很多常见 RAG 样式，会把动态检索内容直接拼进统一 prompt 模板，甚至放进 `system` message。这样做对缓存很不友好。

`T1` LangChain 官方示例和生态文档里，常见写法就是把 `{context}` 直接塞进 system prompt 或统一 QA prompt，再交给 `create_stuff_documents_chain` / retrieval chain。[LangSmith tracing quickstart](https://docs.langchain.com/langsmith/observability-quickstart) [LangChain retrieval docs](https://docs.langchain.com/oss/python/langchain/retrieval) [LangChain integration example](https://docs.langchain.com/oss/python/integrations/vectorstores/sqlserver)

`T1` Anthropic 明确说明缓存层级是 `tools -> system -> messages`，而且某一层发生变化，会让该层及其后续层失效。[Anthropic prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)

这两件事一拼起来，结论就出来了：

如果你的 RAG 每次都把不同检索片段塞进 `system`：

1. `system` 每轮都变
2. `system` cache 失效
3. `messages` cache 也跟着失效
4. 你上一轮辛苦攒下来的 input cache 命中率直接塌掉

**[Author's analysis]** 所以问题不在 LangChain 这三个字。问题在 prompt shape。LangChain 只是太方便了，方便到很多人顺手把动态上下文塞进了最不该频繁变化的那一层。

## 更缓存友好的 RAG 结构

更好的做法不是“不要 RAG”。那是废话。更好的做法是把稳定前缀和动态检索硬拆开。

推荐结构：

1. 把稳定的 system instruction 固定住
2. 把工具定义固定住
3. 把业务背景或操作手册固定住
4. 把检索结果尽量放在后面
5. 如果供应商支持显式 cache breakpoint，就把断点放在稳定内容之后、动态内容之前

这时即使 RAG 每轮都变，至少前面的大块稳定前缀还能继续命中。

## 省 Token 的实战手法

### 1. 固定系统提示词

不要每轮改 system wording。哪怕只是改了一个开关、一个引用设置、一个工具参数，也可能让前缀命中率掉下去。

### 2. 工具定义尽量稳定

`T1` Anthropic 明确说，修改 tool definitions 会让整个缓存失效。[Anthropic prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)

### 3. 动态检索放后面

别把检索上下文塞进最前面的 system 长文本里。把它放到后置消息或后置上下文块里。

### 4. 业务知识静态化

这就是为什么前面要做 `business-logic` skill。把稳定的业务骨架、字段说明、关键行号、时序图写进本地文档后，很多重复说明就不必每轮都靠在线检索和临时拼接。

### 5. 控制消息块数量和编辑位置

`T1` Anthropic 文档指出，自动缓存只会往前检查有限数量的 block；如果你在太靠前的位置改内容，又没有额外断点，命中会失败。[Anthropic prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)

### 6. 监控缓存字段

不要靠感觉优化。看真实返回值：

- Anthropic: `cache_read_input_tokens`, `cache_creation_input_tokens`, `input_tokens`
- OpenAI: `usage.prompt_tokens_details.cached_tokens`

## 一个粗暴但有效的判断标准

如果你每次请求都在重写下面这些东西，你的 token 通常浪费得很厉害：

- system prompt
- 工具 schema
- 长示例
- 长代码库背景
- RAG 检索片段的拼接方式

如果这些东西大部分是稳定的，却还在每轮重算，那不是模型贵。是 prompt 结构太烂。

## 缓存的价格与时效

`T1` Anthropic 官方给出的缓存计价与生命周期（[Anthropic prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)）：

- 默认 TTL 5 分钟，每次命中刷新存活时间。
- 可选 1 小时 TTL，适合调用间隔超过 5 分钟的场景。
- 写缓存不免费：5 分钟档按基础 input 价格的 1.25 倍计费，1 小时档按 2 倍计费。
- 读缓存便宜一个数量级：按基础 input 价格的 0.1 倍计费。
- 一次请求最多 4 个显式 cache breakpoint。

**[Author's analysis]** 这组数字给出一个硬判断：缓存只在「同一前缀会被反复读」时划算。写一次 1.25 倍，读一次 0.1 倍——前缀被复用一次就回本。反过来，每轮都变的内容塞进缓存段，等于花 1.25 倍的钱买永远不会命中的缓存。

## 边界

`T4` 并不是所有 provider 的缓存实现都完全一样。上面关于 Anthropic 和 OpenAI 的字段、缓存层级、命中条件，是有官方文档支持的。关于更底层的“到底缓存哪些张量、保留多久、如何路由到同机”，不同厂商实现细节会不同。

但工程结论很稳定：

- 稳定前缀越长，缓存价值越大
- 动态内容越靠后，缓存越容易命中
- RAG 拼接越粗暴，缓存越容易失效
- 持久化项目知识，能减少重复 prefill
