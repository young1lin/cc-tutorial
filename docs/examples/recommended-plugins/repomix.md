# 工具：repomix

## 概述

`repomix` 将整个代码库打包为一个 AI 优化的单文件（XML/Markdown），方便将完整项目上下文提供给 Claude。

**GitHub**: `yamadashy/repomix`
**类型**: 独立 CLI 工具
**Star 数**: 热门（持续增长）

**解决的核心问题**：
处理大型项目时，"把整个代码库发给 Claude"是个难题：
- 文件太多，不知道该发哪些
- 手动拼接文件容易遗漏
- 不知道会消耗多少 Token

`repomix` 自动处理这些问题，生成干净、Token 高效的代码库快照。

**使用场景**:
- 架构分析和重构建议
- 代码库迁移评估
- 技术债务盘点
- 为新 Claude 会话快速提供完整项目背景

---

## 安装

```bash
# 临时使用（推荐）
npx repomix

# 全局安装
npm install -g repomix

# 验证
repomix --version
```

---

## 工作原理

```
代码库目录
    │
    ▼
┌─────────────────────────────────────┐
│              repomix                 │
│                                     │
│ 1. 读取所有文件（遵循 .gitignore）   │
│ 2. Tree-sitter 语法分析             │
│    └── 理解代码结构和依赖关系        │
│ 3. 应用过滤规则（.repomixignore）   │
│ 4. Token 数量估算                   │
│ 5. 生成 AI 优化格式                 │
└──────────────┬──────────────────────┘
               │
               ▼
      repomix-output.xml
      （或 .md/.txt 格式）
```

生成的文件包含文件树、每个文件的内容，以及 Claude 容易理解的结构标记。

---

## 基础用法

### 打包当前目录

```bash
# 在项目根目录运行
repomix

# 默认生成 repomix-output.xml
# 同时显示统计信息：
# ✔ Packed 142 files (1,247 KB)
# ✔ Total tokens: ~89,400 (Opus: $1.34, Haiku: $0.02)
```

### 常用选项

```bash
# 指定输出格式
repomix --style markdown   # Markdown 格式
repomix --style plain      # 纯文本格式
repomix --style xml        # XML 格式（默认，最适合 AI）

# 压缩模式（移除注释和空行，节省 ~30% Token）
repomix --compress

# 只打包特定目录
repomix --include "src/**"

# 排除特定文件
repomix --exclude "**/*.test.ts" --exclude "**/*.spec.ts"

# 统计 token 数量（不生成文件）
repomix --token-count

# 远程仓库（直接从 GitHub 打包）
repomix --remote https://github.com/user/repo
```

---

## 输出格式示例

```xml
<!-- repomix-output.xml 格式 -->
<repository>
  <summary>
    <total_files>142</total_files>
    <total_tokens>89400</total_tokens>
  </summary>

  <file_tree>
    src/
    ├── auth/
    │   ├── auth.service.ts
    │   └── auth.controller.ts
    ├── payment/
    │   └── payment.service.ts
    └── app.module.ts
  </file_tree>

  <files>
    <file path="src/auth/auth.service.ts">
      <content>
        // 文件内容...
      </content>
    </file>
    <!-- 更多文件... -->
  </files>
</repository>
```

---

## 配置文件

创建 `repomix.config.json` 持久化配置：

```json
{
  "output": {
    "filePath": "context/codebase.xml",
    "style": "xml",
    "compress": true,
    "showLineNumbers": true,
    "copyToClipboard": false
  },
  "include": [
    "src/**",
    "tests/**",
    "CLAUDE.md",
    "package.json"
  ],
  "ignore": {
    "useGitignore": true,
    "customPatterns": [
      "**/*.test.ts",
      "**/*.spec.ts",
      "node_modules/**",
      "dist/**",
      "**/*.lock",
      "coverage/**"
    ]
  },
  "security": {
    "enableSecurityCheck": true  // 自动检测并移除密钥等敏感信息
  }
}
```

---

## `.repomixignore` 文件

类似 `.gitignore`，专门用于排除不相关文件：

```
# .repomixignore

# 测试文件（视情况排除）
**/*.test.ts
**/*.spec.ts
__tests__/

# 生成文件
dist/
build/
coverage/

# 大型资产文件
**/*.png
**/*.jpg
**/*.svg
**/*.pdf

# 不相关的配置
.github/
docs/images/
```

---

## 实际演示

