# 90 分钟完整教程视频：大纲总纲

**版本**: 1.0.0
**面向受众**: 零基础开发者
**总时长**: 90 分钟
**逻辑主线**: 底层原理 → API 机制 → Prompt 工程 → 工具安装 → 核心功能 → 实战演示

---

## 时间戳总览

| # | 段落标题 | 开始 | 时长 | 标注 |
|---|----------|------|------|------|
| 1 | LLM 底层原理：AI 到底在做什么？ | 0:00 | 10 min | 开场核心 |
| 2 | API 通信 + Prompt 工程：跑一个请求，讲一个原理 | 0:10 | 18 min | 含 2x；演示↔原理交叉 |
| ↳ | **过渡段**：Claude Code 安装 + 首次运行 | 0:28 | 5 min | 2x 快进 |
| 3 | 核心快捷键 + Task/TODO + 分步骤执行 + 上下文管理 | 0:33 | 8 min | **新增 @引用/一对话一任务/compact** |
| 4 | Plan Mode：先想后做的革命 | 0:41 | 15 min | **最重要** |
| 5 | EPCC 工作流：探索 → 计划 → 编码 → 提交 | 0:56 | 9 min | |
| 6 | CLAUDE.md：项目说明书的正确写法 | 1:05 | 7 min | |
| 7 | 实战演示：真实项目任务（mybatis-boost）| 1:12 | 12 min | 综合高潮 |
| 8 | 生态圈速览 + 3 条原则 + 资源导航 | 1:24 | 6 min | 收尾 |
| | **合计** | | **90 min** | ✓ |

---

## 段落 1：LLM 底层原理 — AI 到底在做什么？

**时间戳**: 0:00 – 0:10（10 分钟）
**类型**: 讲解 + ASCII 图示
**源文件**: `docs/tutorial/module-06-llm-limitations/chapter-23-how-llms-work.md`（§23.1 LLM 的本质）

### 录制要点

1. **核心认知（3 min）**：在屏幕上显示以下 ASCII 图，逐行朗读讲解：
   ```
   LLM = "预测下一个 Token" 的概率函数

   Input:  "The quick brown fox jumps over the"
   Output: "dog" (概率最高的下一个词)

   它不是搜索引擎，不是数据库，不是有意识的智能体
   它是：基于统计学的模式匹配器
   ```

2. **上下文窗口（3 min）**：
   - 类比"短期记忆"：Claude 只能看到当前对话窗口内的内容
   - 超出窗口 = 真正"忘记"，不是假装
   - 这解释了为什么 `/clear` 很重要，为什么要用 CLAUDE.md

3. **为什么懂行的人效果更好（2 min）**：
   - 统计模式匹配：你给的上下文越准确，预测越精准
   - 程序员写注释 = 给 LLM 提供更好的模式匹配材料
   - 引出"提示词 = 程序"的概念

4. **过渡衔接（2 min）**：
   > "既然 LLM 靠 HTTP 请求工作，我们就去看一下真实的请求长什么样"

### 关键台词
> "LLM 不是在思考，它在做一件非常复杂的事：根据你给的上下文，预测最合适的下一个词。这个过程没有理解，但有模式。"

---

## 段落 2：API 通信 + Prompt 工程 — 跑一个请求，讲一个原理

**时间戳**: 0:10 – 0:28（18 分钟）
**类型**: 屏幕录制（HTTP demo）+ 原理讲解交叉
**源文件**: `docs/examples/http/02-limitations.http`、`05-prompt-engineering.http`、`06-parameter-experiments.http`
**节奏模式**: 每个 demo 结束立即讲原理，不积攒到最后
**2x 提示**: 等待 API 响应（1-2 秒）全程 2x，节约观众时间

### 引入：HTTP 就是 AI 的语言（1 min）

打开 VS Code，展示 `docs/examples/http/` 目录结构，解释：
> "我们接下来用最直接的方式和 AI 对话——HTTP 请求。这些 `.http` 文件就是原始的 API 调用，没有任何封装。你看懂了这个，就看懂了所有 AI 工具的底层。"

---

### Demo 1 → 原理 1：局限性 → LLM 是概率，不是计算器（3 min）

**Demo（1.5 min）**
**文件**: `docs/examples/http/02-limitations.http` → `[局限性 1.1]` 大数乘法

```http
POST https://api.stepfun.com/v1/chat/completions
{
  "messages": [{"role": "user", "content": "请计算：9876 × 5432 = ?"}],
  "model": "step-3.5-flash",
  "temperature": 0
}
```
- 运行请求，展示响应（正确答案是 53,646,432）
- 如果答错：画面定格，让观众看清错误

**原理讲解（1.5 min）**
```
为什么出错？

LLM 在做：P("53646432" | "9876 × 5432 = ")
不是在做：9876 × 5432 的数学运算

它看到过无数"小数字乘法"的训练数据，
但大数乘法在训练数据中少见 → 概率预测失准

结论：LLM 的"智能"是模式匹配，不是推理
      这就是为什么写代码要测试，不能只靠 AI 说对就信
```

---

### Demo 2 → 原理 2：Zero-Shot vs Few-Shot → 示例=上下文=模式引导（4 min）

