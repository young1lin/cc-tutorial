# Chapter 3: 核心快捷键和基本用法

**模块**: Module 1 - 入门基础
**预计阅读时间**: 12 分钟
**难度**: ⭐

---

## 学习目标

本章结束后，你将能够：

- [ ] 掌握 Claude Code 的核心快捷键
- [ ] 理解基本命令的使用场景
- [ ] 学会如何有效地与 Claude Code 交互
- [ ] 了解上下文管理技巧

---

## 前置知识

- [ ] 已完成 Chapter 2 - 安装与配置
- [ ] Claude Code CLI 已安装并可运行

---

## 核心快捷键概览

### 最常用的快捷键

| 快捷键 | 功能 | 重要性 |
|--------|------|--------|
| `Shift+Tab` | 切换 Plan Mode | ⭐⭐⭐⭐⭐ |
| `Alt+V` | 粘贴图片 | ⭐⭐⭐⭐ |
| `Escape` | 中断当前操作 | ⭐⭐⭐⭐ |
| `Escape Escape` | 跳回历史记录 | ⭐⭐⭐ |
| `Ctrl+C` / `Ctrl+D` | 退出 Claude Code | ⭐⭐⭐ |

---

## 快捷键详解

### 1. Shift+Tab - Plan Mode 切换

**功能**: 在 Plan Mode 和正常执行模式之间切换

**为什么这是最重要的快捷键？**

> **"始终以 Plan Mode 开始"** - Boris Power (Claude Code 之父)

Plan Mode 让 Claude 先规划再执行，是获得高质量结果的关键。

**使用方法**:

```
# 第一次按 Shift+Tab
> 进入 Plan Mode
Claude 将只制定计划，不执行任何修改操作

# 第二次按 Shift+Tab
> 退出 Plan Mode
Claude 将可以执行修改操作
```

**何时使用**:
- ✅ 多文件修改任务
- ✅ 不熟悉的代码库
- ✅ 复杂功能实现
- ✅ 需要理解现有代码

**何时不使用**:
- ❌ 快速的单词拼写修正
- ❌ 简单的代码格式化
- ❌ 已非常熟悉的小改动

**详细讲解**: 见 [Chapter 4 - Plan Mode 革命](chapter-04-plan-mode.md)

---

### 2. Alt+V - 粘贴图片

**功能**: 从剪贴板粘贴图片到对话中

**使用场景**:

1. **设计稿参考**
   ```
   粘贴 UI 设计稿 → 让 Claude 实现相应的界面
   ```

2. **错误截图**
   ```
   粘贴错误信息截图 → 让 Claude 分析问题
   ```

3. **架构图**
   ```
   粘贴系统架构图 → 让 Claude 理解系统结构
   ```

4. **视觉对比**
   ```
   粘贴期望效果截图 → 让 Claude 调整代码实现
   ```

**使用方法**:

```
# Windows: 截图到剪贴板
Win+Shift+S (选择区域)

# macOS: 截图到剪贴板
Cmd+Ctrl+Shift+4 (选择区域)

# 然后在 Claude Code 中
按 Alt+V (粘贴图片)

# 或者直接拖放图片文件
```

**示例对话**:

```
你: [按 Alt+V 粘贴设计稿]

请实现这个登录页面的 HTML 和 CSS。

Claude Code: 我将根据这个设计稿创建登录页面。

让我分析一下设计元素：
- 居中的登录表单
- 蓝色主题色
- 邮箱和密码输入框
- "登录" 按钮
- "忘记密码" 链接

[生成代码...]
```

**注意事项**:
- 图片会被自动分析
- Claude 可以识别 UI 元素、文字、颜色等
- 支持常见图片格式（PNG、JPG、WebP）

---

### 3. Escape - 中断操作

**功能**: 立即停止 Claude Code 当前正在执行的操作

**使用场景**:

1. **Claude 误解了意图**
   ```
   Claude 开始修改错误的文件
   → 按 Escape 立即停止
   → 重新澄清需求
   ```

2. **操作时间过长**
   ```
   Claude 正在进行耗时的操作
   → 按 Escape 中断
   → 调整策略
   ```

3. **意识到不该这样做**
   ```
   Claude 准备删除文件
   → 按 Escape 停止
   → 检查是否正确
   ```

**使用方法**:

```
Claude 正在执行操作...
[按 Escape]

操作已中断。

你可以：
1. 修改指令后继续
2. 让 Claude 撤销更改
3. 使用 /clear 清空上下文重新开始
```

**技巧**: 可以在工具调用的任何阶段中断，不会破坏已完成的操作

---

### 4. Escape Escape - 跳回历史记录

**功能**: 快速返回到对话历史的某个位置并重新编辑提示词

**使用场景**:

1. **想尝试不同的方法**
   ```
   之前的实现不够好
   → 双击 Escape 回到那个提示
   → 修改提示词
   → 重新发送
   ```

2. **Claude 之前的回答更好**
   ```
   新的实现有 bug
   → 双击 Escape 回到之前的版本
   → 让 Claude 重新实现
   ```

**使用方法**:

```
[双击 Escape - 快速按两次 Escape]

对话历史将显示在终端中
↑/↓ 箭头选择历史位置
Enter 跳转到该位置

可以编辑提示词后重新发送
```

---

### 5. Ctrl+C / Ctrl+D - 退出

**功能**: 优雅地退出 Claude Code

**使用方法**:

```
# Ctrl+C 或 Ctrl+D
> 你确定要退出吗？(y/n)
y

感谢使用 Claude Code！再见！👋
```

**区别**:
- `Ctrl+C`: 可以中断，确认后退出
- `Ctrl+D`: 直接退出（EOF）

---

## 基本命令

### 斜杠命令概览

| 命令 | 功能 | 示例 |
|------|------|------|
| `/help` | 显示帮助信息 | `/help` |
| `/clear` | 清空对话上下文 | `/clear` |
| `/init` | 初始化项目配置 | `/init` |
| `/permissions` | 管理权限 | `/permissions allow Edit` |
| `/mode` | 切换模式 | `/mode plan` |
| `/tasks` | 查看任务列表 | `/tasks` |

---

### /help - 帮助命令

**功能**: 显示可用命令和帮助信息

```
> /help

Claude Code 命令帮助：

基本命令:
  /help          显示此帮助信息
  /clear         清空对话上下文
  /exit          退出 Claude Code

项目管理:
  /init          初始化项目配置
  /permissions   管理权限设置
  /mode          切换权限模式

高级功能:
  /tasks         查看当前任务列表
  /compact       压缩上下文

更多信息请访问: https://claude.ai/code
```

---

### /clear - 清空上下文

**功能**: 清空当前的对话历史，释放 token 并重新开始

**何时使用**:

1. **切换到完全不同的任务**
   ```
   刚完成了用户认证功能
   → 现在要做数据导出功能
   → 使用 /clear 清空上下文
   → 开始新任务
   ```

2. **上下文过于混乱**
   ```
   对话过长，Claude 开始"忘记"之前的内容
   → 使用 /clear 重新开始
   ```

3. **想要全新的开始**
   ```
   之前的探索方向不对
   → 使用 /clear
   → 重新描述需求
   ```

**使用方法**:

```
> /clear

上下文已清空。
对话历史将被保留，但不会发送给 Claude。

你现在可以开始一个新的对话。
```

**注意**: `/clear` 不会清除终端显示的历史，只是不再将其发送给后续的请求

---

### /init - 初始化项目

**功能**: 分析项目并生成初始配置

```
> /init

正在分析项目...

发现:
- React 项目
- TypeScript
- 使用 ESLint 和 Prettier

创建以下文件:
✓ .claude/settings.json
✓ CLAUDE.md

已配置:
- TypeScript 支持
- 常用命令
- 项目结构说明
```

---

### /permissions - 权限管理

**功能**: 管理工具权限

```
> /permissions

当前权限设置:
- 默认模式: ask
- 允许的工具: Read, Bash(ls,cat)

可用操作:
- /permissions allow <tool>     允许工具
- /permissions deny <tool>      拒绝工具
- /permissions defaultMode <mode>  设置默认模式

模式: ask | auto | bypassPermissions

> /permissions allow Edit
Edit 工具已添加到允许列表

> /permissions defaultMode auto
默认模式已设置为 auto
```

---

### /mode - 模式切换

**功能**: 快速切换权限模式

```
> /mode plan
已切换到 Plan Mode

> /mode auto
已切换到自动执行模式

> /mode ask
已切换到询问模式
```

---

## 对话技巧

### 1. 提供上下文

**DO（应该做的）**:
```
✅ 请阅读 src/api/user.ts 文件，然后添加一个删除用户的函数
✅ 这个项目的认证系统位于 src/auth/ 目录
✅ 参考现有的 login 函数来实现 logout
```

**DON'T（不应该做的）**:
```
❌ 添加一个删除用户的功能
❌ 实现 logout
```

### 2. 具体化指令

**DO**:
```
✅ 为 User 组件添加一个名为 "avatarUrl" 的 prop
✅ 创建一个 GET /api/users/:id 端点，返回 JSON 格式的用户数据
✅ 修复登录表单的验证问题，当邮箱为空时显示错误提示
```

**DON'T**:
```
❌ 添加头像功能
❌ 创建用户 API
❌ 修复登录表单
```

### 3. 分步骤执行

对于复杂任务，分解为小步骤：

