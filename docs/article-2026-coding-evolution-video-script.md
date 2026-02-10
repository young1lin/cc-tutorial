# 2026年古法编程注定被淘汰 - 视频脚本大纲（细化版）

## 视频概述
- **主题**: 展示 2026 年 AI 辅助编程的现实，从大模型原理到 Claude Code 实战
- **核心理念**: 小步快跑，逐步迭代 - 展示专业开发者如何用 AI 放大自身能力
- **时长**: 约 35-45 分钟
- **风格**: 技术分享 + 从零实战演示
- **配套文章**: `article-2026-coding-evolution.md`
- **演示素材**:
  - https://young1lin.github.io/posts/llm-0/ - LLM 入门
  - https://young1lin.github.io/posts/llm-1/ - LLM 原理
  - https://young1lin.github.io/posts/mcp/ - MCP 协议
- **实战项目**: 从零开发 Go 聊天历史查看器（Claude Code 聊天记录的 Web 界面）

---

## 第一部分：大模型原理入门（8-10 分钟）

### 目标
让观众理解 LLM 为什么强大，以及它的工作原理和局限性

### 内容结构

#### 1.1 引入（1 分钟）
- **开场问题**: "如果你还在靠 Google 搜索解决编程问题，那你可能已经落后了。国内开发更惨，只能用百度 + CSDN + 博客园这种垃圾内容聚集地获取所谓的知识。"
- **数据震撼**: Google Principal Engineer 一天完成团队一年的工作
- **主题预告**: 古法编程 vs AI 辅助编程

#### 1.2 LLM 基础知识讲解（2 分钟）【基于用户网站】

**参考资料**:
- https://young1lin.github.io/posts/llm-0/ - LLM 入门与学习资源推荐
- https://young1lin.github.io/posts/llm-1/ - LLM 原理深入探索

**核心内容**:

**为什么学习 LLM 不需要高性能 GPU？**
- 本地开发：CPU + 小模型足够
- API 调用：无需本地算力
- 专注于理解原理和应用

**学习路径推荐**:
- HuggingFace NLP Course
- Andrej Karpathy 的 YouTube 系列 "Neural Networks: Zero to Hero"
- 3B1B 的神经网络视频
- 李沐《动手学深度学习》

**避免幸存者偏差**:
- 不要只看成功案例
- 关注失败经验和学习曲线
- 理解 LLM 的局限性

**Token 的概念**:
- Token ≠ 字符，Token ≠ 单词
- 中文：1-2 个字符 ≈ 1 Token
- 英文：约 4 个字符 ≈ 1 Token
- 代码：符号、关键字各自独立 Token

**幻觉问题（Hallucination）**:
- LLM 会"自信地胡说八道"
- 不是真正理解，只是统计预测
- 需要验证和测试

**AI Agent 组成**:
1. **Planning（规划）** - 分解任务
2. **Memory（记忆）** - 上下文窗口
3. **Tools（工具）** - Function Calling

**ReAct 模式**:
```
Thought: 思考当前状态
Action: 选择一个工具执行
Observation: 观察执行结果
→ 重复直到完成
```

#### 1.3 上下文窗口概念（2 分钟）

**比喻：固定长度数组**
- **想象一个固定长度的数组**：
  ```
  context_window = [token1, token2, token3, ..., tokenN]
  ```
- **新 token 进来，旧 token 出去**（滑动窗口）
- **上下文窗口大小对比**：
  | 模型 | 上下文大小 |
  |------|-----------|
  | GPT-4 | 128K tokens |
  | Claude 3.5 Sonnet | 200K tokens |
  | Claude Opus 4.5 | 200K tokens |
  | DeepSeek-V3 | 64K - 128K tokens |

**为什么重要？**
- 上下文越大 → 能理解的代码越多
- 但不是无限大 → 需要管理上下文
- **CLAUDE.md 的作用**: 项目记忆，减少重复上下文

**演示**:
```bash
# 在 Claude Code 中查看上下文使用
claude
# Claude 会显示当前上下文使用情况
```

#### 1.4 猜下一个词的局限性（2 分钟）

**核心原理**:
```
用户输入: "def hello_world():"
LLM 思考: 下一个词最可能是什么？
  - "print" (概率: 0.35)
  - "return" (概率: 0.25)
  - "pass" (概率: 0.15)
  - ...

选中: "print"
继续: "(", '"', 'Hello', 'World', "'", ")"
```

**局限性演示**:
1. **幻觉问题**: 可能猜错，但"自信"地输出
2. **上下文依赖**: 没有 context 就无法理解意图
3. **无法推理**: 只是统计概率，不是真正"理解"

**为什么需要代理（Agent）？**
- 纯猜词 → 无法验证代码
- 代理 + 工具 → 可以运行、测试、修正代码

#### 1.5 HTTP API 调用演示（1.5 分钟）

**本地演示**:
```bash
# 1. 设置环境变量
export ANTHROPIC_API_KEY="your-api-key"

# 2. 发起 HTTP 请求
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{
    "model": "claude-opus-4-5",
    "max_tokens": 1024,
    "messages": [
      {"role": "user", "content": "用 Python 写一个 Hello World"}
    ]
  }'

# 3. 查看响应
# Claude 返回生成的代码
```

**对比展示**:
- **HTTP 调用**: 一次性请求，无状态
- **Claude Code 对话**: 有状态，上下文累积