**Demo（2 min）**
**文件**: `docs/examples/http/05-prompt-engineering.http` → `[提示词 1.1]` 和 `[提示词 1.2]`

- 先运行 `[提示词 1.1]` Zero-Shot：无示例情感分析
  - 展示响应：格式可能是自然语言、可能是 JSON，结果不统一
- 再运行 `[提示词 1.2]` 3-Shot：带 3 个示例
  - 展示响应：格式完全按示例输出，一致性飞跃

**原理讲解（2 min）**
```
为什么加了示例效果好这么多？

回想段落1：LLM = 预测下一个 Token
示例在做什么？—— 在上下文里展示了"期望的模式"

实际文件里的做法（更常见）：把示例内嵌进 system message
  system: "...示例 1：\n输入：好吃！服务棒。\n输出：正面（★★★★★）
               示例 2：\n输入：太差了。\n输出：负面（★☆☆☆☆）
               示例 3：\n输入：价格适中，味道还行。\n输出：中性（★★★☆☆）
           现在请分析以下评论："
  user:   "这家餐厅的环境不错，但菜品一般，价格有点贵。"
                                                           ← 模型接续这个模式

口诀：Zero-Shot 试了不行？加两个例子再试！
适合：格式要求严格、分类任务、统一代码风格
```

---

### Demo 2.5 → 原理 3：Chain-of-Thought — 让 AI 先想再答（3 min）

**Demo（1.5 min）**
**文件**: `docs/examples/http/05-prompt-engineering.http` → `[提示词 2.2]` 和 `[提示词 2.1]`

演示顺序（先看没有 CoT 的效果，再看有的）：
- 先运行 `[提示词 2.2]`（无提示词版）：直接问数学应用题 → 模型可能直接给答案，跳过推理
- 再运行 `[提示词 2.1]`（有 CoT 版）：加了 "让我们一步步思考" → 模型列出完整推理步骤，准确率提升

题目：`一个孩子存了 21 元，如果又得到 15 元，用这些钱可以买多少个单价 6 元的玩具？`

**原理讲解（1.5 min）**
```
为什么"列出步骤"会提升准确率？

Token 是线性生成的。
生成"步骤1"时，步骤1已写入上下文
生成"步骤2"时，能看到步骤1 → 减少跳跃式错误

触发词：
  "让我们一步步思考"（Let's think step by step）
  "请先列出思考步骤"
  "请一步一步分析"

适合：数学推理、代码 debug、多条件判断
注意：增加 Token 消耗，简单任务不需要
```

---

### Demo 3 → 原理 4：结构化输出 → 格式指令比自然语言稳定（4 min）

**Demo（2 min）**
**文件**: `docs/examples/http/05-prompt-engineering.http` → `[提示词 3.1]` 和 `[提示词 3.2]`

- 先运行 `[提示词 3.1]`（基础 JSON 提取）：只说"以 JSON 格式返回"
  - 响应：有 JSON，但字段不固定，可能缺 skills，可能多余字段
- 再运行 `[提示词 3.2]`（带 JSON Schema 约束）：提供完整 Schema 定义
  - 响应：字段完整（name/age/occupation/city/skills 全部正确），类型严格符合

**原理讲解（2 min）**
```
为什么要用 Schema 而不是自然语言说"返回 JSON"？

自然语言版：
  "请以 JSON 格式返回，包含 name, age, occupation, city 字段"
  → 模型可能：skills 字段不返回、age 返回字符串不是整数、多余字段

带 Schema 版：
  "请严格按照以下 JSON Schema 返回..."（附 required、type 约束）
  → 字段完整、类型正确、结构可预测、便于程序处理

这就是 CLAUDE.md 用 Markdown 写结构化指令的原因：
边界清晰的格式 > 模糊的自然语言描述
```

---

### Demo 4 → 小结：Temperature — 创意 vs 精确（2 min）[2x]

**Demo（1 min）**
**文件**: `docs/examples/http/06-parameter-experiments.http` → `[参数 1.1]`

- temperature=0：每次运行结果完全相同
- temperature=1：每次运行结果有变化

**小结（1 min）**
```
temperature 控制"随机性"：
  = 0 → 总是选概率最高的 Token → 确定性、适合代码生成
  = 1 → 引入随机采样 → 创意、适合头脑风暴

实践口诀：
  写代码 → temperature 0
  写文案 → temperature 0.7-1
```

---

### 速查：promptingguide.ai 的 5 条通用最佳实践（1 min，口播总结）

> 来源：https://www.promptingguide.ai/introduction/tips

```
1. 从简单开始，迭代加复杂
   先写最短的 prompt，看效果，再逐步加约束。不要一次写 100 行指令。

2. 用命令动词，不要用问句
   "Write / Classify / Summarize / Extract"
   比 "你能帮我..." 更精准。

3. 具体 > 模糊
   差："用简洁的语言解释这个"
   好："用 2-3 句话，向没有编程背景的人解释这个概念"

4. 正向表述（说要做什么，不说不要做什么）
   差："不要返回多余内容"
   好："只返回 JSON，不包含任何其他文字"

5. 用分隔符隔开指令和内容
   用 ### 或 <content>...</content> 把"指令"和"输入内容"分开，
   避免模型混淆边界。
```

