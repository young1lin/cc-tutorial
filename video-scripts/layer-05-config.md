# 第五层：项目配置体系

## Claude Code 配置目录结构

Claude Code 的配置采用三级覆盖系统（前面讲的 CLAUDE.md 和 Rules 的层级就来自这里）：

**用户级别** (`~/.claude/`)：
```
~/.claude/
├── CLAUDE.md                    # 用户全局 CLAUDE.md
├── rules/                       # 用户全局 Rules
├── settings.json                # 全局设置（模型、权限等）
├── plugins/                     # 已安装的插件
├── agents/                      # 用户自定义 Agent
└── projects/<project>/memory/   # 各项目的记忆文件
```

**项目级别** (`.claude/`)：
```
<项目根目录>/.claude/
├── settings.json                # 项目级别设置
├── agents/                      # 项目专用 Agent
├── commands/                    # 项目自定义命令
└── skills/                      # 项目专用 Skills
```

**本地级别** (`.claude/*.local.*`)：
- `settings.local.json`、`CLAUDE.local.md`、`rules.local.*` 等
- 这些文件优先级最高，但**不应提交到 git**（加入 `.gitignore`）
- 用于本地环境特有的配置（如本地数据库端口、API 密钥等）

## settings.json 主要可配置项

在 `~/.claude/settings.json`（全局）或 `.claude/settings.json`（项目）中可配置：

| 字段 | 类型 | 说明 |
|------|------|------|
| `model` | string | 默认模型（`"sonnet"` / `"opus"` / `"haiku"`） |
| `cleanupPeriodDays` | number | 会话历史保留天数（默认 30，设大值避免清理） |
| `permissions.defaultMode` | string | `"default"` / `"bypassPermissions"` / `"plan"` |
| `permissions.allow` / `deny` | array | 细粒度工具白/黑名单 |
| `statusLine` | object | 状态栏插件配置（`type: "command"`，`command: "路径"`） |
| `hooks` | object | 生命周期 Hook 配置（见第六层） |

不是每个字段都要配，只填你需要改的。

## .gitignore 规范

项目根 `.gitignore` 应包含：

```gitignore
# Claude Code 本地配置（含个人 API Key 路径、本地 statusLine 等）
.claude/*.local.*
.claude/CLAUDE.local.md

# 环境变量（绝对不提交）
**/.env
```

项目级 `CLAUDE.md` 和 `settings.json`（不含敏感信息的）应提交到 git，供团队共享。

## Rules

Rules 和 CLAUDE.md 文件本质相同，每次对话都会加载到 System Prompt。区别在于：CLAUDE.md 偏向项目信息（"这是什么项目、怎么构建"），Rules 偏向行为约束和编码规范（"拒绝蓝紫色主题"、"所有函数必须有 JSDoc 注释"）。

**Rules 的三个层级（和 CLAUDE.md 一样）：**

| 层级 | 位置 | 用途 |
|------|------|------|
| **用户级别** | `~/.claude/rules/` | 你个人的全局编码偏好 |
| **项目级别** | `.cursor/rules` 或项目根目录 | 团队共同遵守的规则（提交到 git） |
| **本地级别** | `.claude/rules/*.local.*` | 本地覆盖规则（不提交） |

**从哪找现成的 Rules 模板：**

Cursor 官方和社区维护了大量现成的 Rules 模板，覆盖各种技术栈和场景：

