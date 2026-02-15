---
title: "hwchase17/react ReAct Prompt Template"
author: "Harrison Chase (hwchase17)"
date: "2023-01-01"
url: "https://smith.langchain.com/hub/hwchase17/react"
tier: T2
topics: [react, agent, prompt-template, langchain]
---

# hwchase17/react - LangChain Hub ReAct Prompt

这是 LangChain Hub 上最经典的 ReAct 提示词模板，由 LangChain 创始人 Harrison Chase 创建。

## 原始提示词

```
Answer the following questions as best you can. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought:{agent_scratchpad}
```

## 变量说明

| 变量 | 说明 |
|------|------|
| `{tools}` | 可用工具的描述列表 |
| `{tool_names}` | 工具名称列表，用于限制 Action 的取值 |
| `{input}` | 用户输入的问题 |
| `{agent_scratchpad}` | Agent 的思考过程记录区 |

## 使用方式

```python
from langchain import hub

# 从 LangChain Hub 拉取提示词
prompt = hub.pull("hwchase17/react")

# 或使用 LangSmith SDK
from langsmith import Client
client = Client()
prompt = client.pull_prompt("hwchase17/react")
```

## 设计特点

1. **强制思考**: `Thought:` 必须在 `Action:` 之前
2. **格式约束**: 明确定义了 Thought/Action/Action Input/Observation 循环
3. **循环提示**: `... (this Thought/Action/Action Input/Observation can repeat N times)`
4. **终止条件**: `Thought: I now know the final answer` 作为循环终止信号

## 统计数据

- ⭐ 222 stars
- 📥 218k pulls
- 📊 7.72M views

## 相关资源

- [LangChain Hub - hwchase17/react](https://smith.langchain.com/hub/hwchase17/react)
- [GitHub - langchain-hub](https://github.com/hwchase17/langchain-hub)