---

### 过渡衔接（1 min）

> "我们用 4 个 HTTP 请求，走完了 Prompt 工程的核心：示例引导、步骤推理、结构约束、参数控制，外加 5 条通用原则。这些东西，就是让 AI 效果提升 5 倍的核心技巧。接下来装上 Claude Code，把这些知识用起来。"

---

## 过渡段：Claude Code 安装 + 首次运行 [2x 快进]

**时间戳**: 0:28 – 0:33（5 分钟，实际录制约 8-10 分钟后 2x）
**类型**: 屏幕录制，终端操作
**源文件**: `docs/tutorial/module-01-fundamentals/chapter-02-setup.md`

### 国内安装注意（口播，10 秒）

> ⚠️ 国内用户：请用 npm 方式安装，**不要用官网的原生安装脚本**
> 原因：原生安装不走代理，国内网络无法下载
>
> ```bash
> npm install -g @anthropic-ai/claude-code  ← 用这个
> ```
>
> 如果本地 Node.js 版本低于 22，先用 nvm 切换到最新版本再安装。

### 没有 Anthropic API Key？中转方案（口播，15 秒）

> 如果你有 Gemini Pro 订阅、Stepfun、ChatGPT 订阅，但没有 Anthropic API Key：
>
> 1. **Claude Code Router**：把 OpenAI 格式的接口转成 Anthropic 格式
>    → 支持 Stepfun、DeepSeek、GLM 等任意 OpenAI 兼容接口
> 2. **Gemini Pro / ChatGPT 订阅**：先通过 Claude Relay Service 获取 Access Token，再绑定
> 3. **Antigravity Tools**：Gemini Pro 订阅直接使用 Claude Opus 或 Gemini 3 Pro
>    → `https://github.com/lbjlaq/Antigravity-Manager`
>
> 核心思路：**模型质量对体验非常重要**，尽量用 Opus 级别模型。

### 录制步骤（仅保留必要操作）

```bash
# 步骤 1：安装 Claude Code（30 秒）
npm install -g @anthropic-ai/claude-code

# 步骤 2：配置 API Key（30 秒）
# 展示：访问 claude.ai/settings 获取 API Key（网站截图即可，不录实际操作）
export ANTHROPIC_API_KEY="sk-ant-..."

# 步骤 3：首次运行（1 min）
claude

# 步骤 4：/init 初始化项目（2 min）[重点演示]
> /init
# 展示 Claude 自动分析项目结构并生成 CLAUDE.md
```

### IDE 联动（口播，15 秒）

> 安装好 Claude Code 后，在 VS Code / IDEA / Cursor 中安装 Claude Code 插件。
> 终端输入 `/config`，搜索 IDE，打开 **Auto-Connect to IDE**。
> 打开后，在 IDE 中选中代码 → 终端自动显示 "xx lines selected"，可以直接对选中的代码提问。
> 如果没有显示，输入 `/ide` 确认连接状态，或重启 IDE。

### 允许所有权限（口播警告，10 秒）

> ⚠️ 开发环境可以用 `claude --dangerously-skip-permissions` 跳过确认弹窗，提高效率。
> **生产环境绝对不要用！** 如果 Fetch 的网页有提示词注入，可能触发危险命令。
> 更细粒度的控制：在 `.claude/settings.json` 中配置 `permissions.allow` 和 `permissions.deny`。

### 录制提示
- 安装命令等待时间全程 2x
- `/init` 这一步放慢速度，这是观众第一次看到 Claude Code 工作
- 强调：Claude 在读取项目后自动提问了解上下文

---

## 段落 3：核心快捷键 + Task/TODO + 分步骤执行 + 上下文管理

**时间戳**: 0:33 – 0:41（8 分钟）
**类型**: 屏幕录制，简单对话演示
**源文件**: `docs/tutorial/module-01-fundamentals/chapter-03-shortcuts.md` + `docs/tutorial/module-02-core-workflows/`

### 核心内容（七件事）

#### 快捷键速查（1.5 min）

| 快捷键 / 命令 | 作用 | 备注 |
|--------------|------|------|
| `Shift+Tab` | 切换 Plan Mode | 多文件/复杂任务前 **必用** |
| `Escape` | 中断当前操作 / 退出应用 | 中断一次；无输入时再按退出 |
| `!` | 进入 bash 模式 | 对话框首字符输入 `!`，直接执行 shell 命令 |
| `@` | 文件引用 | 精准引用文件进上下文，减少一次工具调用 |
| `Alt+V` | 粘贴截图 | 给 Claude 看界面截图（⚠️ 见下方多模态说明） |
| `Ctrl+C` | 清除当前输入 | 再次按 → 退出应用 |
| `Ctrl+O` | 展开全部内容 | 折叠内容太长时用 |
| `Ctrl+T` | 显示 TODO 列表 | 查看当前任务清单 |
| `Shift+?` | 显示所有快捷键 | **输入框第一个字符按**，不是全局快捷键 |
| `/clear` | 清空上下文 | 切换任务时用 |
| `/compact` | 压缩上下文为摘要 | 同一任务进行到一半时用 |
| `/rewind` | 退回到指定轮次 | ⚠️ 后面的对话永久丢失，慎用 |
| `/resume` | 恢复上次对话 | 重启终端后继续工作 |
| `/model` | 切换模型 | 对话中在 Opus / Sonnet 间切换 |
| `/cost` | 查看 Token 消耗和费用 | 监控花费，避免超预算 |
| `Ctrl+A` | 全选粘贴网页内容 | Claude 无法 fetch 的页面（Reddit 等），手动粘贴 |
| `Ctrl+B` | 后台运行长命令 | 不阻塞对话，稍后自动检查结果 |
| `think` | 深度思考关键词 | 对话中说 "think" / "think harder" / "ultrathink" |

