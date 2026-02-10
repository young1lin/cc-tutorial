# Chapter 24: 当 AI 失败时 - HTTP 连接限制案例研究

## 学习目标

完成本章后，你将能够：

- 理解 LLM 失败的真实案例
- 分析为什么 AI 会犯某些特定的错误
- 学会如何避免类似的 AI 错误
- 建立对 AI 输出的健康怀疑态度
- 知道何时以及如何验证 AI 的输出

## 前置知识

- [Chapter 23: LLM 真实工作原理](chapter-23-how-llms-work.md)
- 基本的 Web 开发知识

---

## 24.1 案例背景：浏览器 HTTP 连接限制

### 24.1.1 问题陈述

```
场景：开发一个需要同时发送多个 API 请求的 Web 应用

需求：
- 用户点击"加载所有数据"按钮
- 需要从 100 个不同的 API 端点获取数据
- 希望尽可能快地完成

开发者问 AI：
"如何同时发送 100 个 HTTP 请求？"

AI 的回答（简化）：
"使用 Promise.all() 并行发送所有请求！"
```

### 24.1.2 AI 给出的代码

```typescript
/**
 * ❌ AI 生成的"解决方案"
 * 这个代码看起来正确，但实际上有严重问题
 */

async function fetchAllData(urls: string[]): Promise<any[]> {
  // AI 建议：使用 Promise.all 并行发送所有请求
  const responses = await Promise.all(
    urls.map(url => fetch(url))
  );

  const data = await Promise.all(
    responses.map(response => response.json())
  );

  return data;
}

// 使用
const urls = Array.from({ length: 100 }, (_, i) =>
  `https://api.example.com/data/${i}`
);

const allData = await fetchAllData(urls);
```

---

## 24.2 为什么这是错误的

### 24.2.1 浏览器 HTTP 连接限制

```
┌─────────────────────────────────────────────────────────────┐
│              浏览器 HTTP/1.1 连接限制                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  HTTP/1.1 协议限制：                                         │
│  - 每个域名最多 6 个并发连接（Chrome/Firefox）             │
│  - 总连接数有上限（通常 100-300 个）                        │
│                                                             │
│  HTTP/2 协议：                                               │
│  - 支持多路复用，单连接可以处理多个请求                      │
│  - 但仍然受到服务器和浏览器的限制                            │
│                                                             │
│  问题：                                                     │
│  ┌─────────────────────────────────────────────┐           │
│  │  同时发送 100 个请求                         │           │
│  │  ├─ 前 6 个：立即发送 ✓                     │           │
│  │  ├─ 接下来的 N 个：排队等待...              │           │
│  │  └─ 超出限制的：失败/超时 ✗                 │           │
│  └─────────────────────────────────────────────┘           │
│                                                             │
│  后果：                                                     │
│  - 请求超时                                                 │
│  - 连接池耗尽                                               │
│  - 内存占用过高                                             │
│  - 用户体验差                                               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 24.2.2 实际问题演示

```typescript
/**
 * 实际运行时会发生什么
 */

/**
 * 问题 1: 连接排队
 */
async function demonstrateQueueing() {
  const requests = [];
  const LIMIT = 6; // 浏览器并发限制

  // 前 6 个请求立即执行
  for (let i = 0; i < LIMIT; i++) {
    requests.push(
      fetch(`https://api.example.com/${i}`)
        .then(() => console.log(`Request ${i} completed`))
    );
  }

  // 剩余的请求需要等待前面的完成
  for (let i = LIMIT; i < 100; i++) {
    requests.push(
      fetch(`https://api.example.com/${i}`)
        .then(() => console.log(`Request ${i} completed`))
    );
    // 这些请求会排队，直到前面的完成
  }

  await Promise.all(requests);
}

/**
 * 问题 2: 请求超时
 */
