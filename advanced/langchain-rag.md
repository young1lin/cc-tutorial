# LangChain RAG

## 先说结论

截至我直接读取的最新源码，LangChain 默认和经典 RAG 路径，依然主要是把检索结果塞进 prompt，而不是把“RAG 内容”以某种独立通道交给模型内部处理。

这意味着一件事：

- 检索结果每轮都变
- prompt 前缀就会变
- input token cache 就会掉

如果你还把检索结果放进 `system`，缓存命中会更差。

## 我直接看的源码位置

LangChain 本地源码：

- [retrieval.py](vendor/langchain/libs/langchain/langchain_classic/chains/retrieval.py)
- [stuff.py](vendor/langchain/libs/langchain/langchain_classic/chains/combine_documents/stuff.py)
- [factory.py](vendor/langchain/libs/langchain_v1/langchain/agents/factory.py)

WeKnora 本地源码：

- [config.yaml](vendor/WeKnora/config/config.yaml)
- [context_template.yaml](vendor/WeKnora/config/prompt_templates/context_template.yaml)
- [session.go](vendor/WeKnora/internal/application/service/session.go)

## LangChain 经典 RAG 是怎么走的

### `create_retrieval_chain(...)`

[retrieval.py](vendor/langchain/libs/langchain/langchain_classic/chains/retrieval.py) 里，检索结果会被挂到 `context` 键。

这不是推测。源码就是这么写的。

### `create_stuff_documents_chain(...)`

[stuff.py](vendor/langchain/libs/langchain/langchain_classic/chains/combine_documents/stuff.py) 里，prompt 必须包含 `context`。

更关键的是，源码示例直接是这种形状：

```python
prompt = ChatPromptTemplate.from_messages(
    [("system", "What are everyone's favorite colors:\n\n{context}")]
)
```

这已经把问题说透了。经典 LangChain RAG 不只是“会把 context 放进 prompt”。它连官方示例都经常把它放进 `system`。

## 为什么这会打坏缓存

你前面已经有 [token.md](token.md) 了。这里直接落工程结论。

如果每轮检索到的 `context` 都不同，而你又把它塞进：

- `system`
- 很靠前的共享前缀
- 长 prompt 模板前半段

那么 provider 的 prefix cache 命中率就会明显下降。

不是因为 LangChain 特别坏。是因为 prompt shape 很差。

## 新版 LangChain 有什么变化

[factory.py](vendor/langchain/libs/langchain_v1/langchain/agents/factory.py) 说明新版高层 agent 已经暴露了这些能力：

- `checkpointer`
- `store`
- `interrupt_before`
- `interrupt_after`
- `cache`
- `middleware`

这说明 LangChain 现在的 agent 基础设施比老版本强很多。

但别搞错。它暴露了能力，不等于它自动替你做了缓存友好的 RAG。

框架更强了。默认 prompt shape 还是得你自己管。

## WeKnora 给了什么启发

WeKnora 不是一个“天然缓存友好”的例外。它的配置层同样有明显的 `{{contexts}}` 模板注入路径。

看这里：

- [config.yaml](vendor/WeKnora/config/config.yaml)
- [context_template.yaml](vendor/WeKnora/config/prompt_templates/context_template.yaml)

例如 `context_template.yaml` 里就是：

```text
Reference materials:
{{contexts}}

User question: {{query}}
```

所以它也不是把检索结果从 prompt 里完全剥离掉了。

但它有两点值得学：

1. 检索、模板、agent、GraphRAG、fallback 是拆开的
2. `context_template` 是独立配置，不是硬编码死在代码里

这很重要。因为一旦模板独立，你就能重构 prompt shape，而不是去魔改检索引擎。

## 缓存友好的改法

### 坏写法

```text
system:
  你是客服助手...
  以下是检索内容:
  {{contexts}}
  ...
```

坏在哪里：

- `system` 每轮都变
- 最长稳定前缀被打断
- 后面所有层都跟着失效

### 更好的写法