#### 1.6 Function Calling 机制（1 分钟）

**什么是 Function Calling？**
```
用户: "帮我创建一个文件 test.txt"
Claude 分析: 需要调用 Write 工具
Claude 调用: Write("test.txt", "content")
系统执行: 文件创建成功
Claude 返回: "文件已创建"
```

**演示 Claude Code 的工具调用**:
```bash
claude
> 帮我创建一个 Python 文件

# Claude 会自动调用:
# 1. Write - 创建文件
# 2. Edit - 编辑文件
# 3. Bash - 运行测试
```

**工具列表**:
- `Read` - 读取文件
- `Write` - 写入文件
- `Edit` - 编辑文件
- `Bash` - 执行命令
- `Glob` - 搜索文件
- `Grep` - 搜索内容

#### 1.7 小结（0.5 分钟）
> "理解了原理，你就明白为什么 Claude Code 是'代理'而不是简单的'代码生成器'。它不只是猜词，而是理解意图、调用工具、验证结果。"

---

## 第二部分：不需要学习，直接问！（6-8 分钟）

### 目标
消除学习门槛，证明使用 Claude Code 不需要专门学习

### 核心观点
> "使用 Claude Code 不需要背诵文档，不懂的直接问 Claude Code 自己！"

### 内容结构

#### 2.1 为什么不需要学习？（1 分钟）

**传统工具的学习曲线**：
```
购买教程 → 阅读文档 → 背诵命令 → 练习使用
```

**Claude Code 的使用方式**：
```
安装 → 直接用 → 不懂就问 → 边用边学
```

**核心机制**：`claude-code-guide` 内置工具
- Claude Code 有一个内置的 subtool 专门用来搜索官方文档
- 任何问题都能通过它找到答案

#### 2.2 实时演示：不懂就问（3-4 分钟）

**场景 1：完全不知道怎么用（1 分钟）**
```
用户输入: 我第一次用 Claude Code，怎么开始？

Claude 调用 claude-code-guide，然后回答:
欢迎！Claude Code 是一个高度代理化的 AI 编程助手。

快速开始：
1. 确保已安装：npm install -g @anthropic-ai/claude-code
2. 配置 API Key：claude config set api-key YOUR_KEY
3. 启动：claude
4. 开始对话！

基本操作：
- 直接输入你的问题或任务
- 按 Shift+Tab 两次进入 Plan Mode（重要！）
- 输入 /help 查看帮助
- 输入 /clear 清空上下文
```

**场景 2：不知道某个功能怎么用（1 分钟）**
```
用户输入: 我想回退到之前的某个对话，怎么做？

Claude 调用 claude-code-guide，然后回答:
可以使用 /resume 命令恢复之前的对话：

步骤：
1. 输入 /resume 查看最近的会话列表
2. 选择你想恢复的会话 ID
3. Claude 会恢复该会话的所有上下文

示例：
claude> /resume
会话列表：
  [1] 2026-01-11 22:30 - 实现 MyBatis SQL 格式化器
  [2] 2026-01-11 21:15 - 添加单元测试
  [3] 2026-01-11 20:00 - 项目初始化

claude> /resume 1
→ 已恢复会话 1
```

**场景 3：想知道快捷键（1 分钟）**
```
用户输入: 有哪些快捷键？

Claude 调用 claude-code-guide，然后回答:
Claude Code 核心快捷键：

快捷键              | 功能
--------------------|------------------
Shift+Tab (两次)    | 进入/退出 Plan Mode
Escape              | 中断当前操作
Ctrl+C              | 退出 Claude Code
Tab                 | 自动补全

Tips：
- Plan Mode 是最重要的功能！始终以 Plan Mode 开始复杂任务
- 按 Escape 可以随时中断 AI 的操作
```

**场景 4：想知道如何配置（1 分钟）**
```
用户输入: 如何设置默认模型？

Claude 调用 claude-code-guide，然后回答:
设置默认模型的方法：

方法 1：命令行设置
claude config set model claude-opus-4-5

方法 2：环境变量
export ANTHROPIC_MODEL=claude-opus-4-5

可用模型：
- claude-opus-4-5    （最强，但慢）
- claude-sonnet-4-5  （推荐，平衡）
- claude-haiku-4-5   （快速，适合简单任务）
```

#### 2.3 核心功能：Plan Mode（1.5 分钟）

**为什么 Plan Mode 最重要？**
> "Plan Mode 是专业开发者的秘密武器。它让 Claude 先探索、规划，而不是盲目写代码。"

**演示 Plan Mode**：
```
任务：我想创建一个简单的 HTTP 服务器

按下 Shift+Tab 两次，进入 Plan Mode

Claude 分析：
我需要先了解你的项目情况：
1. 这是什么类型的项目？（Web 服务、CLI 工具...）
2. 你希望使用什么框架？（Express、Fastify...）
3. 需要什么功能？（路由、中间件...）

让我先探索一下当前目录结构...
```

**展示 Claude 如何**：
1. 读取现有文件
2. 分析项目架构
3. 制定实施计划
4. 征求用户确认

#### 2.4 快速总结（0.5 分钟）
> "看到了吗？我不需要背诵文档。有问题直接问，Claude Code 会调用 claude-code-guide 搜索官方文档，然后给我答案。"

---

## 第三部分：自定义 Command - 把琐碎事情自动化（3-4 分钟）

### 目标
展示如何用自定义命令提高效率