async function demonstrateTimeout() {
  const urls = Array.from({ length: 100 }, (_, i) =>
    `https://api.example.com/slow-endpoint/${i}`
  );

  try {
    // 如果每个请求需要 2 秒，但有 6 个并发限制
    // 总时间 = ceil(100 / 6) * 2 ≈ 34 秒
    // 某些请求可能在 30 秒后超时
    const data = await Promise.all(
      urls.map(url => fetch(url, { timeout: 30000 }))
    );
  } catch (error) {
    console.error('Some requests timed out:', error);
  }
}

/**
 * 问题 3: 内存占用
 */
async function demonstrateMemoryUsage() {
  const urls = Array.from({ length: 100 }, (_, i) =>
    `https://api.example.com/large-data/${i}`
  );

  // 100 个并发请求 = 100 个响应体在内存中
  const responses = await Promise.all(
    urls.map(url => fetch(url))
  );

  // 如果每个响应 1MB，总共 100MB
  const data = await Promise.all(
    responses.map(r => r.json())
  );

  // 可能导致浏览器标签页崩溃
}

/**
 * 问题 4: 服务器拒绝
 */
async function demonstrateServerRejection() {
  const urls = Array.from({ length: 100 }, (_, i) =>
    `https://api.example.com/rate-limited/${i}`
  );

  // 服务器可能检测到异常流量
  // 并返回 429 (Too Many Requests)
  const results = await Promise.allSettled(
    urls.map(url => fetch(url))
  );

  const rejected = results.filter(r => r.status === 'rejected');
  console.log(`${rejected.length} requests were rejected`);
}
```

---

## 24.3 为什么 AI 犯了这个错误

### 24.3.1 AI 的"思考"过程

```
LLM 的推理链（推测）：

User: "如何同时发送 100 个 HTTP 请求？"

LLM 内部:
1. 识别关键词："同时", "HTTP 请求"
2. 搜索训练数据中的模式
3. 找到常见模式："Promise.all 用于并行"
4. 生成代码：Promise.all(urls.map(url => fetch(url)))
5. 输出：看起来合理且常见

问题：
- LLM 不知道浏览器的实际限制
- 训练数据中的代码示例通常规模较小
- 没有实际运行过代码
- 只是模式匹配，不是真正的工程推理
```

### 24.3.2 训练数据偏差

```typescript
/**
 * AI 训练数据中的代码示例
 */

// 大多数教程/博客/Stack Overflow 的示例

/**
 * ❌ 教程中的常见示例（小规模）
 */
// 示例 1: 3 个请求
const urls = ['/api/user', '/api/posts', '/api/comments'];
const data = await Promise.all(urls.map(url => fetch(url)));
// → 对 3 个请求没问题！

// 示例 2: 5 个请求
const endpoints = ['users', 'posts', 'comments', 'likes', 'shares'];
const results = await Promise.all(
  endpoints.map(e => fetch(`/api/${e}`))
);
// → 对 5 个请求也没问题！

// 示例 3: 10 个请求
const items = Array.from({ length: 10 }, (_, i) => i);
const data = await Promise.all(
  items.map(i => fetch(`/api/item/${i}`))
);
// → 对 10 个请求可能有问题，但不明显！

/**
 * AI 学习的模式：
 * "同时发送多个请求" → "Promise.all"
 *
 * 没有考虑：
 * - 规模（100 vs 10）
 * - 环境限制（浏览器连接池）
 * - 实际运行后果
 */
```

---

## 24.4 正确的解决方案

### 24.4.1 请求批处理

```typescript
/**
 * ✅ 正确的解决方案：并发限制
 */

/**
 * 方案 1: 使用 p-limit 库
 */
import pLimit from 'p-limit';

async function fetchAllDataCorrectly(urls: string[]): Promise<any[]> {
  // 限制并发数为 6（浏览器限制）
  const limit = pLimit(6);

  const requests = urls.map(url =>
    limit(() => fetch(url).then(r => r.json()))
  );

  return await Promise.all(requests);
}

/**
 * 方案 2: 手动实现并发控制
 */