```text
system:
  你是客服助手...
  只允许基于提供的资料回答...

user:
  问题: {{query}}

assistant_context 或后置消息块:
  检索资料:
  {{contexts}}
```

如果 provider 支持更细的 cache breakpoint，就把断点放在：

- 固定 system
- 固定工具定义
- 固定业务说明

之后，再拼动态 `contexts`。

### 更进一步的写法

把稳定知识前置本地化，而不是每轮在线拼：

- 业务规则放进 skill
- 字段说明放进 skill
- 关键代码位置放进 skill
- 检索只拿“本轮新增事实”

这样动态上下文就会变短，稳定前缀就会变长。

这才是真正省 token。

## 一句硬话

**[Author's analysis]** 很多 RAG 项目根本不是“检索效果不够好”。是 prompt 结构太烂。把所有动态 context 都堆进最前面，再抱怨模型贵、慢、缓存不命中。这不是模型问题。是工程问题。

## 缓存友好的 RAG 重构方案

这部分不是概念说明。是改法。

目标只有一个：

- 尽量保住稳定前缀
- 把动态检索内容往后压
- 让 Anthropic/OpenAI 的 input cache 能持续命中更长前缀

### 现状基线

基于当前源码，可以把默认路径抽象成这样：

#### LangChain 经典路径

```text
user query
-> retriever
-> context
-> create_stuff_documents_chain
-> prompt(context + question)
-> model
```

#### WeKnora 模板路径

```text
system prompt
+ context_template({{contexts}}, {{query}})
-> model
```

这两条路的问题都一样：

- `contexts` 是动态的
- 还经常被放进很靠前的位置
- 前缀缓存很容易被打断

## 坏写法

### 坏写法 1：动态检索直接塞进 `system`

```python
prompt = ChatPromptTemplate.from_messages([
    ("system", """
你是企业知识库助手。
以下是检索结果：
{context}
请严格根据检索结果回答。
"""),
    ("human", "{input}")
])
```

坏点：

1. `context` 每轮都变
2. `system` 每轮都变
3. 最长稳定前缀直接断掉
4. tool definitions 和 system 后面的缓存价值一起缩水

### 坏写法 2：把 query 和 context 一起塞进一个大模板

```text
Reference materials:
{{contexts}}

User question:
{{query}}
```

这类模板在 WeKnora 里很好配，但如果整段都作为“核心主提示”参与每轮生成，缓存并不会因为模板可配置就 magically 变好。

模板可配置，不等于缓存友好。

## 好写法

### 好写法 1：固定 system，动态 context 后置

```python
prompt = ChatPromptTemplate.from_messages([
    ("system", """
你是企业知识助手。
你只能依据提供的资料回答。
如果资料不足，明确说明不足。
回答语言必须跟用户问题一致。
"""),
    ("human", "{input}"),
    ("human", "Retrieved materials:\n{context}")
])
```

为什么更好：

1. `system` 固定
2. 主行为约束固定
3. 动态 `context` 被推迟到后置消息
4. 稳定前缀更长

它不会让 cache 百分之百命中。那不现实。  
但它会比“每轮改 system”强得多。

### 好写法 2：把稳定业务知识前置本地化，把检索结果变成补充材料

这就是 `business-logic` skill 要做的事。

不要每轮都让模型重新吃这些稳定内容：

- 业务背景
- 接口字段
- 关键代码位置
- 常见规则
- 时序图

先把这些固化到本地 skill 文档。然后每轮 RAG 只检索：

- 新增事实
- 本轮用户特定资料
- 时效性内容

这样 `contexts` 变短，变化幅度也更小。

### 好写法 3：检索和回答拆两段

不要一股脑把所有检索块直接喂最终回答模型。

拆成：

1. 检索阶段
2. 筛选/压缩阶段
3. 最终回答阶段

结构像这样：

```text
query
-> retrieval
-> rerank
-> compress / shortlist
-> final answer prompt
```

这样做不是因为流程更优雅。是因为你不该让最终回答模型每轮都吞几十段脏 context。

## 基于 LangChain 的具体改法

### 方案 A：继续用 `create_retrieval_chain`，但改 prompt 位置

保留：

- retriever
- `create_retrieval_chain`
- `create_stuff_documents_chain`

只改 prompt：

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain

qa_prompt = ChatPromptTemplate.from_messages([
    ("system", """
You are a retrieval-grounded assistant.
Use only the provided materials.
If the materials are insufficient, say so.
Keep the answer in the same language as the user.
"""),
    ("human", "{input}"),
    ("human", "Reference materials:\n{context}")
])

qa_chain = create_stuff_documents_chain(model, qa_prompt)
rag_chain = create_retrieval_chain(retriever, qa_chain)
```

这是最小改动。

### 方案 B：在 `stuff` 前加压缩层

如果检索结果很多，不要直接 `stuff`。

先：

- rerank
- 去重
- 按业务分组
- 截断到最终真正需要的块

然后再进最终 prompt。

因为真正烧 token 的不是“有 RAG”。是“垃圾 context 太长”。

### 方案 C：Agent + middleware 模式

新版 LangChain `create_agent(...)` 已经有：

- `middleware`
- `cache`
- `checkpointer`
- `interrupt_before/after`

这意味着你可以把“检索”做成一个工具或 middleware，而不是把 RAG 完全绑定死在一个 monolithic prompt 里。

推荐思路：

1. 固定主 `system_prompt`
2. 用工具做 retrieval
3. retrieval 返回结构化结果
4. 只把 shortlist 后的内容拼到最终回答阶段

这样 prompt 的稳定部分会更稳定。

## 基于 WeKnora 的具体改法

WeKnora 最容易改的不是检索引擎。是模板。

你已经有：

- `config.yaml`
- `prompt_templates/context_template.yaml`
- `custom agent` 的 `context_template`

所以先改模板分层。

### 现有思路

```text
Reference materials:
{{contexts}}

User question:
{{query}}
```

### 建议改成两层

第一层：稳定 system prompt

```text
You are WeKnora.
Only answer from provided materials.
If insufficient, say so.
Use the user's language.
```

第二层：后置动态 context block

```text
User question:
{{query}}

Retrieved materials:
{{contexts}}
```

这样至少不会让系统规则和动态检索一起抖动。

### 更进一步

把 `context_template` 再细分成：

1. `instruction_template`
2. `retrieval_context_template`
3. `fallback_template`

不要让一个模板同时承担：

- system behavior
- retrieval injection
- fallback logic
- formatting rules

这会让缓存、维护性和调试一起烂掉。

## 推荐迁移步骤

### 第一步：先测当前 cache 命中

看真实字段，不要靠感觉：

- Anthropic: `cache_read_input_tokens`, `cache_creation_input_tokens`, `input_tokens`
- OpenAI: `usage.prompt_tokens_details.cached_tokens`

### 第二步：固定 system

把所有稳定规则抽出去。不要混进动态 `contexts`。

### 第三步：把动态检索后置

把 `contexts` 从 `system` 或超前位置挪到后面。

### 第四步：缩 context

做：

- rerank
- dedupe
- chunk merge
- shortlisting

### 第五步：把稳定项目知识从 RAG 挪到 skill

例如：

- 业务流程
- API 字段
- 关键代码行号
- 权限规则

这些不该每轮在线检索。

## 改完之后应该看到什么

如果改法是对的，你通常会看到：

1. `cached input tokens` 增加
2. 首 token 延迟下降
3. 相同会话里的重复问答更快
4. provider 账单里的重复 input 成本下降

如果改完没有变化，通常不是 provider 不行，是你还有这些问题：

- system 还在偷偷变
- 工具 schema 还在变
- 检索结果还插在太前面
- 每轮都在换 prompt wording

## 最终建议

最务实的路线不是“推倒重做 RAG”。是分三刀：

1. 先改 prompt shape
2. 再压缩 context
3. 最后把稳定知识迁到 skill

这三刀下去，cache、延迟、可维护性会一起改善。

## LangChain 对照样例

### 坏写法

这个写法的问题不是不能跑。是太浪费前缀缓存。

```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain

model = ChatOpenAI(model="gpt-4o-mini")

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are an enterprise support assistant.
Use the following retrieved content to answer the user:

{context}

If the content is insufficient, say so.""",
        ),
        ("human", "{input}"),
    ]
)

qa_chain = create_stuff_documents_chain(model, prompt)
rag_chain = create_retrieval_chain(retriever, qa_chain)
```

坏点：

- `context` 直接进 `system`
- 每轮检索变化都会改写系统前缀
- cache 很难稳定命中

### 好写法

这个版本不神奇。但更缓存友好。

```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain

model = ChatOpenAI(model="gpt-4o-mini")

qa_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are an enterprise support assistant.
Answer only from provided materials.
If the materials are insufficient, say so clearly.
Keep the answer in the same language as the user.""",
        ),
        ("human", "User question:\n{input}"),
        ("human", "Retrieved materials:\n{context}"),
    ]
)

