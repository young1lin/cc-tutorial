# tooling 项目工具配置 Overview

> last_verified_commit: 3cf4d89
> source_paths: .claude/commands/, .claude/rules/, .claude/agents/

## 快速索引

- slash 命令: `/commit-push`
- 规则: `evidence-based`, `voice-and-tone`
- agents: `business-logic-researcher`

## 领域概述

本项目通过 `.claude/` 下的三个目录为 Claude Code 会话注入自定义行为：**命令**自动化重复操作流程，**规则**强制内容质量标准，**agent** 封装可复用的分析能力。三者共同构成教程项目的"工具基座"，确保每次会话的输出风格一致、事实可追溯、研究流程标准化。

## 子领域

| 类别 | 文件 | 作用 |
|------|------|------|
| slash 命令 | `.claude/commands/commit-push.md` | 一键暂存、生成 conventional commit、推送到远端，自动排除调试文件和编译产物 |
| 规则 | `.claude/rules/evidence-based.md` | 四级证据体系(T1-T4)，强制每个事实声明可追溯，禁止无来源断言 |
| 规则 | `.claude/rules/voice-and-tone.md` | 冷峻分析文风——禁止 AI 填充词、要求短句硬判断、去伪中立 |
| agent | `.claude/agents/business-logic-researcher.md` | 只读代码分析 agent，将代码行为映射为业务逻辑文档并同步 markdown 知识文件 |

## 内容地图

### slash 命令 (`/commit-push`)

- 变更分析: `git status --porcelain` + `git diff --stat`
- 文件过滤: 排除 `debug*.json`、`*.exe`、`*.dll`、`*.log`、`.DS_Store`、`Thumbs.db`、`*.tmp`、`*.swp`、`node_modules/`、`__pycache__/`、`*.pyc`
- 提交格式: `<type>(<scope>): <description>`，尾部附 `Co-Authored-By` 署名
- 署名规则: 按终端区分——Claude Code 用 `<Model Name> <noreply@anthropic.com>`，Codex 用 `<Model Name> (Codex)`，不跨厂商伪造
- 错误处理: 任何步骤失败即停止，不继续执行后续步骤

### 规则 (`evidence-based`)

- 四级证据体系: T1(官方一手)、T2(专家实践)、T3(社区共识，至少两个独立来源)、T4(教程解读)
- 强声明规则: 含 `best`/`fastest`/`only`/`always`/`never` 等词的断言必须 T1 或 T2 支撑，否则降级为 T4
- 预测规则: 所有前瞻性声明一律 T4
- 冲突规则: 专家意见不一致时必须双面呈现，再给出教程立场
- 标记: 非事实内容须用 `**[Tutorial perspective]**` 或 `**[Author's analysis]**` 显式标记
- 研究工作流: 新来源写 `research/NN-descriptive-name.md`(含 YAML front matter)并更新 `research/00-research-summary.md` 索引

### 规则 (`voice-and-tone`)

- 核心要求: 分析师文风，禁用 `imagine`、`needless to say`、`it is worth noting` 等 AI 填充词
- 句式: 短句为主，长句只在承载技术重量时使用
- 判断: 明确表态，不用 `suboptimal`/`challenging` 等模糊弱化词
- 隐喻: 只在有实际论证功能时使用，不用方括号解释隐喻
- 边界条件: 冷峻文风不豁免证据要求，T4 标记照常

### agent (`business-logic-researcher`)

- 用途: 分析代码库中的业务流程，将代码行为同步为业务逻辑 markdown 文档
- 工具集: Read, Grep, Glob, Bash, Edit, Write(只写知识文件)
- 模型: sonnet
- 关联 skill: `business-logic`
- 工作流: 先读路由规则 → 加载相关领域文件 → 对照代码验证 → 更新过时文档 → 记录假设

## 关键文件

| 文件 | 角色 |
|------|------|
| `.claude/commands/commit-push.md` | Git 工作流自动化入口 |
| `.claude/rules/evidence-based.md` | 事实质量门禁——全仓库生效的硬规则 |
| `.claude/rules/voice-and-tone.md` | 文风门禁——全仓库生效的硬规则 |
| `.claude/agents/business-logic-researcher.md` | 业务逻辑分析 agent 定义 |

## 检索锚点

- `/commit-push` — slash 命令名
- `evidence-based` — 证据规则文件名
- `voice-and-tone` — 文风规则文件名
- `business-logic-researcher` — agent 名称
- `T1`/`T2`/`T3`/`T4` — 证据等级标识符
- `Co-Authored-By` — 提交署名尾部标记
- `conventional commits` — 提交消息格式
- `**[Tutorial perspective]**` — T4 非事实内容标记
- `**[Author's analysis]**` — T4 作者分析标记

## 潜在坑点 / 注意

- `voice-and-tone` 规则与 `evidence-based` 规则叠加生效: 冷峻文风不降低证据门槛，T4 标记在任何文风下都强制
- `/commit-push` 的署名规则区分 Claude Code 和 Codex 两种终端，跨终端会话混用署名格式会导致 git log 中的身份伪造
- `business-logic-researcher` agent 有 Edit 和 Write 权限，但它只应修改 `.claude/skills/business-logic/` 下的知识文件，不应触碰源码
- 两条规则文件的内容也通过 `CLAUDE.md` 中的引用被注入到每次会话的 system prompt，修改任一规则影响全仓库的 Claude Code 行为

## 相关文档

- `CLAUDE.md` — 项目顶层指令，引用了 evidence-based 和 voice-and-tone 两条规则
- `research/00-research-summary.md` — 证据规则要求维护的研究索引文件
- `examples/` — 示例代码目录，`/commit-push` 可能涉及的提交范围