### 场景 1：架构分析

```bash
# 生成代码库快照
$ repomix --compress

# 发给 Claude
$ claude

> 这是我们的代码库快照，请分析：
  1. 整体架构有什么问题？
  2. 哪些模块之间耦合度过高？
  3. 有哪些重复代码可以抽象？

[将 repomix-output.xml 内容粘贴或通过文件引用]
```

### 场景 2：快速上下文建立

```bash
# 开始新会话时，无需逐个解释文件
$ repomix --compress --style markdown
$ claude

> 以下是我们项目 mybatis-boost 的完整代码库，
  请先理解项目结构，然后帮我：
  为 MybatisSqlFormatter 类添加 Oracle 方言支持

$(cat repomix-output.md)
```

### 场景 3：技术迁移评估

```bash
# 分析迁移可行性
$ repomix
$ claude "分析这个 Express.js 项目，
  评估迁移到 NestJS 的工作量：
  - 哪些部分可以直接迁移？
  - 哪些需要重写？
  - 依赖项有什么兼容性问题？
  给出一个 3 分制的难度评分" < repomix-output.xml
```

### 场景 4：配合 repomix 远程分析开源项目

```bash
# 分析 GitHub 上的开源项目
$ repomix --remote https://github.com/smtg-ai/claude-squad

# 或分析特定分支
$ repomix --remote https://github.com/user/repo --branch develop
```

---

## Token 优化技巧

### 分层打包策略

```bash
# 只打包核心源码（减少 60-70% Token）
repomix --include "src/**" --exclude "src/**/*.test.*"

# 关键配置文件
repomix --include "package.json,tsconfig.json,CLAUDE.md"

# 然后按需追加特定文件
```

### 对比不同配置的 Token 消耗

```bash
# 全量打包
repomix --token-count
# → Total tokens: 245,000

# 压缩模式
repomix --compress --token-count
# → Total tokens: 178,000 (节省 27%)

# 只包含源码
repomix --include "src/**" --token-count
# → Total tokens: 89,400 (节省 64%)
```

### 安全检查

repomix 内置安全检查，防止意外包含密钥：

```bash
# 启用安全检查（默认开启）
repomix --security

# 输出：
# ⚠️  Detected potential secrets in:
#   .env (line 3): STRIPE_SECRET_KEY=sk_live_...
# These files have been excluded from output.
```

---

## 常见问题

### Q1: 输出文件太大，超过 Claude 的上下文窗口怎么办？

**A**: 分层处理：先发送文件树 + 关键文件，再按需发送具体文件内容。

```bash
# 只生成文件树（极少 Token）
repomix --tree-only
```

### Q2: 每次打包都要重新生成吗？

**A**: 如果代码变化不大，可以复用上次的输出。在 CI/CD 中可以定时生成并缓存。

### Q3: 支持哪些语言？

**A**: 几乎所有主流语言，Tree-sitter 语法分析支持 50+ 种语言。

### Q4: 输出内容会包含 `.env` 文件吗？

**A**: 默认遵循 `.gitignore`，通常 `.env` 已在 `.gitignore` 中。启用安全检查会进一步过滤。

---

## 技巧与最佳实践

### 在 CLAUDE.md 中记录常用 repomix 命令

```markdown
## 上下文管理

生成代码库快照：
```bash
repomix --compress --include "src/**" --output context/snapshot.xml
```

使用方式：将 context/snapshot.xml 内容投喂给新 Claude 会话
```

### 与 CI/CD 集成

```yaml
# .github/workflows/generate-context.yml
- name: Generate codebase snapshot
  run: |
    npx repomix --compress
    # 可以将 repomix-output.xml 上传为 artifact
```

### 配合 firecrawl 处理文档

```bash
# 代码 + 文档一起打包
repomix --include "src/**"  # 生成代码快照
firecrawl scrape https://docs.mylib.com > docs-snapshot.md  # 抓取文档

# 发给 Claude：
# "这是代码库（repomix-output.xml）和 API 文档（docs-snapshot.md），帮我..."
```

---

## 相关工具

- [firecrawl](./firecrawl.md) - 抓取外部文档，与 repomix 配合使用
- [claude-mem](./claude-mem.md) - 记忆长期上下文，补充 repomix 的不足
- [ccusage](./ccusage.md) - 追踪 repomix 上下文投喂的 Token 消耗

---

**工具版本**: 最新
**最后更新**: 2026-02-10