qa_chain = create_stuff_documents_chain(model, qa_prompt)
rag_chain = create_retrieval_chain(retriever, qa_chain)
```

为什么更好：

- `system` 固定
- 用户问题和检索材料后置
- 稳定前缀更长

### 更进一步的版本

如果你已经用 LangChain agent，不要让 retrieval 直接污染主 prompt。

```python
from langchain.agents import create_agent

agent = create_agent(
    model="anthropic:claude-sonnet-4-5",
    system_prompt="""You are an enterprise support assistant.
Use retrieval tools when needed.
Answer only from retrieved or provided materials.""",
    tools=[retrieve_tool, lookup_order_tool],
)
```

然后把 retrieval 工具返回值先做：

- rerank
- dedupe
- shortlist

最后再拼到最终回答阶段。不要工具一查到 20 段文本，就整包塞给模型。

## WeKnora 模板改造示例

### 现有形态

[context_template.yaml](vendor/WeKnora/config/prompt_templates/context_template.yaml) 现在的基本思路是：

```yaml
content: |
  Reference materials:
  {{contexts}}

  User question: {{query}}

  Please answer based on the above reference materials.
```

这比硬编码强。但还不够。

### 建议改成双层结构

先把稳定规则放在主 prompt：

```yaml
summary:
  prompt: |
    You are a professional retrieval assistant.
    Answer only from provided materials.
    If the materials are insufficient, say so clearly.
    Always use the same language as the user.
