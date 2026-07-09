---
title: Prompt Caching And KV Cache Mechanics
author: Research Compilation
date: 2026-03-07
url: https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching
tier: T1
topics: [prompt-caching, kv-cache, token-efficiency, anthropic, openai]
---

# Prompt Caching And KV Cache Mechanics

## Key Findings

### 1. Anthropic exposes cache usage as three input counters

`T1` Anthropic documents three relevant response fields:

- `cache_read_input_tokens`
- `cache_creation_input_tokens`
- `input_tokens`

It also gives the total input formula:

```text
total_input_tokens = cache_read_input_tokens + cache_creation_input_tokens + input_tokens
```

Source: https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching

### 2. Anthropic cache hierarchy is structural, not fuzzy

`T1` Anthropic states that cache prefixes are built in order:

```text
tools -> system -> messages
```

Changes at one level invalidate that level and all later levels.

Source: https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching

### 3. OpenAI exposes cached prompt tokens explicitly

`T1` OpenAI returns cache hit information in:

```json
usage.prompt_tokens_details.cached_tokens
```

It also states prompt caching only works on exact prompt prefixes.

Source: https://platform.openai.com/docs/guides/prompt-caching

### 4. OpenAI explicitly ties extended prompt caching to KV tensors

`T1` OpenAI states that extended prompt caching works by offloading key/value tensors to GPU-local storage, and describes these tensors as the intermediate representation from the model’s attention layers produced during prefill.

Source: https://platform.openai.com/docs/guides/prompt-caching

### 5. KV cache exists to avoid recomputing previous attention state

`T2` Hugging Face explains that key/value vectors are used to calculate attention scores and that KV cache stores these calculations so they can be reused without recomputing them.

Source: https://huggingface.co/docs/transformers/main/en/kv_cache

## Practical Implication

**[Author's analysis]** API-level cache counters are not just billing trivia. They are a surface-level signal for whether the provider was able to reuse prefill work from an unchanged prefix.

For engineering decisions, the stable rule is:

1. Keep long-lived instructions and tool definitions stable
2. Put stable content first
3. Push dynamic content later
4. Watch cache hit counters instead of guessing
