
# Ralph Loop - 高效使用指南

## 🚀 快速开始（3 分钟上手）

### 1. 安装插件

```bash
# 方法 1：CLI 安装（推荐）
/plugin install ralph-loop

# 方法 2：NPM 安装（如果方法 1 失败）
# 在系统终端运行：
npx claude-plugins install @anthropics/claude-code-plugins/ralph-loop
```

### 2. 验证安装

```bash
/help
# 检查是否有 ralph-loop:ralph-loop 和 ralph-loop:cancel-ralph
```

### 3. 运行第一个任务

```bash
/ralph-loop:ralph-loop "为 pkg/util/retry.go 添加单元测试，覆盖率 > 80%，完成后输出 <promise>DONE</promise>" --completion-promise "DONE" --max-iterations 10
```

---

## 📋 命令格式（根据你的环境）

**✅ 正确命令格式（你的环境）：**
```bash
/ralph-loop:ralph-loop "任务描述" --completion-promise "标志" --max-iterations 数字
/ralph-loop:cancel-ralph
```

**⚠️ 注意：** 不同安装方式可能命名空间不同：
- `ralph-loop:ralph-loop` - 官方插件（你的当前配置）
- `ralph-wiggum:ralph-loop` - 旧版本
- `ralph-loop` - 某些版本的简写

**验证你的命名空间：** 运行 `/help` 查看实际命令名称

---

## ⚡ 实战案例（针对 Go/IM Server 项目）

### 🟢 案例 1：单文件测试（新手入门，10 分钟）

**任务：** 为单个文件添加完整测试

```bash
/ralph-loop:ralph-loop "
为 internal/repository/redis/presence.go 添加完整单元测试

要求：
1. 使用 miniredis 模拟 Redis
2. 测试所有公开方法（Set, Get, Remove 等）
3. 覆盖正常流程和错误场景
4. 覆盖率 ≥ 85%

验证：运行 go test ./internal/repository/redis/ -cover -v

完成后输出 <promise>DONE</promise>
" --completion-promise "DONE" --max-iterations 10
```

**成本预估：** $10-20，10-20 分钟

---

### 🟡 案例 2：批量测试（中级，1-2 小时）

**任务：** 提升某个包的测试覆盖率

```bash
/ralph-loop:ralph-loop "
提升 internal/repository/db/user/ 包的测试覆盖率到 80%+

执行步骤：
1. 为 repository.go 中所有公开方法添加测试
2. 测试正常流程和错误路径
3. 测试并发安全性（如果涉及）
4. 每完成一个测试文件，运行 go test -cover 验证

验证：go test ./internal/repository/db/user/... -cover
目标：覆盖率 ≥ 80%

完成后输出 <promise>USER_REPO_TESTS_DONE</promise>
" --completion-promise "USER_REPO_TESTS_DONE" --max-iterations 20
```

**成本预估：** $30-60，1-2 小时

---

### 🔴 案例 3：复杂重构（高级，3-6 小时）

**任务：** 重构整个模块的架构

```bash
/ralph-loop:ralph-loop "
重构 internal/app/message/ 包，按照 DDD 分层拆分

目标结构：
- core_service.go - 核心业务逻辑
- validator.go - 参数验证
- hooks.go - 生命周期钩子
- saga_compensation.go - 事务补偿

执行步骤：
1. 分析当前代码结构，识别职责
2. 按功能拆分到独立文件
3. 确保所有 import 正确
4. 运行 go test ./internal/app/message/... 验证功能不变
5. 运行 go build ./cmd/server 确保编译通过

自检机制：每拆分一个文件，立即运行测试验证

完成条件：
- 代码按职责拆分到独立文件
- 所有测试通过
- 编译成功
- 输出 <promise>REFACTOR_COMPLETE</promise>
" --completion-promise "REFACTOR_COMPLETE" --max-iterations 30
```

**成本预估：** $80-150，3-6 小时

---

## 🎯 5 个成功要素（必读）

### 1️⃣ 任务必须具体且可自动验证

```bash
# ❌ 错误："优化代码"
# ✅ 正确："为 pkg/util/retry.go 添加测试，go test 通过，覆盖率 > 80%"
```

### 2️⃣ 必须有明确的完成标志

```bash
# 完成后必须输出这个标记
完成后输出 <promise>DONE</promise>
```

### 3️⃣ 必须设置迭代上限（防止无限循环）

```bash
--max-iterations 10   # 单文件任务
--max-iterations 20   # 单包/模块任务
--max-iterations 30   # 多包重构
```

### 4️⃣ 必须包含自检机制

```bash
# 在提示词中加入：
每完成一个文件，运行 go test -cover 验证
如果失败，查看错误并修复
重复直到通过
```

### 5️⃣ 大任务拆分执行（最重要！）