- **Cursor Directory**：[cursor.directory](https://cursor.directory/) - 官方推荐的 Rules 和 MCP 服务器目录，按框架和语言分类
- **awesome-cursorrules**：[GitHub](https://github.com/PatrickJS/awesome-cursorrules) - 社区维护的配置文件集合
- **cursorrules.org**：专门的 Rules 模板站，可以直接复制粘贴

**典型 Rules 内容示例：**

```markdown
# 代码风格
- 使用 TypeScript strict 模式
- 组件优先使用函数式而非 class
- 错误处理使用 Result 类型而非异常

# 禁止
- 不要使用 any 类型
- 不要使用蓝紫色主题
- 提交前必须运行 `bun test`

# 命名规范
- React 组件用 PascalCase
- 工具函数用 camelCase
- 常量用 UPPER_SNAKE_CASE
```

**2026 年新增：** Cursor 在 v0.43+ 加入了 `/rules` CLI 命令，可以直接在终端创建和编辑 Rules，不需要手动打开文件。

## Memory —— 跨对话持久记忆

Claude Code 有一个自动记忆系统。每个项目有独立的记忆目录：

```
~/.claude/projects/<project>/memory/
├── MEMORY.md          # 主记忆文件，每次对话自动加载到 System Prompt
├── debugging.md       # 按主题组织的详细笔记
├── patterns.md        # 项目模式和约定
└── ...
```

**MEMORY.md 和 CLAUDE.md 的区别：**

- **CLAUDE.md**：你写给 Claude 的指令（"项目用什么技术栈、怎么构建"）
- **MEMORY.md**：Claude 写给自己的笔记（"上次调试发现 XX 模块有 YY 问题、ZZ 方法有效"）

**工作方式：** Claude 在工作过程中会自动记录有价值的发现——比如踩过的坑、有效的解决方案、项目特有的模式。下次对话时，这些记忆会被加载，避免重复犯错。

**注意事项：**
- MEMORY.md 超过 200 行会被截断，保持精简
- 按主题拆分成多个文件（debugging.md、patterns.md），从 MEMORY.md 中链接过去
- 如果发现记忆中的内容过时了，可以手动编辑或让 Claude 更新

## 自定义 Commands —— 可复用的 Prompt 模板

除了 Skills，Claude Code 还有一个更轻量的复用机制：**自定义 Commands**。在 `.claude/commands/` 目录下创建 Markdown 文件，文件名就是命令名，内容就是 prompt 模板。

```
.claude/commands/
├── bug-report.md      → 对话中输入 /bug-report 触发
├── code-review.md     → 对话中输入 /code-review 触发
├── feature-spec.md    → 对话中输入 /feature-spec 触发
└── refactor.md        → 对话中输入 /refactor 触发
```

**示例：`.claude/commands/bug-report.md`**

```markdown
请分析以下 Bug：

1. 先复现问题：阅读相关代码，找到可能的 root cause
2. 列出所有相关文件和函数调用链
3. 给出修复方案（至少 2 个备选）
4. 评估每个方案的风险和影响范围
5. 推荐最佳方案并说明理由

分析完成后，运行相关测试确认修复有效。
```

对话中输入 `/bug-report` 就会自动加载这个模板，然后你只需要补充具体的 Bug 描述就行。

**Commands 和 Skills 的区别：**

- **Commands**（`.claude/commands/`）：轻量级，就是一个 prompt 模板文件，输入 `/命令名` 触发。适合固定的工作流模板。
- **Skills**（`.claude/skills/`）：重量级，有元信息（SKILL.md）、示例代码（examples/）、可以关联 SubAgent。适合需要参考样例、有复杂触发条件的场景。

两者也分为用户级别（`~/.claude/commands/`）和项目级别（`.claude/commands/`），和 CLAUDE.md 的层级逻辑一致。

**实用建议：** 先从 Commands 开始，把你经常重复的 prompt 抽成模板。如果发现模板不够用（需要示例代码、需要 SubAgent 配合），再升级成 Skills。

## Context Engineering —— 上下文工程

前面讲了那么多概念——CLAUDE.md、MCP、Skills、SubAgent、LSP、Rules——它们本质上都在解决同一个问题：**让 200k Token 的上下文窗口里，装的全是有用的信息**。

这就是 Addy Osmani 提出的 Context Engineering（上下文工程）。不是写更多的 Prompt，而是**精心设计 Claude 能看到什么**。

**上下文的来源：**

| 来源 | 什么时候加载 | 作用 |
|------|------------|------|
| CLAUDE.md | 每次对话自动加载 | 项目基础信息，永远在场 |
| Rules | 每次对话自动加载 | 行为约束 |
| MCP | 工具调用时按需加载 | 外部数据（数据库、Figma、API 文档等） |
| Skills | 匹配到场景时按需加载 | 专业能力（代码风格、测试模式等） |
| SubAgent | 被主 Agent 调用时独立运行 | 拆分复杂任务，避免主上下文膨胀 |
| LSP | 代码跳转时精准加载 | 只读相关代码，不读整个文件 |
| Memory | 每次对话自动加载 MEMORY.md | 跨对话经验积累 |

**核心原则：按需加载，避免浪费。** 一个复杂的重构任务，拆成 SubAgent 各自处理，不会把主对话的上下文撑爆。Figma 的设计稿信息，只在 Plan Mode 探索阶段通过 MCP 拉取，不会常驻上下文。LSP 的精准代码加载能力，详见第六层的 `/plugin` 章节。

**一句话总结：** 你的上下文质量决定了 AI 的输出质量。垃圾进，垃圾出。