### 内容结构

#### 3.1 为什么需要自定义 Command？（0.5 分钟）

**场景**：每次发布都要做这些事：
```bash
npm run test        # 运行测试
npm run lint        # 检查代码
npm run build       # 构建
git add .
git commit -m "..."
git push
```

**痛点**：重复、容易遗漏、容易出错

#### 3.2 创建自定义 Command（2 分钟）

**演示：创建发布命令**

```
用户输入: 我想创建一个发布命令，帮我自动完成测试、lint、构建、提交、推送

Claude 回答：
我来帮你创建一个自定义 skill！

步骤 1：创建 skill 文件
在项目根目录创建 .claude/skills/release.md

步骤 2：编写 skill 内容
```

**Skill 文件内容**：
```markdown
<!-- .claude/skills/release.md -->
# 发布项目

执行以下步骤：
1. 运行测试：npm test
2. 运行 lint：npm run lint
3. 构建项目：npm run build
4. 询问用户 commit 信息
5. git add .
6. git commit -m "用户输入的信息"
7. git push

如果任何步骤失败，停止执行并告知用户。
```

**使用**：
```
用户输入: /release

Claude 执行：
✓ 运行测试... 通过
✓ 运行 lint... 通过
✓ 构建项目... 完成
请输入 commit 信息: feat: 添加用户认证功能
✓ 提交代码
✓ 推送到远程

发布完成！
```

#### 3.3 更多实用示例（1 分钟）

**示例 1：代码审查命令**
```
/code-review
→ 检查代码风格
→ 检查安全问题
→ 检查性能问题
→ 给出改进建议
```

**示例 2：文档生成命令**
```
/gendocs
→ 扫描所有源文件
→ 提取函数和类定义
→ 生成 API 文档
→ 保存到 docs/api.md
```

**示例 3：数据库迁移命令**
```
/migrate create 添加用户表
→ 生成迁移文件
→ 创建表结构 SQL
→ 生成回滚脚本
```

#### 3.4 小结（0.5 分钟）
> "自定义 Command 让你把重复性工作自动化。创建一次，反复使用。"

---

## 第四部分：与 Cursor 等 IDE 联动（2-3 分钟）

### 目标
展示 Claude Code 如何与 IDE 配合使用

### 内容结构

#### 4.1 为什么要联动？（0.5 分钟）

**Claude Code 的优势**：
- 强大的 Plan Mode
- 更好的上下文管理
- 丰富的 MCP 插件生态

**IDE 的优势**：
- 可视化编辑
- 调试器
- 代码补全

**结论**：两者结合，威力最大！

#### 4.2 Cursor + Claude Code MCP（1.5 分钟）

**什么是 MCP？**
- MCP = Model Context Protocol（模型上下文协议）
- 让 AI 工具之间可以互相调用
- Claude Code 可以作为 MCP Server 被其他工具调用

**演示：在 Cursor 中调用 Claude Code**

```
场景：在 Cursor 中开发，需要规划一个复杂功能

步骤 1：在 Cursor 中打开 MCP 面板
步骤 2：选择 Claude Code MCP
步骤 3：输入任务

Cursor> @claude-code 帮我规划如何实现用户认证系统

Claude Code（通过 MCP）响应：
我来帮你规划用户认证系统的实现：

项目分析：
- 当前使用 Express + TypeScript
- 已有用户模型
- 使用 JWT 进行认证

实施计划：
1. 创建认证中间件
2. 实现登录/注册 API
3. 添加 Token 验证
4. 编写单元测试
...

[详细计划]
```

**实际开发流程**：
```
1. 在 Claude Code 中规划（Plan Mode）
2. Claude 生成代码框架
3. 在 Cursor 中可视化编辑
4. 遇到问题，回到 Claude Code 询问
5. 循环往复
```

#### 4.3 MyBatis Boost 的 MCP 应用（1 分钟）

**展示 MyBatis Boost 项目**：
```
MyBatis Boost 提供了一个 MCP Server

在 Cursor 中可以使用：
@mybatis-boost 生成代码
→ 输入 DDL
→ 自动生成 Java Mapper
→ 自动生成 XML 配置
→ 自动生成 Entity 类
```

**演示**：
```sql
-- 在 Cursor 中输入 DDL
CREATE TABLE user (
    id BIGINT PRIMARY KEY,
    username VARCHAR(50),
    email VARCHAR(100)
);

-- 调用 MCP
@mybatis-boost 根据这个 DDL 生成 MyBatis 代码

-- Cursor 中自动生成：
User.java
UserMapper.java
UserMapper.xml
```

#### 4.4 小结（0.5 分钟）
> "Claude Code 不是要替代你的 IDE，而是和 IDE 配合使用。规划在 Claude Code，编辑在 IDE，两者结合效率最高。"

---

## 第五部分：专业开发者的 AI 工作流（2-3 分钟）

### 目标
展示 AI 如何放大专业开发者的能力，而不是替代专业能力

### 内容结构

#### 3.1 成果展示：MyBatis Boost（1.5 分钟）

**快速过一遍项目成果**：
- **项目规模**: 99 个 TypeScript 文件，~24,000 行代码
- **测试覆盖**: 106+ 单元测试，15+ 集成测试全部通过
- **核心功能**: Java ↔ XML 双向导航、AI 代码生成、SQL 格式化器
- **开发方式**: 完全使用 Claude Code 开发