async function fetchWithConcurrencyLimit(
  urls: string[],
  concurrency: number = 6
): Promise<any[]> {
  const results: any[] = [];
  const executing: Promise<any>[] = [];

  for (const url of urls) {
    const promise = fetch(url).then(r => r.json()).then(data => {
      executing.splice(executing.indexOf(promise), 1);
      return data;
    });

    results.push(promise);
    executing.push(promise);

    // 如果达到并发限制，等待一个完成
    if (executing.length >= concurrency) {
      await Promise.race(executing);
    }
  }

  return await Promise.all(results);
}

/**
 * 方案 3: 使用分块处理
 */
async function fetchInBatches(
  urls: string[],
  batchSize: number = 6
): Promise<any[]> {
  const results: any[] = [];

  // 将 URLs 分成每 batch 个一组
  for (let i = 0; i < urls.length; i += batchSize) {
    const batch = urls.slice(i, i + batchSize);

    // 并行处理当前批次
    const batchResults = await Promise.all(
      batch.map(url => fetch(url).then(r => r.json()))
    );

    results.push(...batchResults);

    // 可选：批次间添加延迟
    if (i + batchSize < urls.length) {
      await new Promise(resolve => setTimeout(resolve, 100));
    }
  }

  return results;
}
```

### 24.4.2 完整的生产级实现

```typescript
/**
 * 生产级的并发请求处理器
 */

interface RequestOptions {
  concurrency?: number;
  delayBetweenBatches?: number;
  retryAttempts?: number;
  retryDelay?: number;
  timeout?: number;
}

class ConcurrentRequestHandler {
  private readonly concurrency: number;
  private readonly delayBetweenBatches: number;
  private readonly retryAttempts: number;
  private readonly retryDelay: number;
  private readonly timeout: number;

  constructor(options: RequestOptions = {}) {
    this.concurrency = options.concurrency ?? 6;
    this.delayBetweenBatches = options.delayBetweenBatches ?? 0;
    this.retryAttempts = options.retryAttempts ?? 3;
    this.retryDelay = options.retryDelay ?? 1000;
    this.timeout = options.timeout ?? 30000;
  }

  async fetchAll<T>(urls: string[]): Promise<(T | null)[]> {
    const results: (T | null)[] = new Array(urls.length).fill(null);

    let index = 0;
    const executing: Map<number, Promise<void>> = new Map();

    for (const url of urls) {
      const currentIndex = index++;

      const promise = this.fetchWithRetry<T>(url)
        .then(data => {
          results[currentIndex] = data;
          executing.delete(currentIndex);
        })
        .catch(error => {
          console.error(`Failed to fetch ${url}:`, error);
          executing.delete(currentIndex);
        });

      executing.set(currentIndex, promise);

      // 控制并发
      if (executing.size >= this.concurrency) {
        await Promise.race(Array.from(executing.values()));
      }

      // 批次间延迟
      if (executing.size === 0 && this.delayBetweenBatches > 0) {
        await this.delay(this.delayBetweenBatches);
      }
    }

    // 等待所有请求完成
    await Promise.all(Array.from(executing.values()));

    return results;
  }