```bash
# ❌ 不要这样：
"完成 TODO.md 中的所有任务" --max-iterations 50

# ✅ 应该这样：
# 任务 1：先测试 presence.go (10 次)
# 任务 2：再测试 user_id_mapper.go (10 次)
# 任务 3：最后测试整个 redis/ 包 (20 次)
```

---

## 💰 成本与时间预估

| 任务类型 | 迭代次数 | 时间 | 成本 |
|---------|---------|------|------|
| 单文件测试 | 10 | 10-30min | $10-20 |
| 单包测试 | 20 | 1-2h | $30-60 |
| 模块重构 | 30 | 3-6h | $80-150 |

---

## ⚠️ 重要提醒

### 1. 新建分支保护代码

```bash
git checkout -b ralph-auto-dev
```

### 2. 先小规模测试

```bash
# 第一次使用建议只设置 5 次迭代，观察效果
--max-iterations 5
```

### 3. 监控运行状态

**正常：**
- 每次迭代输出不同内容
- 错误逐渐减少
- 有明显进展

**卡住：**
- 连续 5 次相同错误
- 原地打转
- 立即运行 `/ralph-loop:cancel-ralph` 停止

---

## ❓ FAQ

### Q1: 命令太长怎么办？

使用多行输入：
```bash
/ralph-loop:ralph-loop "
第一行任务描述
第二行任务描述
第三行任务描述
" --completion-promise "DONE" --max-iterations 10
```

### Q2: 如何停止正在运行的任务？

```bash
/ralph-loop:cancel-ralph
```

### Q3: 运行失败了怎么办？

**检查清单：**
1. 任务是否太大？→ 拆分成更小的任务
2. 是否有完成标志 `<promise>XXX</promise>`？
3. 是否包含自检机制（如 `go test`）？
4. 任务是否可以完全自动验证？

### Q4: 如何写出好的提示词？

```bash
# ❌ 错误示例
"优化代码"

# ✅ 正确示例
"
为 pkg/util/retry.go 添加单元测试

要求：
1. 测试所有公开方法
2. 覆盖正常流程和错误场景
3. 覆盖率 ≥ 80%

验证：go test ./pkg/util/ -cover
完成后输出 <promise>DONE</promise>
"
```

### Q5: Ralph 适合做什么？

**✅ 适合：**
- 添加单元测试
- 批量重构（如统一命名、添加注释）
- 按模板生成代码
- 自动修复 lint 错误

**❌ 不适合：**
- 需要人工判断的架构设计
- 需要 UI 交互的任务
- 复杂的跨项目重构
- 不能自动验证的任务

---

## 💎 高级技巧

### 1. 分阶段执行大任务

```bash
# ❌ 不要一次执行 50 次迭代的大任务
/ralph-loop:ralph-loop "完成整个模块的重构..." --max-iterations 50

# ✅ 拆分成 3 个小任务
# 阶段 1：
/ralph-loop:ralph-loop "重构 service 层..." --max-iterations 15

# 阶段 2：
/ralph-loop:ralph-loop "重构 repository 层..." --max-iterations 15

# 阶段 3：
/ralph-loop:ralph-loop "添加测试..." --max-iterations 15
```

### 2. 让 Ralph 输出进度报告

```bash
/ralph-loop:ralph-loop "
任务描述...

每完成一个文件，输出进度：
- 已完成：X/Y 个文件
- 当前覆盖率：Z%
- 剩余工作：...
" --completion-promise "DONE" --max-iterations 20
```

### 3. 使用 Git 保护代码

```bash
# 运行前创建分支
git checkout -b ralph-test

# 运行完成后查看改动
git diff main

# 满意后合并
git checkout main && git merge ralph-test
```

---

## 🎯 快速参考卡片

**命令模板：**
```bash
/ralph-loop:ralph-loop "<任务>" --completion-promise "<标志>" --max-iterations <数字>
```

**成功要素：**
1. 任务具体且可自动验证
2. 包含明确的完成标志 `<promise>XXX</promise>`
3. 设置合理的迭代上限
4. 包含自检机制（如 `go test`）
5. 大任务拆分成小任务

**停止命令：**
```bash
/ralph-loop:cancel-ralph
```

---

## 📌 立即开始

**步骤 1：** 复制案例 1 的命令（单文件测试）
**步骤 2：** 修改文件路径为你的项目文件
**步骤 3：** 在 Claude Code CLI 中粘贴并回车
**步骤 4：** 观察执行，理解工作原理

**推荐第一个任务：**
```bash
/ralph-loop:ralph-loop "为 internal/repository/redis/presence.go 添加完整单元测试，使用 miniredis 模拟 Redis，测试所有公开方法，覆盖率 ≥ 85%，运行 go test -cover 验证，完成后输出 <promise>DONE</promise>" --completion-promise "DONE" --max-iterations 10
```