**关键展示点**（屏幕快速滚动 Git 历史）：
```
❯ git log --oneline | head -20
a1b2c3d fix: 修复多模块项目导航问题
d4e5f6g feat: 添加 MyBatis SQL 格式化器
h7i8j9k refactor: 重构 MCP Provider 架构
...
```

**核心观点**：
> "这个项目不是让 AI 替代我写代码，而是用我的专业能力 + AI 的执行能力。我是导演，AI 是演员。"

#### 3.2 为什么专业开发者更受益？（1.5 分钟）

**专业开发者的特质被 AI 放大**：

| 初级开发者 | 资深开发者 | AI 放大效果 |
|-----------|-----------|-----------|
| 不知道问什么 | 知道如何拆解任务 | 任务拆解能力 → AI 并行执行 |
| 看不出代码问题 | 快速识别问题 | 审查能力 → AI 迭代修正 |
| 浪费时间查 API | 知道原理即可 | 知识结构 → AI 补充细节 |
| 写完就算 | 考虑可维护性 | 架构思维 → AI 实现细节 |

**核心原则：小步快跑，逐步迭代**
```
传统方式: 写一大段代码 → 调试 → 修改 → 再调试
AI 辅助:    小功能 → 测试 → commit → 下一个小功能
           ↑ 每步都可回滚，风险可控
```

**Git Commit 作为游戏保存点**：
```bash
# 每个小功能完成后立即 commit
git commit -m "feat: 添加基础路由处理"
git commit -m "feat: 实现 SQLite 存储层"
git commit -m "feat: 添加搜索功能"
# 如果出问题，随时回滚到任意保存点
```

#### 3.3 小结（0.5 分钟）
> "专业开发者 + AI = 超级个体。不是 AI 让你变强，而是你的专业能力被 AI 放大了。"

---

## 第六部分：从零实战 - Go 聊天历史查看器（12-15 分钟）

### 目标
完整展示从零开始用 Go 开发项目的真实过程，体现小步迭代的工作流

### 项目需求
- **语言**: Go（假设你不熟悉 Go，展示跨语言能力）
- **功能**: 网页展示 Claude Code 聊天历史记录
- **存储**: SQLite 同步存储
- **搜索**: 分项目搜索、全局搜索、输入/输出过滤

### 内容结构

#### 4.1 Plan Mode - 任务拆解的艺术（2 分钟）

**按下 `Shift+Tab` 两次，进入 Plan Mode**

```
用户输入:
我想用 Go 开发一个聊天历史查看器。
功能需求：
1. 读取 Claude Code 的聊天历史 JSON 文件
2. 用 SQLite 存储一份副本
3. 提供 Web 界面展示
4. 支持分项目搜索、全局搜索
5. 可以筛选输入/输出消息

请帮我规划这个项目
```

**Claude 分析输出**（展示计划）：
```
# 项目结构建议
chat-history-viewer/
├── internal/
│   ├── models/      # 数据模型
│   ├── storage/     # SQLite 存储
│   ├── parser/      # JSON 解析
│   └── api/         # Web API
├── web/             # 前端界面
├── cmd/             # 命令行入口
└── go.mod

# 实现步骤（按优先级排序）
1. 搭建项目骨架和基础配置
2. 定义数据模型（Conversation, Message）
3. 实现 JSON 解析器
4. 实现 SQLite 存储层
5. 实现基础 Web API（列表、详情）
6. 实现搜索功能
7. 开发前端界面
```

**关键点展示**：
> "看到没有？资深开发者的优势是知道如何拆解任务。AI 给出了完整的实施路径，而我会一步步验证每一步。"

#### 4.2 第一步：项目骨架（1.5 分钟）

**小步迭代演示**：

```bash
# 步骤 1: 创建项目目录
mkdir chat-history-viewer && cd chat-history-viewer

# 步骤 2: 初始化 Go 模块
go mod init github.com/yourname/chat-history-viewer

# 步骤 3: 创建基础目录结构
mkdir -p internal/{models,storage,parser,api} web cmd
```

**立即 Commit**：
```bash
git add .
git commit -m "chore: 初始化项目骨架"
```

> "每完成一个独立的小步骤，立即 commit。这就是专业开发者的习惯。"

#### 4.3 第二步：定义数据模型（2 分钟）

**Plan Mode 分析**：
```
我需要定义 Conversation 和 Message 模型。
Claude Code 的聊天历史格式是 JSON，包含：
- conversations: 对话列表
- messages: 每个对话的消息列表
- 每个 message 有 role (user/assistant) 和 content
```

**AI 生成模型代码**：
```go
// internal/models/conversation.go
package models

type Conversation struct {
    ID        string    `json:"id" db:"id"`
    Title     string    `json:"title" db:"title"`
    Project   string    `json:"project" db:"project"`
    CreatedAt time.Time `json:"created_at" db:"created_at"`
    UpdatedAt time.Time `json:"updated_at" db:"updated_at"`
    Messages  []Message `json:"messages"`
}

type Message struct {
    ID             string        `json:"id" db:"id"`
    ConversationID string        `json:"conversation_id" db:"conversation_id"`
    Role           string        `json:"role" db:"role"` // user, assistant
    Content        string        `json:"content" db:"content"`
    Timestamp      time.Time     `json:"timestamp" db:"timestamp"`
    ToolCalls      []ToolCall    `json:"tool_calls,omitempty"`
}
```