**Alt+V 多模态兼容性说明（口播，10 秒）：**
```
原生多模态（Claude Opus、GPT-4o、Gemini）：Alt+V 截图直接分析 ✅
非原生多模态（StepFun、DeepSeek、GLM）：可能不支持，需复制文字代替截图 ⚠️

替代方案：错误信息复制文字、UI 问题用 Figma MCP 获取结构化信息
```

**深度思考关键词（口播，15 秒）：**
```
在 prompt 中加入特定关键词，触发 Claude 更深层的推理：
  "think"        → 正常深度思考
  "think harder"  → 更深层推理
  "ultrathink"   → 最深层推理（消耗更多 Token，但复杂问题准确率飙升）

适合：复杂架构决策、多条件 debug、难以复现的 bug
不需要：简单的代码修改、格式调整
```

#### `@` 文件引用（1 min）
```
在对话框里输入 @ → 弹出文件搜索框 → 选择文件 → 引用进上下文

比"帮我读一下 src/auth/login.ts"更精准，减少一次工具调用。
Claude 不需要先搜索文件再读取，直接拿到内容。

用法示例：
  @ src/auth/login.ts 这个函数有什么问题？
  @ package.json 我需要添加哪些依赖？
```

#### 一个对话只做一件事（1.5 min）
```
LLM 的上下文窗口有限。混入多个任务会导致：
- 上下文污染：任务 A 的代码和任务 B 的错误信息混在一起
- 难以回溯：想 /rewind 回退时不知道该回退哪一步
- Token 浪费：不相关的内容占用宝贵的窗口空间

❌ 错误方式：
  "帮我修 bug，顺便优化查询，还有更新文档"

✅ 正确方式：
  对话 1："修复登录 Token 过期问题" → 完成 → /clear
  对话 2："优化用户列表查询" → 完成 → /clear
  对话 3："更新 README 安装说明"

何时 /clear：
  · 任务完成后（功能完成、测试通过、已提交）
  · 切换领域时（后端切前端、业务逻辑切 UI）
  · 上下文变杂时（Claude 开始"忘事"或回答混乱）
  · 踩坑后重来（方案走错了，换方向重新开始）
```

#### `/compact` vs `/clear`（0.5 min）
```
/compact：压缩当前对话为摘要（同一任务做到一半时用）
          保留关键信息（文件路径、决策、代码变更），丢弃细节
          Claude 接近上下文上限时也会自动触发

/clear：清空所有上下文，从零开始（切换任务时用）

区别：
  /compact → 保留记忆，继续同一任务
  /clear   → 彻底清空，开始新任务
```

#### `/rewind` 和 `/resume`（1 min）
```
/resume：恢复上次对话（换了终端或重启后继续工作）

/rewind：退回到指定轮次
  ⚠️ 注意：后面的对话内容会被永久丢弃！
  例：U1→A1→U2→A2→U3，rewind 到 U2 → A2 和 U3 永久消失

口诀：/resume 是"续"，/rewind 是"悔棋"——慎用
配合 git commit，代码 + 对话都能回退
```

#### TodoWrite：自动任务清单（1.5 min）
```
Claude Code 内置 TodoWrite 工具：
- 接到复杂任务后，Claude 会自动创建 TODO 清单
- 清单展示在对话中，勾选完成的步骤
- 你可以说"先做第 1 步，完成后告诉我"

演示：
  给 Claude 一个多步骤任务 → 看它自动生成并管理 TODO
```

#### 分步骤技巧（1 min）
```
关键技巧：不要一次给 Claude 所有任务！

❌ 错误方式：
  "帮我重构整个项目，添加测试，更新文档，修复所有 bug"

✅ 正确方式：
  第 1 步："先帮我分析项目结构，列出需要重构的文件"
  确认后再说："好，现在重构第一个文件"
  再确认再说："现在写测试"
```

---

## 段落 4：Plan Mode — 先想后做的革命（最重要）

**时间戳**: 0:41 – 0:56（15 分钟）
**类型**: 完整屏幕录制演示
**源文件**: `docs/tutorial/module-01-fundamentals/chapter-04-plan-mode.md`
**重要性**: 这是 Claude Code 的核心心智模型，是视频高潮

### 结构（15 分钟完整演示）

#### 什么是 Plan Mode（2 min）
- **问题引入**: AI 直接执行 vs 先规划再执行的对比（用一个真实 bug 案例）
- **定义**: Plan Mode = Claude 只能思考和规划，不能修改文件
- **触发方式**: 两次 `Shift+Tab`（演示键盘操作），或直接输入 `/plan` 命令（v2.1.0+）
- 引用 Boris Power（Claude Code 之父）：
  > "Always start with Plan Mode" —— 多文件/多步骤任务，先规划