```

再把动态部分放进 `context_template`：

```yaml
templates:
  - id: "cache_friendly_context"
    name: "Cache Friendly Context"
    description: "Keep dynamic retrieval content late in the prompt"
    has_knowledge_base: true
    content: |
      User question:
      {{query}}

      Retrieved materials:
      {{contexts}}

      Please answer the user's question based only on the retrieved materials.
```

### 再往前走一步

把现有单块模板拆成三类：

```text
instruction_template
retrieval_context_template
fallback_template
```

分工：

- `instruction_template`: 永久稳定规则
- `retrieval_context_template`: 动态检索内容
- `fallback_template`: 无命中时的补救逻辑

这样做的好处不是“优雅”。是你终于能单独优化缓存，而不是每次一动模板就把所有行为绑着一起动。

## 一份务实的迁移清单

### 对 LangChain 项目

1. 找到所有 `create_stuff_documents_chain`
2. 检查 `{context}` 是否在 `system`
3. 把 `{context}` 挪到后置 message
4. 增加 rerank / shortlist
5. 观察 cached input token 变化

### 对 WeKnora 风格项目

1. 找到 `summary.prompt`
2. 找到 `context_template`
3. 把稳定规则从 `context_template` 挪回 `summary.prompt`
4. 让 `context_template` 只承载 `query + contexts`
5. 如有 fallback，再单独拆模板

## 一个最终判断标准

如果你改完之后，仍然每轮都在重写这些东西：

- system wording
- 长规则文本
- 工具定义
- 检索说明
- 引用格式规范

那你还没有真的做完缓存优化。你只是把烂 prompt 换了个文件放。