**人类审查**（展示人在循环）：
> "AI 生成了基础结构。我看到它考虑了 SQLite 的 db tag，这很好。但我需要补充一些字段..."
```go
// 添加索引和搜索相关的字段
type Conversation struct {
    // ... 现有字段
    MessageCount int    `json:"message_count" db:"message_count"` // 用于搜索排序
}
```

**立即 Commit**：
```bash
git commit -m "feat: 定义 Conversation 和 Message 数据模型"
```

#### 4.4 第三步：JSON 解析器（2 分钟）

**Plan Mode 分析**：
```
Claude Code 的聊天历史存储在 ~/.claude/conversations/*.json
每个 JSON 文件包含完整的对话信息
我需要：1. 读取所有 JSON 文件 2. 解析为模型 3. 返回切片
```

**AI 生成 + 人类审查**：
```go
// internal/parser/json_parser.go
package parser

import (
    "encoding/json"
    "os"
    "path/filepath"
    "github.com/yourname/chat-history-viewer/internal/models"
)

type Parser struct {
    conversationsDir string
}

func NewParser(dir string) *Parser {
    return &Parser{conversationsDir: dir}
}

func (p *Parser) ParseAll() ([]models.Conversation, error) {
    var conversations []models.Conversation

    files, err := filepath.Glob(filepath.Join(p.conversationsDir, "*.json"))
    if err != nil {
        return nil, err
    }

    for _, file := range files {
        data, err := os.ReadFile(file)
        if err != nil {
            continue // 跳过无法读取的文件
        }

        var conv models.Conversation
        if err := json.Unmarshal(data, &conv); err != nil {
            continue // 跳过无法解析的文件
        }

        conversations = append(conversations, conv)
    }

    return conversations, nil
}
```

**人类审查发现的问题**：
> "AI 的代码能工作，但有两个问题需要改进：
> 1. 没有并发处理，大量文件会很慢
> 2. 错误处理只是跳过，没有日志"

**改进后立即测试**：
```bash
# 编译测试
go build ./...

# 运行简单测试
go test ./internal/parser -v
```

**Commit**：
```bash
git commit -m "feat: 实现 JSON 解析器，支持读取 Claude Code 聊天历史"
```

#### 4.5 第四步：SQLite 存储层（2.5 分钟）

**Plan Mode 分析**：
```
我需要实现 SQLite 存储层：
1. 创建数据库表（conversations, messages）
2. 插入/更新对话和消息
3. 支持搜索查询
4. 使用 github.com/mattn/go-sqlite3
```

**AI 生成数据库初始化**：
```go
// internal/storage/sqlite.go
package storage

import (
    "database/sql"
    "time"
    _ "github.com/mattn/go-sqlite3"
)

type SQLiteStorage struct {
    db *sql.DB
}

func NewSQLiteStorage(dbPath string) (*SQLiteStorage, error) {
    db, err := sql.Open("sqlite3", dbPath)
    if err != nil {
        return nil, err
    }

    storage := &SQLiteStorage{db: db}
    if err := storage.initTables(); err != nil {
        return nil, err
    }

    return storage, nil
}

func (s *SQLiteStorage) initTables() error {
    schema := `
    CREATE TABLE IF NOT EXISTS conversations (
        id TEXT PRIMARY KEY,
        title TEXT,
        project TEXT,
        created_at DATETIME,
        updated_at DATETIME,
        message_count INTEGER DEFAULT 0
    );

    CREATE TABLE IF NOT EXISTS messages (
        id TEXT PRIMARY KEY,
        conversation_id TEXT,
        role TEXT,
        content TEXT,
        timestamp DATETIME,
        FOREIGN KEY (conversation_id) REFERENCES conversations(id)
    );

    CREATE INDEX IF NOT EXISTS idx_messages_conversation ON messages(conversation_id);
    CREATE INDEX IF NOT EXISTS idx_messages_role ON messages(role);
    CREATE VIRTUAL TABLE IF NOT EXISTS messages_fts USING fts5(content, role);
    `

    _, err := s.db.Exec(schema)
    return err
}
```

**人类审查亮点**：
> "AI 做得很好！它自动添加了：
> 1. 外键约束
> 2. 索引优化查询性能
> 3. FTS5 全文搜索支持
>
> 这就是专业能力 + AI 的价值：我知道需要索引，AI 帮我写 SQL。"

**实现搜索功能**：
```go
func (s *SQLiteStorage) Search(query string, project string, role string) ([]models.Conversation, error) {
    sql := `
        SELECT DISTINCT c.* FROM conversations c
        JOIN messages m ON c.id = m.conversation_id
        WHERE m.content LIKE ?
    `
    args := []interface{}{"%" + query + "%"}

    if project != "" {
        sql += " AND c.project = ?"
        args = append(args, project)
    }

    if role != "" {
        sql += " AND m.role = ?"
        args = append(args, role)
    }

    rows, err := s.db.Query(sql, args...)
    // ... 解析结果
}
```

**Commit**：
```bash
git commit -m "feat: 实现 SQLite 存储层，支持全文搜索和项目过滤"
```

#### 4.6 第五步：Web API（1.5 分钟）