  private async fetchWithRetry<T>(
    url: string,
    attempt: number = 0
  ): Promise<T> {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(
        () => controller.abort(),
        this.timeout
      );

      const response = await fetch(url, {
        signal: controller.signal
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        throw new Error(
          `HTTP ${response.status}: ${response.statusText}`
        );
      }

      return await response.json();
    } catch (error) {
      if (attempt < this.retryAttempts) {
        console.warn(
          `Retry ${attempt + 1}/${this.retryAttempts} for ${url}`
        );
        await this.delay(this.retryDelay * (attempt + 1));
        return this.fetchWithRetry<T>(url, attempt + 1);
      }
      throw error;
    }
  }

  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

/**
 * 使用示例
 */
async function loadAllData() {
  const urls = Array.from({ length: 100 }, (_, i) =>
    `https://api.example.com/data/${i}`
  );

  const handler = new ConcurrentRequestHandler({
    concurrency: 6,        // 浏览器限制
    delayBetweenBatches: 100,  // 防止服务器过载
    retryAttempts: 3,
    retryDelay: 1000,
    timeout: 30000
  });

  const data = await handler.fetchAll<any>(urls);

  console.log(`Loaded ${data.filter(d => d !== null).length} items`);
}
```

---

## 24.5 其他常见 AI 错误案例

### 24.5.1 案例列表

```typescript
/**
 * 其他常见的 AI 编程错误
 */

/**
 * 错误 1: 忽略错误处理
 */

// ❌ AI 生成的代码（没有错误处理）
async function getUser(id: string) {
  const response = await fetch(`/api/users/${id}`);
  return await response.json();
}

// ✅ 正确的代码
async function getUser(id: string): Promise<User> {
  try {
    const response = await fetch(`/api/users/${id}`);

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Failed to fetch user:', error);
    throw error;
  }
}

/**
 * 错误 2: 不考虑边界情况
 */

// ❌ AI 生成的代码
function divide(a: number, b: number): number {
  return a / b;  // 没有检查除以零
}

// ✅ 正确的代码
function divide(a: number, b: number): number {
  if (b === 0) {
    throw new Error('Division by zero');
  }
  return a / b;
}

/**
 * 错误 3: 硬编码配置
 */

// ❌ AI 生成的代码
const API_KEY = 'sk-1234567890';  // 硬编码密钥！

// ✅ 正确的代码
const API_KEY = process.env.API_KEY;
if (!API_KEY) {
  throw new Error('API_KEY environment variable is required');
}

/**
 * 错误 4: 安全漏洞
 */

// ❌ AI 生成的代码（SQL 注入风险）
async function getUserByName(name: string) {
  const query = `SELECT * FROM users WHERE name = '${name}'`;
  return await db.query(query);
}

// ✅ 正确的代码（参数化查询）
async function getUserByName(name: string) {
  const query = 'SELECT * FROM users WHERE name = $1';
  return await db.query(query, [name]);
}

/**
 * 错误 5: 性能问题
 */

// ❌ AI 生成的代码（循环中的异步操作）
async function processItems(items: Item[]) {
  const results = [];
  for (const item of items) {
    const result = await fetch(`/api/items/${item.id}`);
    results.push(await result.json());
  }
  return results;
}

// ✅ 正确的代码（并行处理）
async function processItems(items: Item[]) {
  const results = await Promise.all(
    items.map(item =>
      fetch(`/api/items/${item.id}`).then(r => r.json())
    )
  );
  return results;
}
```

---

## 24.6 如何验证 AI 的输出

### 24.6.1 验证清单

```typescript
/**
 * AI 输出验证清单
 */

const VERIFICATION_CHECKLIST = {
  // 1. 功能正确性
  functionality: [
    "代码能运行吗？",
    "输出符合预期吗？",
    "边界情况处理了吗？"
  ],

  // 2. 性能考虑
  performance: [
    "有性能瓶颈吗？",
    "内存使用合理吗？",
    "网络请求优化了吗？"
  ],

  // 3. 安全性
  security: [
    "有注入漏洞吗？",
    "敏感信息处理了吗？",
    "输入验证了吗？"
  ],

  // 4. 错误处理
  errorHandling: [
    "所有可能的错误都处理了吗？",
    "错误信息有用吗？",
    "有重试机制吗？"
  ],

  // 5. 最佳实践
  bestPractices: [
    "符合项目规范吗？",
    "代码可读吗？",
    "需要重构吗？"
  ]
};

/**
 * 具体验证步骤
 */
async function verifyAICode(
  code: string,
  testCases: TestCase[]
): Promise<boolean> {
  // 1. 静态分析
  const staticAnalysis = analyzeCode(code);
  if (staticAnalysis.hasIssues) {
    console.warn('Static analysis found issues:', staticAnalysis.issues);
  }

  // 2. 运行测试
  const results = await runTests(code, testCases);
  if (!results.allPassed) {
    console.error('Some tests failed:', results.failures);
    return false;
  }

  // 3. 性能测试
  const performance = await measurePerformance(code);
  if (performance.isSlow) {
    console.warn('Performance concerns:', performance.issues);
  }

  // 4. 安全扫描
  const security = scanForSecurityIssues(code);
  if (security.hasVulnerabilities) {
    console.error('Security issues found:', security.vulnerabilities);
    return false;
  }

  return true;
}
```

### 24.6.2 使用 Claude Code 验证

```bash
# 使用 Claude Code 验证自己的输出

# 1. 让 Claude Code 检查潜在问题
# "请检查这段代码的潜在问题："

# 2. 让 Claude Code 生成测试
# "为这段代码生成单元测试："

# 3. 让 Claude Code 进行代码审查
# "请审查这段代码，找出可能的 bug："

# 4. 让 Claude Code 解释代码
# "请解释这段代码的工作原理："
# （确保你理解代码在做什么）
```

---

## 24.7 关键教训

### 24.7.1 理解 AI 的局限性

```
┌─────────────────────────────────────────────────────────────┐
│                    关键教训                                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. AI 不是魔法                                             │
│     - 它基于训练数据中的模式                                │
│     - 它没有真正的理解                                      │
│     - 它可能产生看起来合理但有问题的代码                     │
│                                                             │
│  2. AI 不知道环境约束                                       │
│     - 浏览器限制                                            │
│     - 服务器限制                                            │
│     - 网络条件                                              │
│     - 实际运行环境                                          │
│                                                             │
│  3. AI 缺乏实际经验                                         │
│     - 没有调试过代码                                        │
│     - 没有处理过生产问题                                    │
│     - 没有经历过性能调优                                    │
│                                                             │
│  4. AI 的建议需要验证                                       │
│     - 总是审查代码                                          │
│     - 运行测试                                              │
│     - 检查边界情况                                          │
│     - 测量性能                                              │
│                                                             │
│  5. 你仍然是工程师                                          │
│     - 你对代码负责                                          │
│     - 你做最终决定                                          │
│     - 你需要理解代码                                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 24.7.2 最佳实践

```typescript
/**
 * 与 AI 协作的最佳实践
 */

/**
 * 1. 提供充分的上下文
 */
// ❌ 不好
user: "如何发送多个 HTTP 请求？"

// ✅ 好
user: `
  我需要从 100 个不同的 API 端点获取数据。
  浏览器环境，考虑连接限制。
  请提供一个生产级的解决方案。
`

/**
 * 2. 使用 Plan Mode
 */
// Shift+Tab (两次) 激活 Plan Mode
// 让 AI 先规划，而不是直接写代码

/**
 * 3. 要求测试
 */
user: "请为这段代码生成测试，包括边界情况。"

/**
 * 4. 要求解释
 */
user: "请解释这段代码的工作原理和潜在问题。"

/**
 * 5. 迭代改进
 */
user: "这段代码有性能问题，请帮我优化。"
user: "请为这个函数添加错误处理。"
user: "请检查这段代码的安全漏洞。"
```

---

## 24.8 练习

### 练习 1：识别 AI 错误

以下 AI 生成的代码有什么问题？

```typescript
async function uploadFiles(files: File[]) {
  return await Promise.all(
    files.map(file => {
      const data = new FormData();
      data.append('file', file);
      return fetch('/upload', {
        method: 'POST',
        body: data
      });
    })
  );
}
```

### 练习 2：修复 AI 错误

修复上面的代码，考虑：
- 并发限制
- 错误处理
- 进度反馈

### 练习 3：审查 AI 输出

给定以下 AI 生成的代码，列出所有潜在问题：

```typescript
function getPassword(): string {
  const chars = 'abcdefghijklmnopqrstuvwxyz';
  let password = '';
  for (let i = 0; i < 8; i++) {
    password += chars[Math.floor(Math.random() * chars.length)];
  }
  return password;
}
```

---

## 24.9 进一步阅读

- [Browser Connection Limits](https://developer.chrome.com/docs/performance/network/)
- [Promise.all Concurrency](https://advancedweb.hu/how-to-use-async-functions-with-array-map-in-javascript/)
- [Chapter 25: AI 辅助 vs AI 自动化](chapter-25-assisted-vs-automated.md) - 下一章

---

## 视频脚本

### Episode 24: 当 AI 失败时 (18 分钟)

#### [0:00-1:00] 引入
**视觉元素**：
- 标题："AI 失败案例：浏览器连接限制"
- 错误代码示例

**内容**：
> AI 很强大，但它不是魔法。今天我们看一个真实的 AI 失败案例：当让它同时发送 100 个 HTTP 请求时会发生什么。
>
> 这个案例来自真实的项目，展示了 AI 的局限性，以及为什么我们需要验证它的输出。

#### [1:00-3:00] 问题背景
**视觉元素**：
- 需求说明
- AI 生成的代码

**内容**：
> 场景：需要从 100 个 API 端点获取数据。
>
> 开发者问 AI："如何同时发送 100 个 HTTP 请求？"
>
> AI 回答：使用 `Promise.all()` 并行发送所有请求。
>
> [展示 AI 生成的代码]
>
> 这段代码看起来很合理，对吧？但它有一个致命的问题。

#### [3:00-7:00] 为什么会失败
**视觉元素**：
- 浏览器连接限制示意图
- 请求排队动画

**内容**：
> 问题在于：**浏览器有 HTTP 连接限制**。
>
> HTTP/1.1 协议限制每个域名最多 6 个并发连接。
>
> [演示请求排队]
>
> - 前 6 个请求：立即发送 ✓
> - 剩余 94 个：排队等待...
>
> 这会导致：
> - 请求超时
> - 连接池耗尽
> - 内存占用过高
> - 用户体验差

#### [7:00-11:00] 为什么 AI 犯了这个错误
**视觉元素**：
- AI 的"思考"过程图解
- 训练数据示例

**内容**：
> 为什么 AI 会犯这个错误？
>
> **AI 的推理链**：
> 1. 识别关键词："同时", "HTTP 请求"
> 2. 搜索训练数据中的模式
> 3. 找到模式："Promise.all 用于并行"
> 4. 生成代码
>
> **问题**：
> - AI 不知道浏览器的实际限制
> - 训练数据中的示例通常规模较小（3-10 个请求）
> - 没有实际运行过代码
> - 只是模式匹配，不是真正的工程推理

#### [11:00-14:00] 正确的解决方案
**视觉元素**：
- 正确的代码实现
- 性能对比

**内容**：
> [展示正确的解决方案：并发限制]
>
> 使用 `p-limit` 库或手动实现并发控制。
>
> [代码演示]
>
> 这将 100 个请求分成多个批次，每批最多 6 个并发请求。既利用了并行性，又避免了连接池问题。

#### [14:00-16:00] 其他常见错误
**视觉元素**：
- 错误代码列表
- 快速修复

**内容**：
> 其他常见的 AI 编程错误：
>
> 1. **忽略错误处理** - 没有异常捕获
> 2. **不考虑边界情况** - 除以零
> 3. **硬编码配置** - API 密钥
> 4. **安全漏洞** - SQL 注入
> 5. **性能问题** - 循环中的异步

#### [16:00-18:00] 关键教训
**视觉元素**：
- 关键教训列表
- 验证清单

**内容**：
> **关键教训**：
> 1. AI 不是魔法 - 它基于模式匹配
> 2. AI 不知道环境约束 - 浏览器、服务器限制
> 3. AI 缺乏实际经验 - 没有调试过代码
> 4. AI 的建议需要验证 - 总是审查代码
> 5. **你仍然是工程师** - 你对代码负责
>
> **验证清单**：
> - 功能正确性
> - 性能考虑
> - 安全性
> - 错误处理
> - 最佳实践
>
> 下一章，我们将讨论"AI 辅助工程"与"AI 自动化工程"的区别。
