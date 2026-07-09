# 插件：claude-mem

## 概述

`claude-mem` 是一个 Claude Code npm 插件，通过 SQLite 数据库 + 向量搜索，为 Claude 提供跨会话的长期记忆能力。

**Stars**: ~20k（2026-02 单日获 1739 stars，登上 GitHub 趋势第一）
**GitHub**: `thedotmack/claude-mem`
**类型**: npm 插件（`/plugin install` 安装）

**解决的核心问题**：
每次运行 `/clear` 或关闭终端后，Claude 会完全"失忆"——不记得你的项目背景、编码偏好、历史决策。`claude-mem` 让 Claude 在会话之间保持记忆。

**使用场景**:
- 记住项目特定的编码规范和偏好
- 保留历史架构决策，避免重复解释
- 在长期项目中维持连贯的上下文

---

## 安装

**前置要求**: Node.js 18+（Bun 会自动安装）

```bash
# 在 Claude Code 会话中执行
/plugin install claude-mem
```

安装完成后，插件会自动注册生命周期 Hook，无需额外配置。

---

## 工作原理

```
用户输入 / Claude 响应
        │
        ▼
┌─────────────────────┐
│  5 个生命周期 Hook   │
│                     │
│ • PreToolUse        │  ← 工具调用前检索相关记忆
│ • PostToolUse       │  ← 工具调用后捕获新信息
│ • PreCompact        │  ← 压缩前保存重要内容
│ • Stop              │  ← 会话结束时持久化记忆
│ • SubagentStop      │  ← 子代理结束时同步记忆
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│   SQLite 数据库      │  ← 结构化存储
│   Chroma 向量索引    │  ← 语义搜索
└─────────────────────┘
```

每次 Claude 开始新会话时，插件会自动检索与当前任务相关的历史记忆，注入到上下文中。

---

## 实际演示

### 基础用法

```bash
# 安装后立即生效，无需额外命令
$ claude

> 我们项目使用 TypeScript strict 模式，所有函数必须有返回类型注解

# claude-mem 自动记录这个偏好

> /clear
# 清空上下文...

> 帮我写一个解析 JSON 的函数
# Claude 会自动回想起 TypeScript strict 模式的要求
```

### 查看记忆 Web 界面

```bash
# 打开浏览器访问
http://localhost:37777
```

Web 查看器功能：
- 浏览所有存储的记忆
- 按来源/时间筛选
- 手动删除不需要的记忆

### 隐私控制

用 `<private>` 标签标记不想被记忆的内容：

```
<private>
这段 API Key 只用于临时测试：sk-xxxxx
</private>
```

标记为 `<private>` 的内容不会被 claude-mem 捕获和存储。

---

## 实战场景

### 场景 1：记住编码风格

```bash
# 第一次会话
> 我们团队规定：
  1. 变量用 camelCase
  2. 组件用 PascalCase
  3. 常量用 UPPER_SNAKE_CASE
  4. 所有异步函数必须处理错误

# 重新开启会话后
> 帮我写一个 React 组件来显示用户列表

# Claude 自动应用之前记住的规范
```

### 场景 2：保留架构决策

```bash
> 我们决定用 Zustand 而不是 Redux，因为状态比较简单，
  不需要 Redux 的样板代码。这个决定不要再建议换回 Redux。

# 之后的会话，当讨论状态管理时，Claude 会记住这个决定
```

### 场景 3：记录 Bug 修复历史

```bash
> 我们在 2026-01-15 修复了一个 React useEffect 的内存泄漏问题，
  原因是忘记在 cleanup 函数中取消订阅。以后写 useEffect 时提醒我。
```

---

## 常见问题

### Q1: 记忆会永久保存吗？

**A**: 默认是的，保存在本地 SQLite 数据库中。可以通过 Web 界面手动清理。

### Q2: 记忆会占用多少磁盘空间？

**A**: 非常小。纯文本记忆很紧凑，向量索引稍大，通常整个数据库不超过 100MB。

### Q3: 与 `--resume` 有什么区别？

**A**: `--resume` 恢复完整对话历史（适合短期），`claude-mem` 提取关键信息长期保存（适合跨项目）。

### Q4: 如何清除所有记忆重新开始？

```bash
# 删除数据库文件
rm ~/.claude-mem/memory.db
```

---

## 技巧与最佳实践

### 主动告知 Claude 重要信息

```bash
# 在会话开始时主动说明
> 请记住：这个项目的数据库是 PostgreSQL 14，ORM 用 Prisma，
  部署在 AWS ECS 上，CI/CD 用 GitHub Actions
```

### 利用记忆减少重复上下文

```bash
# 无需每次粘贴项目说明
> 根据你对我们项目的了解，评估这个新功能的实现方案
```

### 定期审查记忆

每隔一段时间访问 `http://localhost:37777`，清理过时的记忆，保持记忆库的准确性。

---

## 相关工具

- [Memory MCP Server](./official-mcp-servers.md#memory) - 官方简单 Key-Value 记忆方案
- [repomix](./repomix.md) - 将代码库打包，弥补记忆的不足
- [claude-squad](./claude-squad.md) - 多代理协作时共享记忆

---

**插件版本**: 最新
**最后更新**: 2026-02-10