**快速实现基础 API**：
```go
// internal/api/server.go
package api

import (
    "encoding/json"
    "net/http"
    "github.com/gin-gonic/gin"
)

type Server struct {
    storage *storage.SQLiteStorage
}

func NewServer(storage *storage.SQLiteStorage) *Server {
    return &Server{storage: storage}
}

func (s *Server) Start(port string) {
    r := gin.Default()

    // 静态文件服务
    r.Static("/static", "./web/dist")

    // API 路由
    api := r.Group("/api")
    {
        api.GET("/conversations", s.listConversations)
        api.GET("/conversations/:id", s.getConversation)
        api.GET("/search", s.search)
    }

    r.Run(":" + port)
}

func (s *Server) listConversations(c *gin.Context) {
    project := c.Query("project")
    conversations, err := s.storage.ListConversations(project)
    if err != nil {
        c.JSON(500, gin.H{"error": err.Error()})
        return
    }
    c.JSON(200, conversations)
}

func (s *Server) search(c *gin.Context) {
    query := c.Query("q")
    project := c.Query("project")
    role := c.Query("role")

    results, err := s.storage.Search(query, project, role)
    if err != nil {
        c.JSON(500, gin.H{"error": err.Error()})
        return
    }
    c.JSON(200, results)
}
```

**立即测试**：
```bash
# 启动服务器
go run cmd/server/main.go

# 测试 API
curl http://localhost:8080/api/conversations
curl "http://localhost:8080/api/search?q=mybatis"
```

**Commit**：
```bash
git commit -m "feat: 实现 Web API，支持对话列表和搜索"
```

#### 4.7 第六步：前端界面（1.5 分钟）

**简单展示 HTML/JS 界面**：
```html
<!-- web/dist/index.html -->
<!DOCTYPE html>
<html>
<head>
    <title>Chat History Viewer</title>
    <style>
        .search-box { padding: 10px; margin: 10px 0; }
        .conversation { border: 1px solid #ccc; margin: 10px 0; padding: 10px; }
        .message { padding: 5px; margin: 5px 0; }
        .message.user { background: #e3f2fd; }
        .message.assistant { background: #f5f5f5; }
    </style>
</head>
<body>
    <h1>Claude Code Chat History</h1>

    <div class="search-box">
        <input type="text" id="searchInput" placeholder="搜索消息...">
        <select id="projectFilter">
            <option value="">所有项目</option>
        </select>
        <button onclick="search()">搜索</button>
    </div>

    <div id="results"></div>

    <script>
        async function loadConversations() {
            const response = await fetch('/api/conversations');
            const conversations = await response.json();
            displayConversations(conversations);
        }

        async function search() {
            const query = document.getElementById('searchInput').value;
            const project = document.getElementById('projectFilter').value;
            const response = await fetch(`/api/search?q=${query}&project=${project}`);
            const results = await response.json();
            displayConversations(results);
        }

        function displayConversations(conversations) {
            const container = document.getElementById('results');
            container.innerHTML = conversations.map(conv => `
                <div class="conversation">
                    <h3>${conv.title}</h3>
                    <p>项目: ${conv.project} | 消息数: ${conv.message_count}</p>
                    <div class="messages">
                        ${conv.messages.map(msg => `
                            <div class="message ${msg.role}">
                                <strong>${msg.role}:</strong>
                                <p>${msg.content.substring(0, 100)}...</p>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `).join('');
        }

        loadConversations();
    </script>
</body>
</html>
```

**Commit**：
```bash
git commit -m "feat: 添加前端界面，支持搜索和过滤"
```

#### 4.8 回顾 Git 历史（1 分钟）

**展示完整的提交历史**：
```bash
git log --oneline --graph --all
* feat: 添加前端界面，支持搜索和过滤
* feat: 实现 Web API，支持对话列表和搜索
* feat: 实现 SQLite 存储层，支持全文搜索和项目过滤
* feat: 实现 JSON 解析器，支持读取 Claude Code 聊天历史
* feat: 定义 Conversation 和 Message 数据模型
* chore: 初始化项目骨架
```

> "看到这个 commit 历史了吗？每个 commit 都是一个独立的功能，随时可以回滚。这就是小步迭代的威力。"

**总结这个项目的开发过程**：
```
总耗时: 约 15-20 分钟
总代码: 约 500 行（Go + HTML）
总 commit: 6 次
平均每步: 2-3 分钟 + 1 次 commit
风险: 极低（每步都可验证、可回滚）
```

#### 4.9 小结（0.5 分钟）
> "即使你不熟悉 Go，只要理解编程原理，AI 就能帮你实现。而专业开发者的价值在于：
> 1. 知道如何拆解任务
> 2. 能够审查 AI 生成的代码
> 3. 保持小步迭代、频繁提交的习惯
> 4. 随时可以回滚、修改、重构"

---

## 第七部分：学习方式的颠覆（3-4 分钟）

### 目标
展示 AI 工具如何彻底改变学习编程的方式

### 内容结构

#### 5.1 从刚才的 Go 项目说起（1 分钟）

**回顾刚才的演示**：
> "刚才我用 Go 开发了一个完整的项目。但你知道吗？我对 Go 的了解非常有限。"
> "但这不影响，因为我理解编程原理，AI 帮我补充了语法细节。"

**关键洞察**：
- **不需要背诵语法** - AI 随时提供
- **不需要死记框架** - 知道原理即可
- **不需要查阅文档** - Claude + Context7 实时获取

#### 5.2 三大工具组合（1 分钟）

**Claude Code + Context7 + WebSearch**

| 工具 | 作用 |
|------|------|
| **Claude Code** | 代码生成、架构设计、问题解决 |
| **Context7** (MCP) | 获取任意框架的最新文档 |
| **WebSearch** | 实时信息获取、最新动态 |

**演示：学习新框架**
```bash
# 想学习 Rust 的 Axum 框架
claude> @context7 rust axum 如何创建路由和中间件？
# Context7 会自动获取最新的 Axum 文档