#### 实操演示（10 min）

**演示任务**：为一个已有的 TypeScript 项目添加日志功能

```
步骤 1：激活 Plan Mode（Shift+Tab 两次）
  → 界面变化：底部显示 "Plan Mode" 指示
  → Claude 变成"只读模式"

步骤 2：描述需求
  > "我需要为这个项目添加结构化日志功能，
     要支持不同日志级别，输出到文件和控制台"

步骤 3：审查 Claude 的计划
  → Claude 列出：
    - 将修改哪些文件（不超过 5 个）
    - 每步做什么
    - 潜在风险点
  → 画面放大显示计划内容，逐条朗读

步骤 4：调整计划（关键！）
  > "第 3 步不需要，我们不改 config 文件"
  → Claude 更新计划
  → 展示：你掌握控制权，AI 服从你的判断

步骤 5：执行
  → 退出 Plan Mode（再次 Shift+Tab）
  → Claude 开始执行，屏幕显示文件变更
  → 展示：执行与计划完全一致，无意外
```

#### 何时用 Plan Mode（3 min）

```
必用场景：
✅ 修改 3 个以上文件
✅ 不熟悉的代码库
✅ 重要功能（删除、重构）
✅ 对话上下文超过 50 轮

可以跳过：
⬜ 写一个新函数
⬜ 修复明确的单行 bug
⬜ 添加注释
```

### 关键台词
> "Plan Mode 改变了我和 AI 协作的方式。不是让 AI 直接干活，而是让它先告诉我它打算怎么干。我看了觉得 OK，再让它执行。这才是人在主导。"

---

## 段落 5：EPCC 工作流 — 探索 → 计划 → 编码 → 提交

**时间戳**: 0:56 – 1:05（9 分钟）
**类型**: 讲解 + 快速演示
**源文件**: `docs/tutorial/module-02-core-workflows/chapter-05-explore-plan-code-commit.md`

### 四步流程讲解（6 min）

```
┌─────────────────────────────────────────────────────────┐
│                   EPCC 工作流                            │
├────────────┬────────────┬────────────┬───────────────────┤
│  Explore   │   Plan     │   Code     │     Commit        │
│  探索       │   计划     │   编码     │     提交          │
├────────────┼────────────┼────────────┼───────────────────┤
│ 读代码      │ Plan Mode  │ 小步迭代   │ git add/commit    │
│ 找相关文件  │ 讨论方案   │ 测试验证   │ 有意义的 msg      │
│ 理解上下文  │ 确认边界   │ 及时修正   │ 每步都提交        │
└────────────┴────────────┴────────────┴───────────────────┘
```

**探索（1.5 min）**：
- 用 Claude 读项目：`"先阅读项目结构，告诉我这个项目是做什么的"`
- 找相关文件：`"找到所有处理用户认证的文件"`

**计划（1.5 min）**：
- 即段落 5 的 Plan Mode，简要回顾
- 强调：计划 = 合同，执行时不应该超出计划范围

**编码（1.5 min）**：
- 小步迭代：每次改 1-2 个文件，确认后再继续
- 遇到错误立即停：`"先把测试跑起来，有 red 测试就先修"`
- **Feedback Loop（Boris 的 #1 建议）**：
  ```
  永远给 Claude 一种验证自己工作的方法！

  如果 Claude 能看到自己代码的运行结果（报错信息、测试通过/失败），
  代码质量提升 2-3 倍。

  ✅ "写完后运行测试，把结果贴给我看"
  ✅ "在浏览器里打开，截图给我"
  ✅ "运行这个命令，看输出是否符合预期"
  ❌ 让 Claude 写完就完，不验证

  验证 prompt 金句：
  "Double check everything you produced,
   make a table of what you were able to verify"
  ```

**提交（1.5 min）**：
```
提交 = 游戏存档点（不是可选项，是必选项）

节奏：
  写代码 → 测试通过 → git commit → 继续下一步
  写代码 → 测试通过 → git commit → 继续下一步
  ...

好处：
  Claude 写崩了？git checkout . 一键回到上个存档点
  配合 /rewind，代码 + 对话都能同时回退

口诀：每完成一个功能点就提交，
      不要让 AI 一口气改十个文件再提交
```
- Claude 可以帮写 commit message：直接说"提交当前变更"或用 `/commit` 命令

### TDD 一句话带过（1 min）
```
TDD 和 Claude Code 的天然配合：

1. 先让 Claude 写测试（描述期望行为）
2. 运行 → 全部 RED（正常，还没写实现）
3. 让 Claude 写实现，直到全绿
4. 提交

口诀：测试先行，改到绿灯
```

### 最后 2.5 min：完整流程串联演示
快速展示一个 EPCC 完整循环（不超过 2 分钟，用之前的演示素材剪辑）

---

## 段落 6：CLAUDE.md — 项目说明书的正确写法