```
> 请按以下步骤实现用户注册功能：

1. 创建注册页面组件
2. 实现表单验证
3. 创建注册 API 端点
4. 添加错误处理
5. 编写测试

先从步骤 1 开始。
```

### 4. 使用引用

使用 tab 补全快速引用文件：

```
> 请分析 src/comp[按 Tab 键]

将显示:
src/components/
src/utils/

选择 components → src/components/

> 请分析 src/components/UserCard.tsx
```

---

## 上下文管理

### 理解 Token 限制

Claude Code 的上下文窗口是有限的（通常 200K tokens）：
- 对话历史占用 tokens
- 文件内容占用 tokens
- 上下文过长时，早期内容会被"遗忘"

### 管理技巧

1. **定期使用 /clear**
   ```
   完成一个任务后 → /clear → 开始下一个任务
   ```

2. **只引用需要的文件**
   ```
   ❌ "分析整个项目"
   ✅ "分析 src/auth/login.ts 文件"
   ```

3. **使用 CLAUDE.md**
   ```
   将项目特定信息放在 CLAUDE.md
   Claude 会自动读取
   避免每次重复说明
   ```

4. **简洁的提示词**
   ```
   ❌ 长篇大论的描述
   ✅ 简洁明确的指令
   ```

---

## 常见工作流

### 工作流 1: 快速修复

```
> src/utils/date.ts:25 有个类型错误，帮我修复

[Claude 读取文件]

> 我看到问题了，formatDate 函数的返回类型应该是 string | null

[Claude 提供修复方案]

> 看起来不错，请修复

[Claude 修改文件]
```

### 工作流 2: 功能实现（使用 Plan Mode）

```
> [Shift+Tab 进入 Plan Mode]

我需要添加用户个人资料页面，包括：
- 头像上传
- 个人信息编辑
- 密码修改

请制定实现计划

[Claude 制定详细计划]

> 计划看起来不错，但我想用不同的头像存储方案

[Claude 调整计划]

> 现在可以了，开始实现

[Shift+Tab 退出 Plan Mode，Claude 开始实现]
```

### 工作流 3: 代码库探索

```
> 这个项目的认证系统是如何工作的？

[Claude 搜索相关文件]

> 认证系统基于 JWT token，流程如下：

1. 用户登录 → src/auth/login.ts
2. 生成 JWT token → src/auth/jwt.ts
3. 中间件验证 → src/middleware/auth.ts
4. 受保护路由 → src/routes/protected/

需要我详细解释某个部分吗？
```

---

## 总结

### 关键快捷键回顾

| 快捷键 | 功能 | 重要性 |
|--------|------|--------|
| `Shift+Tab` | Plan Mode 切换 | ⭐⭐⭐⭐⭐ |
| `Alt+V` | 粘贴图片 | ⭐⭐⭐⭐ |
| `Escape` | 中断操作 | ⭐⭐⭐⭐ |
| `Escape Escape` | 跳回历史 | ⭐⭐⭐ |

### 核心命令回顾

| 命令 | 功能 |
|------|------|
| `/help` | 显示帮助 |
| `/clear` | 清空上下文 |
| `/init` | 初始化项目 |
| `/permissions` | 管理权限 |

### 最佳实践

1. **Plan Mode 优先**: 复杂任务先用 Plan Mode
2. **提供上下文**: 明确告诉 Claude 相关文件和背景
3. **具体化指令**: 避免模糊的描述
4. **管理上下文**: 定期使用 /clear
5. **使用引用**: 用 tab 补全引用文件

### 下一步

在下一章中，我们将深入学习 Plan Mode：
- Plan Mode 的详细工作原理
- 何时使用、何时不使用
- 如何阅读和修改计划
- Plan Mode 的最佳实践

---

## 进一步阅读

### 相关章节
- [Chapter 2 - 安装与配置](chapter-02-setup.md)
- [Chapter 4 - Plan Mode 革命](chapter-04-plan-mode.md) - 下一章

### 研究材料
- `docs/research/02-plan-mode-guide-official.md` - Plan Mode 官方指南

---

## 练习

完成以下练习：

1. **快捷键练习**
   - [ ] 使用 `Shift+Tab` 切换 Plan Mode
   - [ ] 使用 `Alt+V` 粘贴一张图片
   - [ ] 使用 `Escape` 中断一个操作

2. **命令练习**
   - [ ] 使用 `/help` 查看帮助
   - [ ] 使用 `/clear` 清空上下文
   - [ ] 使用 `/permissions` 添加权限

3. **对话练习**
   - [ ] 让 Claude 读取一个文件
   - [ ] 让 Claude 解释一段代码
   - [ ] 让 Claude 修复一个简单的 bug

---

**上一章**: [Chapter 2 - 安装与配置](chapter-02-setup.md)
**下一章**: [Chapter 4 - Plan Mode 革命](chapter-04-plan-mode.md)