# 让 Claude 解释概念
claude> 解释一下 Axum 的 State 和 Extension 有什么区别？
```

#### 5.3 学习方式的范式转移（1.5 分钟）

**古法学习路径**:
```
购买书籍 → 阅读文档 → 背诵 API → 练习项目 → 积累经验（数月/数年）
```

**AI 辅助学习路径**:
```
直接问 Claude → 边做边学 → 立即应用（数小时/数天）
```

**从"记忆"到"检索"**
- 古法: 记住 API、框架、最佳实践
- AI 辅助: 知道原理，随时检索

**从"个人经验"到"全人类知识"**
- 古法: 你的知识边界 = 你的解决边界
- AI 辅助: 站在全人类编程知识的肩膀上

#### 5.4 小结（0.5 分钟）
> "AI 时代的学习方式：不再需要背诵 API，而是理解原理、掌握工具、持续实践"

---

## 第六部分：为什么专业开发者更受益（2-3 分钟）

### 目标
总结 AI 辅助编程对专业开发者的价值

### 内容结构

#### 6.1 专业开发者的特质被放大（1.5 分钟）

**回顾刚才的演示，我们看到专业开发者的这些能力**：

| 能力 | 古法价值 | AI 放大后 |
|------|---------|----------|
| **任务拆解** | 让项目更可控 | AI 并行执行多个小任务 |
| **代码审查** | 发现潜在问题 | 快速迭代修正 |
| **架构思维** | 设计可维护系统 | AI 实现细节 |
| **知识结构** | 快速学习新技术 | AI 补充具体 API |
| **测试意识** | 保证代码质量 | AI 生成测试代码 |

**核心观点**：
> "AI 不是替代专业能力，而是放大专业能力。你越专业，AI 越强大。"

#### 6.2 小步快跑 + 频繁提交 = 风险可控（1 分钟）

**展示 Git 历史**：
```bash
git log --oneline --graph --all
* feat: 添加前端界面，支持搜索和过滤
* feat: 实现 Web API，支持对话列表和搜索
* feat: 实现 SQLite 存储层，支持全文搜索和项目过滤
* feat: 实现 JSON 解析器，支持读取 Claude Code 聊天历史
* feat: 定义 Conversation 和 Message 数据模型
* chore: 初始化项目骨架
```

**每个 commit 都是游戏保存点**：
```
传统开发: 写一大段 → 调试很久 → 不知道哪里出问题
AI 辅助:    小功能 → 测试 → commit → 下一个小功能
           ↑ 每步都可回滚，风险可控
```

#### 6.3 三个核心原则（0.5 分钟）

1. **Plan Mode 优先**
   > "始终以 Plan Mode 开始" — Boris Power (Claude Code 之父)

2. **人在循环中**
   > "AI 编码助手是倍增器，但人类工程师仍然是导演" — Addy Osmani

3. **小迭代 + 频繁提交**
   - 每个独立功能完成后立即 commit
   - 把 commit 当作游戏保存点

---

## 第七部分：行动号召（1-2 分钟）

### 目标
激励观众开始使用 Claude Code

### 内容结构

#### 7.1 立即开始（0.5 分钟）

**三步上手**：
```bash
# 1. 安装
npm install -g @anthropic-ai/claude-code

# 2. 配置
claude config set api-key YOUR_API_KEY

# 3. 开始
claude
# 按下 Shift+Tab 两次，进入 Plan Mode
```

#### 7.2 推荐学习路径（0.5 分钟）

**初级**：
- 从小项目开始
- 熟悉 Plan Mode
- 练习小步迭代

**中级**：
- 学习编写 CLAUDE.md
- 尝试 MCP 插件
- 跨语言实践

**高级**：
- 自定义 Skills
- 配置 Hooks
- 企业集成

#### 7.3 结尾金句（0.5-1 分钟）

> "古法编程注定被淘汰，不是因为程序员变懒了，而是因为 AI 让知识边界不再是问题。"
>
> "这不是人与 AI 的对抗，而是**会用 AI 的人**与**不会用 AI 的人**之间的竞争。"
>
> "记住：小步快跑，逐步迭代。每一步都 commit，让风险可控。"
>
> "你是导演，AI 是演员。专业能力被放大，而不是被替代。"

---

## 附录：遗漏内容补充

### A. 数据与权威性（可穿插在各部分）

**Claude Code 的实力证明**:
- 位列 AI 编程助手前三名
- Claude Opus 4.5 SWE-Bench Verified 80.9%
- 2025 vs 2024 性能提升 18%

**震撼事件**:
- 2025年8月2日：Anthropic 切断 OpenAI 访问
- 2025年8月7日：GPT-5 发布（仅差 5 天！）
- Google Principal Engineer 一天完成一年工作量

### B. 常见陷阱（可放在第五部分）

**AI 的局限性**:
- 幻觉问题（胡说八道）
- 上下文限制
- 安全风险（注入攻击）

**如何避免**:
- 人在循环：审查所有代码
- 测试：编写测试验证行为
- 小迭代：分步骤验证

### C. MCP 协议详解（进阶话题）

**参考资料**: https://young1lin.github.io/posts/mcp/

**什么是 MCP？**
- MCP = Model Context Protocol（模型上下文协议）
- 标准化 AI 平台之间的工具调用
- 基于 JSON-RPC 2.0 协议

**MCP 通信方式**:
1. **stdio** - 标准输入输出（本地开发）
2. **HTTP** - HTTP 服务器（远程调用）
3. **WebSocket** - 双向通信（实时交互）

**MCP 核心概念**:

**1. MCP Server（服务端）**
```python
# 提供 tools、resources、prompts
class MCPServer:
    def list_tools(self) -> List[Tool]:
        return [
            Tool(
                name="get_weather",
                description="获取天气信息",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "city": {"type": "string"}
                    }
                }
            )
        ]

    def call_tool(self, name: str, args: dict):
        if name == "get_weather":
            return get_weather_data(args["city"])