**时间戳**: 1:05 – 1:12（7 分钟）
**类型**: 屏幕录制，文件对比演示
**源文件**: `docs/tutorial/module-08-building-workflows/chapter-31-claude-md-template.md`

### 结构

#### 问题引入（1.5 min）
```
场景：你有个项目，第一次用 Claude Code：

无 CLAUDE.md 的对话：
  你：帮我添加一个用户注册功能
  Claude：用什么框架？数据库用什么？密码加密方式？
           有没有现有的认证模块？代码风格要求？...
  → 要回答 5-8 个问题，浪费上下文

有 CLAUDE.md 的对话：
  你：帮我添加一个用户注册功能
  Claude：好的，基于你的 Express + PostgreSQL + bcrypt 配置，
           我会在 src/auth/ 目录下创建...
  → 直接开干
```

#### CLAUDE.md 最简结构（3 min）
```markdown
# 项目名称

## 技术栈
- 语言：TypeScript
- 框架：Express.js
- 数据库：PostgreSQL + TypeORM
- 测试：Jest + Supertest

## 项目结构
src/
├── routes/     # HTTP 路由
├── services/   # 业务逻辑
├── models/     # 数据模型
└── tests/      # 测试文件

## 代码规范
- 使用 async/await，不用回调
- 所有函数需要 JSDoc 注释
- 错误处理用 Result 类型

## 常用命令
- 运行测试：npm test
- 启动开发服务：npm run dev
- 数据库迁移：npm run migrate
```

#### 对比演示（2.5 min）
- 打开本项目的 `CLAUDE.md`
- 展示：Claude Code 启动后自动读取了这个文件
- 演示：`"这个项目的技术栈是什么？"` → Claude 直接回答，无需探索

#### CLAUDE.md 的三个层级（0.5 min）
```
层级覆盖系统（后加载的优先级更高）：

| 层级 | 位置                      | 用途           | 提交 git？ |
|------|--------------------------|---------------|-----------|
| 用户 | ~/.claude/CLAUDE.md       | 个人全局偏好   | 否         |
| 项目 | <项目根>/CLAUDE.md        | 团队共享规则   | 是         |
| 本地 | .claude/CLAUDE.local.md   | 本地覆盖       | 否         |

例：项目级写"用 PostgreSQL"，本地级写"我的端口是 5433"
```

#### 三个核心原则（口播，15 秒）
1. **保持更新**：改了技术栈就改 CLAUDE.md
2. **够用就好**：不需要写 100 行，关键信息 20-30 行足够
3. **像对待代码一样对待 CLAUDE.md**：提交到 git，团队一起维护

#### Context Engineering — 上下文工程（1 min）
```
Addy Osmani 称之为 Context Engineering（上下文工程）：
不是写更多 Prompt，而是精心设计 Claude 能看到什么。

上下文来源优先级：
  CLAUDE.md（常驻）→ MCP（按需）→ @引用（精准）→ 对话（临时）

每一层都有它的位置：
- CLAUDE.md：每次对话自动加载，放不变的项目基础信息
- MCP：只在需要时拉取外部数据（Figma、数据库、文档）
- @ 引用：精准指定当前任务涉及的文件
- 对话本身：临时的、任务相关的上下文

一条推论：你的代码质量 = Claude 的输出质量
  代码模块化差、层次不清 → Claude 读不懂 → 输出烂
  相反：清晰的分层、有意义的命名 → Claude 输出质量飞跃

Vibe Coding vs Spec Coding：
  ❌ Vibe Coding：纯靠 AI，不给明确指令，"帮我随便写一个"
  ✅ Spec Coding：清晰写出需求、约束、实现方式，AI 按规格执行

  你的专业能力决定了 AI 辅助的上限。
  普通人 + Opus = Opus 的分数
  专家 + Opus = 超越 Opus 的分数（因为专家能避开幻觉）
```

> 💡 **英文提示词效果更好**：LLM 训练数据主要是英文，
> 同一个需求用英文描述，输出质量明显提升（编程场景尤其明显）。
> 能用英文就用英文，包括写 SubAgent 的 description 字段。

---

## 段落 7：实战演示 — 真实项目任务（mybatis-boost）

**时间戳**: 1:12 – 1:24（12 分钟）
**类型**: 屏幕录制，完整开发任务演示
**源文件**:
- `docs/tutorial/module-04-real-world-mybatis-boost/chapter-14-project-overview.md`（3 min）
- `docs/tutorial/module-04-real-world-mybatis-boost/chapter-15-cst-vs-regex.md`（9 min）

### 结构

#### 项目介绍（3 min）
**源文件**: `chapter-14-project-overview.md`

```
mybatis-boost：VS Code 插件，用于格式化 MyBatis SQL

特点：
- TypeScript 编写，500+ 行核心代码
- 有真实的 CST 解析器（不是简单的正则）
- 有完整测试套件
- 有 CLAUDE.md（用这个项目来示范！）

展示：打开项目，简要介绍目录结构（30 秒）
      打开 CLAUDE.md，展示项目的 AI 说明书（1 min）
      展示已有的测试（证明这是真实项目）（1.5 min）
```

#### 实战任务：添加一个新的 SQL 格式化规则（9 min）
**源文件**: `chapter-15-cst-vs-regex.md`（CST 解析是核心技术亮点）