```

**2. MCP Client（客户端）**
```python
# 连接到 MCP Server
class MCPClient:
    def __init__(self, command: list):
        self.process = subprocess.Popen(command)

    def list_tools(self):
        return self.send_request({
            "jsonrpc": "2.0",
            "method": "tools/list",
            "id": 1
        })
```

**3. MCP Host（主机端）**
```python
# 管理多个 MCP Client
class MCPHost:
    def __init__(self):
        self.clients = []

    def add_client(self, client: MCPClient):
        self.clients.append(client)

    def get_all_tools(self):
        tools = []
        for client in self.clients:
            tools.extend(client.list_tools())
        return tools
```

**4. LLM 集成**
```python
# 将 MCP Tools 转换为 Function Calling
def mcp_to_function_calling(mcp_tools: List[Tool]):
    return [{
        "name": tool.name,
        "description": tool.description,
        "input_schema": tool.inputSchema
    } for tool in mcp_tools]
```

**实际应用场景**:
- Context7: 获取任意框架的最新文档
- Chrome DevTools MCP: 获取网页结构信息
- Database MCP: 执行数据库查询
- Filesystem MCP: 文件系统操作

**开发自己的 MCP Server**:
```bash
# 1. 创建 MCP Server 项目
npm create mcp-server my-mcp

# 2. 实现 tools、resources、prompts
# 3. 本地测试
mcp-client test ./my-mcp

# 4. 发布到 npm
npm publish
```

**后续可深入的内容**:
- MCP（Model Context Protocol）插件开发
- Skills 自定义命令
- Hooks 自动化工作流
- 企业级部署（CI/CD 集成）
- 多实例并行工作

---

## 视频脚本模板

### 通用结构（每个小节）

```
## [小节标题]

**引入**（30秒）
- 问题/痛点
- 数据/案例
- 本节预告

**讲解**（2-3分钟）
- 核心概念
- 技术原理
- 代码示例

**演示**（1-2分钟）
- 实际操作
- 录屏展示
- 结果验证

**小结**（30秒）
- 关键要点
- 金句/引用
- 下节预告
```

---

## 录制建议

### 准备工作
1. **环境配置**:
   - Claude Code CLI 已安装
   - API Key 已配置
   - Go 开发环境已安装（用于实战演示）
   - mybatis-boost 项目已克隆（用于成果展示）

2. **录屏工具**:
   - OBS Studio / Camtasia
   - 分辨率: 1920x1080
   - 字体大小: 适合观看

3. **演示脚本预演**:
   - Go 聊天历史查看器完整开发流程（最重要！）
   - 每个 demo 提前练习
   - 准备好备用方案（防止 API 调用失败）

**实战演示准备**:
- 准备一些 Claude Code 聊天历史 JSON 文件用于测试
- 确保 SQLite 驱动已安装
- 提前测试 Go 项目的各个步骤

### 录制技巧
1. **语速控制**: 适中，不要太快
2. **重点强调**: 用字幕/箭头突出关键操作
3. **出错处理**: 展示真实场景，包括调试过程
4. **时间控制**: 每部分严格控制时间

### 后期制作
1. **字幕**: 添加中文字幕
2. **进度指示**: 左上角显示当前章节
3. **代码高亮**: 放大关键代码片段
4. **背景音乐**: 轻音乐，不要干扰讲解

---

## 配套资源

### 文章
- `article-2026-coding-evolution.md` - 配套公众号文章

### 代码仓库
- `https://github.com/young1lin/mybatis-boost` - MyBatis Boost 项目
- `https://github.com/young1lin/cc-tutorial` - 本教程项目

### 用户网站（LLM 学习资源）
- [LLM 入门与学习资源推荐](https://young1lin.github.io/posts/llm-0/)
- [LLM 原理深入探索](https://young1lin.github.io/posts/llm-1/)
- [MCP 协议完整技术文档](https://young1lin.github.io/posts/mcp/)

### 参考资料
- [Claude Code: Best practices for agentic coding](https://www.anthropic.com/engineering/claude-code-best-practices)
- [My LLM coding workflow going into 2026](https://addyosmani.com/blog/ai-coding-workflow/)
- [Claude Code: A Highly Agentic Coding Assistant](https://www.deeplearning.ai/short-courses/claude-code-a-highly-agentic-coding-assistant/)

---

**版本**: 1.0.0
**创建时间**: 2026-01-11
**维护者**: cc-tutorial 项目