**任务描述**（给观众看）：
> "为 MyBatis SQL formatter 添加对 CASE...WHEN 语句的格式化支持"

**完整演示（三剑合璧）**：

```
第 1 步：Explore（1 min）
  Claude：帮我理解项目中 SQL 格式化是怎么实现的
  → Claude 读代码，解释 CST 解析流程
  → 指出需要修改哪个文件

第 2 步：Plan Mode（2 min）[Shift+Tab]
  Claude：我需要添加 CASE...WHEN 格式化支持
  → Claude 生成计划：
    1. 在 MybatisSqlFormatter.ts 中添加 CASE 节点处理
    2. 在 formatter.test.ts 中添加测试用例
    3. 更新 README（可选，我们跳过）
  → 调整：确认只做前两步

第 3 步：Code（4 min）
  → 退出 Plan Mode，Claude 开始实现
  → 展示实际代码变更（diff 视图）
  → Claude 遵循了项目现有的代码风格（因为有 CLAUDE.md）
  → 运行测试：全绿！

第 4 步：Commit（1 min）
  > /commit
  → Claude 自动生成有意义的 commit message
  → git log 展示结果
```

#### 关键亮点（1 min）
- CLAUDE.md 让 Claude 直接遵循项目规范
- Plan Mode 防止了意外修改
- 整个过程：10 分钟完成一个真实功能，测试通过，代码质量高

---

## 段落 8：生态圈速览 + 3 条原则 + 资源导航（收尾）

**时间戳**: 1:24 – 1:30（6 分钟）
**类型**: 幻灯片 + 屏幕截图展示
**源文件**: `docs/examples/recommended-plugins/README.md` + `docs/research/`

### 生态圈速览（2.5 min）

#### MCP（Model Context Protocol）（1 min）
```
MCP = 让 Claude Code 连接外部工具的标准协议

当你说：帮我查一下 Jira 上的这个 ticket
Claude 通过 MCP → 真正读取 Jira API → 给你答案

不是 Claude 知道答案，而是 Claude 能调用工具拿到答案
```
**源文件**: `docs/tutorial/module-03-advanced-features/chapter-10-mcp.md`

#### Memory + claude-mem（30 秒）
```
Claude Code 自带记忆系统：
  ~/.claude/projects/<项目>/memory/MEMORY.md
  → Claude 工作中自动记录有价值的发现（踩过的坑、有效的方案）
  → 下次对话自动加载，避免重复犯错
  → 注意：MEMORY.md 是 Claude 写给自己的笔记，CLAUDE.md 是你写给 Claude 的指令

claude-mem MCP 插件：更强的跨对话记忆持久化
  → 安装后 Claude 记住你的代码风格偏好、常用框架
```
**源文件**: `docs/examples/recommended-plugins/claude-mem.md`

#### repomix（30 秒）
```
场景：需要把整个项目给 Claude 分析
工具：repomix 把项目打包成一个 AI 友好的文本文件

npx repomix  →  生成 project-summary.txt  →  给 Claude 读
```
**源文件**: `docs/examples/recommended-plugins/repomix.md`

#### 减少工具调用 / 减少上下文占用的三个工具（0.5 min）
```
上下文窗口是有限的，以下工具让每一个 Token 都有价值：

- LSP 插件：3000 行文件只读 400 行相关代码
  （需要对应语言的 LSP 插件：Java、Go、TypeScript 均有支持）

- SubAgent：复杂任务拆给独立 Agent，不污染主对话上下文
  SubAgent 有自己的上下文窗口，干完活返回结果，主对话保持干净

- claude-mem（已提到）：跨对话记忆持久化，避免每次重新解释项目背景
```

#### Headless 用法（15 秒）
```
Claude Code 不只是交互式终端，还能当命令行工具用：

  claude -p "分析这段代码的安全问题"      ← 单次提问，无交互
  claude -c -p "我上一句说的什么？"        ← 继续上次对话
  claude -p --agent code-analyzer "..."   ← 指定 Agent 执行

实际用途：
  · 配合 Git Hook → 每次提交自动 Code Review
  · 配合 CI/CD → 自动分析 PR 变更
  · 批处理脚本 → 批量分析多个文件
```

#### Git Worktrees 并行开发（15 秒）
```
Claude Code 团队的"最大生产力解锁"：

  git worktree add ../project-feature-a feature-a
  git worktree add ../project-feature-b feature-b

每个 worktree = 独立目录 → 开一个 Claude 会话 → 互不干扰
比单纯开多个终端强：每个会话有自己的 git 分支，不会冲突
```

#### 自定义 Commands（15 秒）
```
.claude/commands/ 目录下创建 Markdown 文件 = 自定义斜杠命令

例：.claude/commands/bug-report.md
    内容写 prompt 模板 → 对话中输入 /bug-report 即可复用

常见自定义命令：
  /bug-report   → 标准化 bug 分析流程
  /code-review  → 统一的代码审查清单
  /feature-spec → 功能需求模板
```

#### 插件生态提示（0.5 min）
```
更多工具：docs/examples/recommended-plugins/README.md

推荐入门套件：
- claude-mem    → 记忆持久化
- repomix       → 代码库打包
- code-review   → PR 代码审查
- firecrawl     → 网页抓取
```

### 3 条核心原则（2 min）

**原则 1：Plan Mode 优先**（Boris Power，Claude Code 之父）
> "始终以 Plan Mode 开始复杂任务" ——
> 多文件修改？Plan Mode。不熟悉的代码库？Plan Mode。
> 习惯先计划，再执行。

**原则 2：人在主导，AI 放大**（Addy Osmani，Google Chrome 工程师）
> "AI 是倍增器，不是替代者"——
> 必须审查所有 AI 生成的代码。
> AI 放大你的专业知识，但你对代码质量负责。

**原则 3：LLM 会出错，你要会发现**（本视频核心）
> 回到段落 1 的教训：LLM 是概率函数，不是权威答案。
> 用它加速，但不要盲目信任。

**⚠️ 数据安全提醒**（口播，10 秒）
> 非企业版 / 非 Max 用户的对话数据**可能被用于模型训练**（Anthropic 和国内厂商均如此）。
> 不要在对话中暴露 API Key、数据库密码等敏感信息，能用环境变量就别直接写。
> 企业对数据安全有极高要求 → 内网部署开源模型（如 StepFun-3.5-Flash）。

### 资源导航（2 min）

```
延伸学习（视频描述区有链接）：

进阶主题（已有完整文档）：
  docs/tutorial/module-03-advanced-features/   → Hooks、Skills 自定义
  docs/tutorial/module-05-architecture/        → 整洁架构、测试设计
  docs/tutorial/module-09-advanced-topics/     → CI/CD 集成
  docs/tutorial/module-11-git-mastery/         → Git 并行工作流

快速参考：
  docs/tutorial/module-10-reference/chapter-37-command-cheatsheet.md → 命令速查
  docs/tutorial/module-10-reference/chapter-38-troubleshooting.md    → 故障排除

研究来源：
  docs/research/01-claude-code-best-practices-anthropic-official.md  → Boris Cherny 最佳实践
  docs/research/04-addy-osmani-2026-workflow.md                      → Addy Osmani 2026 工作流
```

### 结束语
> "LLM 是工具，你是工程师。用好这个工具的核心是：理解它的工作原理，掌握它的局限，然后在这个边界内最大化它的价值。从今天开始，先装上 Claude Code，然后试试 Plan Mode。"

---

## 附录 A：降级内容的延伸学习导航

这些内容因视频时长限制被删减，但作为完整参考文档保留：

| 主题 | 文档位置 | 适合人群 |
|------|----------|---------|
| TDD 完整实践 | `module-02/chapter-06-tdd.md` | 想用 AI 做测试驱动开发 |
| 多实例并行工作 | `module-02/chapter-07-multi-instance.md` | 大型项目、多任务并行 |
| Hooks 自定义 | `module-03/chapter-12-hooks.md` | 想自动化工作流的开发者 |
| Skills 编写 | `module-03/chapter-11-skills.md` | 想创建自定义命令 |
| 整洁架构 + LLM | `module-05/` | 做架构设计的高级开发者 |
| CI/CD 集成 | `module-09/chapter-34-cicd-pipelines.md` | DevOps 场景 |
| 企业级集成 | `module-09/chapter-35-enterprise-integration.md` | 企业团队 |
| Git 并行工作流 | `module-11/chapter-45-parallel-development.md` | 需要多分支并行 |
| 快速参考卡 | `module-10/chapter-37-command-cheatsheet.md` | 日常查阅 |

---

## 附录 B：录制检查清单

在录制每个段落前，确认：

- [ ] 终端字体大小 ≥ 18px（观众看得清）
- [ ] 关闭通知（系统通知弹窗会穿帮）
- [ ] `.env` 文件中有有效 API Key（HTTP 演示需要）
- [ ] 提前确认 REST Client 插件已安装（VS Code）
- [ ] mybatis-boost 项目已克隆到本地（段落 8 需要）
- [ ] 段落标注 `[2x]` 的部分，实际录制可稍慢，后期处理加速

### 2x 快进位置汇总
1. 过渡段（安装）：`npm install` 等待过程
2. 过渡段（安装）：API Key 配置网站截图部分（直接跳过浏览器操作）
3. 段落 2（HTTP 演示）：每次 API 请求的等待时间（1-2 秒）
4. 段落 2（HTTP 演示）：temperature 实验的等待时间

---

## 附录 C：关键引言备用

| 引言 | 来源 | 推荐用在 |
|------|------|---------|
| "始终以 Plan Mode 开始" | Boris Power（Claude Code 之父） | 段落 5 开头 |
| "AI 是倍增器，不是替代者" | Addy Osmani（Google） | 收尾原则 2 |
| "先做小事，验证后再继续" | Boris Cherny（Claude Code 最佳实践文档） | 段落 6 EPCC |
| "你对代码质量负责，AI 是工具" | Andrew Ng（AI 先驱） | 收尾原则 2 |

**引言来源文档**：
- `docs/research/01-claude-code-best-practices-anthropic-official.md`
- `docs/research/04-addy-osmani-2026-workflow.md`
- `docs/research/05-boris-cherny-workflow-x-thread.md`
