# Chapter 34: Claude Code in CI/CD Pipelines

## 学习目标

完成本章后，你将能够：

- 理解如何在 CI/CD 管道中使用 AI
- 实现 AI 辅助的代码审查
- 自动化测试生成和执行
- 创建 AI 辅助的文档生成
- 避免 CI/CD 中的常见陷阱

## 前置知识

- [Module 2: 核心工作流](../module-02-core-workflows/)
- [Module 8: 构建自己的工作流](../module-08-building-workflows/)

---

## 34.1 CI/CD 中的 AI 概览

```typescript
/**
 * AI 在 CI/CD 中的角色
 */

const aiInCICD = {
  vision: `
    愿景：
    将 Claude Code 集成到 CI/CD 管道中，
    让 AI 成为持续集成和持续交付流程的一部分。

    价值：
    - 自动化代码审查
    - 智能测试生成
    - 动态文档更新
    - 预测性质量检查
  `,

  useCases: [
    "PR 自动审查和反馈",
    "测试用例生成和增强",
    "文档自动生成",
    "性能瓶颈检测",
    "安全漏洞扫描",
    "依赖升级建议"
  ],

  challenges: [
    "API 成本和配额",
    "执行时间影响",
    "结果可靠性",
    "敏感信息保护",
    "管道稳定性"
  ]
};
```

---

## 34.2 AI 辅助代码审查

### 34.2.1 基础实现

```yaml
# .github/workflows/ai-review.yml

name: AI Code Review

on:
  pull_request:
    types: [opened, synchronize]

jobs:
  ai-review:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Install Claude Code CLI
        run: npm install -g @anthropic-ai/claude-code

      - name: Configure Claude
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          echo "API_KEY=${{ secrets.ANTHROPIC_API_KEY }}" > ~/.claude-config

      - name: Get changed files
        id: changed
        run: |
          FILES=$(git diff --name-only origin/${{ github.base_ref }}...HEAD | tr '\n' ' ')
          echo "files=$FILES" >> $GITHUB_OUTPUT

      - name: Run AI Review
        id: review
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          CHANGED_FILES: ${{ steps.changed.outputs.files }}
        run: |
          # 创建审查提示
          cat > /tmp/review-prompt.txt << 'EOF'
          请审查以下 PR 中的代码变更：

          变更文件：${CHANGED_FILES}

          请检查：
          1. 功能正确性
          2. 代码质量
          3. 潜在bug
          4. 安全问题
          5. 性能考虑

          以 JSON 格式输出：
          {
            "summary": "审查摘要",
            "issues": [
              {"file": "文件路径", "line": 行号, "severity": "high/medium/low", "message": "问题描述"}
            ],
            "suggestions": ["改进建议"]
          }
          EOF

          # 运行 Claude Code
          claude-code --non-interactive \
            --prompt "$(cat /tmp/review-prompt.txt)" \
            --output /tmp/review-result.json

      - name: Post Review Comments
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const result = JSON.parse(fs.readFileSync('/tmp/review-result.json', 'utf8'));

            // 格式化评论
            let body = '## 🤖 AI Code Review\n\n';
            body += result.summary + '\n\n';

            if (result.issues.length > 0) {
              body += '### Issues Found\n\n';
              result.issues.forEach(issue => {
                const emoji = issue.severity === 'high' ? '🔴' : issue.severity === 'medium' ? '🟡' : '🟢';
                body += `${emoji} **${issue.file}:${issue.line}** - ${issue.message}\n`;
              });
            }

            if (result.suggestions.length > 0) {
              body += '\n### Suggestions\n\n';
              result.suggestions.forEach(s => {
                body += `- ${s}\n`;
              });
            }

            // 发布评论
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: body
            });
```

### 34.2.2 高级实现

```typescript
/**
 * 高级 AI 代码审查配置
 */

interface AIReviewConfig {
  // 审查规则
  rules: ReviewRule[];

  // 忽略规则
  ignore: {
    files: string[];
    patterns: RegExp[];
  };

  // 严重性级别
  severity: {
    high: string[];
    medium: string[];
    low: string[];
  };

  // 自定义检查
  customChecks: CustomCheck[];
}

const advancedReviewConfig: AIReviewConfig = {
  rules: [
    {
      name: "security",
      description: "检查安全漏洞",
      checks: [
        "SQL 注入",
        "XSS 漏洞",
        "硬编码密钥",
        "不安全的随机数",
        "依赖注入"
      ],
      severity: "high"
    },
    {
      name: "performance",
      description: "检查性能问题",
      checks: [
        "N+1 查询",
        "内存泄漏",
        "不必要的重渲染",
        "大文件处理"
      ],
      severity: "medium"
    },
    {
      name: "code-quality",
      description: "检查代码质量",
      checks: [
        "函数长度",
        "复杂度",
        "重复代码",
        "命名规范",
        "文档完整性"
      ],
      severity: "low"
    }
  ],

  ignore: {
    files: [
      "package-lock.json",
      "*.min.js",
      "dist/**",
      "node_modules/**"
    ],
    patterns: [
      /\/vendor\//,
      /\/generated\//
    ]
  },

  severity: {
    high: ["安全漏洞", "数据损坏", "服务中断"],
    medium: ["性能问题", "可维护性"],
    low: ["代码风格", "文档缺失"]
  },

  customChecks: [
    {
      name: "custom-security-check",
      pattern: /process\.env\.[A-Z_]+/,
      message: "确保环境变量在使用前已验证",
      severity: "medium"
    },
    {
      name: "async-error-handling",
      pattern: /async\s+\w+\([^)]*\)\s*{[^}]*}(?!\s*\.catch)/,
      message: "异步函数缺少错误处理",
      severity: "high"
    }
  ]
};

/**
 * TypeScript 审查脚本
 */

// ai-review.ts
import { execSync } from 'child_process';
import { readFileSync, writeFileSync } from 'fs';
import { join } from 'path';

interface ReviewResult {
  summary: string;
  issues: ReviewIssue[];
  suggestions: string[];
  score: number;
}

interface ReviewIssue {
  file: string;
  line: number;
  severity: 'high' | 'medium' | 'low';
  message: string;
  code?: string;
}

async function runAIReview(prNumber: number): Promise<ReviewResult> {
  // 获取 PR 变更
  const changedFiles = getChangedFiles(prNumber);

  // 为每个文件运行 AI 审查
  const issues: ReviewIssue[] = [];

  for (const file of changedFiles) {
    const content = readFileSync(file, 'utf-8');
    const diff = getFileDiff(file);

    const reviewPrompt = `
审查以下代码变更：

文件：${file}
差异：
\`\`\`diff
${diff}
\`\`\`

完整文件：
\`\`\`typescript
${content}
\`\`\`

检查项：
1. 功能正确性
2. 安全漏洞
3. 性能问题
4. 代码质量
5. 测试覆盖

返回 JSON 格式的审查结果。
`;

    // 调用 Claude Code API
    const result = await callClaudeAPI(reviewPrompt);

    // 解析结果
    const fileIssues = parseReviewResult(result, file);
    issues.push(...fileIssues);
  }

  // 生成总结
  const summary = generateSummary(issues);

  // 生成建议
  const suggestions = generateSuggestions(issues);

  // 计算分数
  const score = calculateScore(issues);

  return { summary, issues, suggestions, score };
}

function calculateScore(issues: ReviewIssue[]): number {
  let score = 100;

  issues.forEach(issue => {
    switch (issue.severity) {
      case 'high':
        score -= 10;
        break;
      case 'medium':
        score -= 5;
        break;
      case 'low':
        score -= 2;
        break;
    }
  });

  return Math.max(0, score);
}
```

---

## 34.3 自动化测试生成

### 34.3.1 测试生成工作流

```yaml
# .github/workflows/ai-tests.yml

name: AI Test Generation

on:
  push:
    branches: [main, develop]
  pull_request:

jobs:
  generate-tests:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Install dependencies
        run: npm ci

      - name: Identify untested files
        id: untested
        run: |
          # 查找没有对应测试文件的源文件
          UNTTESTED=$(find src -name "*.ts" -not -name "*.test.ts" -not -name "*.spec.ts" | \
            while read file; do
              test="${file%.ts}.test.ts"
              if [ ! -f "$test" ]; then
                echo "$file"
              fi
            done)
          echo "files=$UNTESTED" >> $GITHUB_OUTPUT

      - name: Generate tests with AI
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          for file in ${{ steps.untested.outputs.files }}; do
            echo "Generating tests for $file"

            # 创建测试生成提示
            cat > /tmp/test-prompt.txt << EOF
            为以下文件生成完整的单元测试：

            文件：$file

            源代码：
            \`\`\`typescript
            $(cat $file)
            \`\`\`

            要求：
            1. 使用 Jest 测试框架
            2. 覆盖所有分支和边界情况
            3. 包含必要的 mock 和 setup
            4. 添加清晰的测试描述
            5. 遵循项目的测试规范

            直接输出测试文件内容，不要其他解释。
            EOF

            # 调用 Claude Code 生成测试
            TEST_OUTPUT=$(claude-code --non-interactive \
              --prompt "$(cat /tmp/test-prompt.txt)" \
              --model claude-opus-4-5)

            # 写入测试文件
            TEST_FILE="${file%.ts}.test.ts"
            echo "$TEST_OUTPUT" > "$TEST_FILE"

            echo "Generated $TEST_FILE"
          done

      - name: Run generated tests
        run: npm test

      - name: Create PR with tests
        if: github.event_name == 'push'
        uses: peter-evans/create-pull-request@v6
        with:
          title: "🤖 AI Generated Tests"
          body: |
            ## 自动生成的测试

            此 PR 包含由 Claude Code 自动生成的单元测试。

            请审查生成的测试，确保：
            1. 测试逻辑正确
            2. 边界情况覆盖完整
            3. Mock 设置适当

            如果发现问题，请修改并提交。
          branch: ai-generated-tests
          commit-message: "AI: Generate unit tests"
```

### 34.3.2 测试覆盖率增强

```typescript
/**
 * AI 辅助测试覆盖率增强
 */

interface CoverageEnhancement {
  file: string;
  currentCoverage: number;
  targetCoverage: number;
  uncoveredLines: number[];
  suggestedTests: TestCase[];
}

async function enhanceTestCoverage(
  file: string,
  coverageReport: CoverageReport
): Promise<CoverageEnhancement> {
  const uncoveredLines = coverageReport.getUncoveredLines(file);
  const sourceCode = readFileSync(file, 'utf-8');

  // 使用 AI 分析未覆盖的代码
  const prompt = `
分析以下源代码中未覆盖的行，生成测试用例：

文件：${file}
源代码：
\`\`\`typescript
${sourceCode}
\`\`\`

未覆盖的行：${uncoveredLines.join(', ')}

要求：
1. 为每个未覆盖的分支生成测试
2. 为边界条件生成测试
3. 为错误处理生成测试
4. 确保测试可以独立运行

返回 JSON 格式的测试用例数组。
`;

  const result = await callClaudeAPI(prompt);
  const suggestedTests = JSON.parse(result);

  return {
    file,
    currentCoverage: coverageReport.getCoverage(file),
    targetCoverage: 100,
    uncoveredLines,
    suggestedTests
  };
}
```

---

## 34.4 文档自动生成

### 34.4.1 API 文档生成

```yaml
# .github/workflows/ai-docs.yml

name: AI Documentation

on:
  push:
    branches: [main]
    paths:
      - 'src/api/**/*.ts'
      - 'src/controllers/**/*.ts'

jobs:
  generate-api-docs:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Generate API documentation
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          # 查找 API 文件
          find src/api src/controllers -name "*.ts" | while read file; do
            echo "Generating docs for $file"

            # 创建文档生成提示
            cat > /tmp/docs-prompt.txt << EOF
            为以下 API 文件生成 OpenAPI 3.0 规范文档：

            文件：$file

            源代码：
            \`\`\`typescript
            $(cat $file)
            \`\`\`

            要求：
            1. 提取所有端点
            2. 识别请求方法、路径、参数
            3. 描述请求体和响应体
            4. 包含状态码
            5. 添加示例

            返回 OpenAPI 3.0 YAML 格式。
            EOF

            # 生成文档
            DOCS_OUTPUT=$(claude-code --non-interactive \
              --prompt "$(cat /tmp/docs-prompt.txt)")

            # 保存到 docs 目录
            DOCS_FILE="docs/api/$(basename $file .ts).yaml"
            mkdir -p "$(dirname $DOCS_FILE)"
            echo "$DOCS_OUTPUT" > "$DOCS_FILE"
          done

      - name: Commit documentation
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add docs/api/
          git diff --quiet && git diff --staged --quiet || git commit -m "docs: AI generated API documentation"

      - name: Push changes
        uses: ad-m/github-push-action@master
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          branch: docs
```

### 34.4.2 README 和贡献指南

```typescript
/**
 * AI 生成项目文档
 */

interface DocumentationPlan {
  readme: string;
  contributing: string;
  changelog: string;
  apiDocs: string;
}

async function generateDocumentation(
  repoPath: string
): Promise<DocumentationPlan> {
  // 分析项目结构
  const structure = analyzeProjectStructure(repoPath);

  // 生成 README
  const readme = await generateREADME(structure);

  // 生成贡献指南
  const contributing = await generateContributing(structure);

  // 生成变更日志
  const changelog = await generateChangelog(repoPath);

  // 生成 API 文档
  const apiDocs = await generateAPIDocumentation(structure);

  return { readme, contributing, changelog, apiDocs };
}

async function generateREADME(structure: ProjectStructure): Promise<string> {
  const prompt = `
为以下项目生成一个完整的 README.md 文件：

项目信息：
- 名称：${structure.name}
- 描述：${structure.description}
- 技术栈：${structure.techStack.join(', ')}

项目结构：
\`\`\`
${structure.tree}
\`\`\`

主要功能：
${structure.features.map(f => `- ${f}`).join('\n')}

README 应该包含：
1. 项目标题和简介
2. 功能特性
3. 快速开始
4. 安装说明
5. 使用示例
6. 配置选项
7. 贡献指南
8. 许可证

使用适当的 emoji 和 markdown 格式。
`;

  return await callClaudeAPI(prompt);
}
```

---

## 34.5 依赖管理和升级

### 34.5.1 智能依赖升级

```yaml
# .github/workflows/ai-deps.yml

name: AI Dependency Management

on:
  schedule:
    - cron: '0 0 * * 1'  # 每周一
  workflow_dispatch:

jobs:
  dependency-review:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Check for outdated dependencies
        id: outdated
        run: |
          npm outdated --json > outdated.json
          echo "count=$(jq '. | length' outdated.json)" >> $GITHUB_OUTPUT

      - name: Analyze with AI
        if: steps.outdated.outputs.count > 0
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          cat > /tmp/deps-prompt.txt << 'EOF'
          分析以下过时的依赖包，推荐升级策略：

          依赖信息：
          $(cat outdated.json)

          考虑：
          1. 升级的风险（breaking changes）
          2. 安全漏洞
          3. 性能改进
          4. 维护状态

          推荐哪些包应该立即升级，哪些可以等待？
          返回 JSON 格式的建议。
          EOF

          ANALYSIS=$(claude-code --non-interactive \
            --prompt "$(cat /tmp/deps-prompt.txt)")

          echo "$ANALYSIS" > dependency-analysis.json

      - name: Create issue with recommendations
        if: steps.outdated.outputs.count > 0
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const analysis = JSON.parse(fs.readFileSync('dependency-analysis.json', 'utf8'));

            let body = '## 📦 依赖升级建议\n\n';
            body += 'AI 分析了过时的依赖包，以下是建议：\n\n';

            analysis.immediate.forEach(dep => {
              body += `### 🚨 立即升级：${dep.name}\n`;
              body += `- 当前版本：${dep.current}\n`;
              body += `- 最新版本：${dep.latest}\n`;
              body += `- 理由：${dep.reason}\n\n`;
            });

            analysis.later.forEach(dep => {
              body += `### ⏳ 计划升级：${dep.name}\n`;
              body += `- 当前版本：${dep.current}\n`;
              body += `- 最新版本：${dep.latest}\n\n`;
            });

            github.rest.issues.create({
              owner: context.repo.owner,
              repo: context.repo.repo,
              title: '📦 依赖升级建议',
              body: body,
              labels: ['dependencies', 'ai-generated']
            });
```

---

## 34.6 CI/CD 最佳实践

### 34.6.1 性能优化

```typescript
/**
 * CI/CD 中 AI 的性能优化
 */

const performanceOptimizations = {
  caching: `
    缓存策略：

    1. 缓存 AI 响应
       - 相同文件变更不重复审查
       - 使用 SHA 作为缓存键

    2. 增量处理
       - 只处理变更的文件
       - 跟踪已审查的内容

    3. 并行处理
       - 多文件并行审查
       - 使用矩阵策略
  `,

  costControl: `
    成本控制：

    1. 使用合适的模型
       - 简单任务使用 Haiku
       - 复杂任务使用 Opus

    2. 限制审查范围
       - 只审查关键文件
       - 设置变更大小阈值

    3. 批处理
       - 合并小审查
       - 减少API调用
  `,

  reliability: `
    可靠性策略：

    1. 超时处理
       - 设置合理的超时
       - 失败时降级

    2. 重试机制
       - 指数退避重试
       - 最大重试次数

    3. 回退选项
       - AI 失败时使用传统方法
       - 记录失败原因
  `
};
```

### 34.6.2 安全考虑

```yaml
# 安全的 CI/CD 配置
name: AI CI/CD with Security

on:
  pull_request:

jobs:
  secure-ai-review:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      # 使用 OIDC 而非 API 密钥
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ secrets.AWS_ROLE_ARN }}
          aws-region: us-east-1

      # 从 Secrets Manager 获取 API 密钥
      - name: Get API key
        id: secrets
        run: |
          API_KEY=$(aws secretsmanager get-secret-value \
            --secret-id claude-api-key \
            --query SecretString --output text)
          echo "::add-mask::$API_KEY"
          echo "key=$API_KEY" >> $GITHUB_OUTPUT

      # 扫描敏感信息
      - name: Scan for secrets
        uses: trufflesecurity/trufflehog@main
        with:
          path: ./
          base: ${{ github.event.repository.default_branch }}

      # 限制审查内容
      - name: Sanitize input
        run: |
          # 移除敏感信息
          sed -i 's/Bearer sk-.*/Bearer [REDACTED]/g' diff.patch

      # 运行 AI 审查
      - name: AI Review
        env:
          ANTHROPIC_API_KEY: ${{ steps.secrets.outputs.key }}
        run: |
          # 审查逻辑...

      # 审查 AI 输出
      - name: Review AI output
        run: |
          # 确保 AI 没有泄露敏感信息
          if grep -r "sk-" ai-output/; then
            echo "AI output contains sensitive data!"
            exit 1
          fi
```

---

## 34.7 监控和报告

### 34.7.1 CI/CD 指标

```typescript
/**
 * CI/CD AI 性能指标
 */

interface CICDMetrics {
  // 执行指标
  execution: {
    duration: number;        // 执行时间
    success: boolean;        // 是否成功
    model: string;          // 使用的模型
    tokens: number;         // Token 使用
    cost: number;           // 成本
  };

  // 质量指标
  quality: {
    issuesFound: number;    // 发现的问题
    issuesFixed: number;    // 修复的问题
    falsePositives: number; // 假阳性
    falseNegatives: number; // 假阴性
  };

  // 效率指标
  efficiency: {
    timeSaved: number;      // 节省的时间
    reviewsAutomated: number; // 自动审查数
    humanReviewTime: number; // 人工审查时间
  };
}

/**
 * 收集 CI/CD 指标
 */

async function collectCICDMetrics(
  workflowRun: WorkflowRun
): Promise<CICDMetrics> {
  return {
    execution: {
      duration: workflowRun.duration,
      success: workflowRun.conclusion === 'success',
      model: workflowRun.params.model,
      tokens: workflowRun.tokens,
      cost: calculateCost(workflowRun.tokens, workflowRun.params.model)
    },
    quality: {
      issuesFound: workflowRun.issues.length,
      issuesFixed: workflowRun.issues.filter(i => i.fixed).length,
      falsePositives: workflowRun.falsePositives,
      falseNegatives: workflowRun.falseNegatives
    },
    efficiency: {
      timeSaved: estimateTimeSaved(workflowRun),
      reviewsAutomated: workflowRun.files.length,
      humanReviewTime: workflowRun.manualReviewTime
    }
  };
}
```

---

## 34.8 常见陷阱

```typescript
/**
 * CI/CD 中使用 AI 的常见陷阱
 */

const commonCICDPitfalls = [
  {
    pitfall: "过度依赖 AI",
    description: "完全信任 AI 的审查结果",
    consequence: "漏掉关键问题，产生虚假安全感",
    solution: "AI 应该作为辅助，最终决策由人类做出"
  },

  {
    pitfall: "忽视成本",
    description: "每次 CI 都调用昂贵的 AI 模型",
    consequence: "成本失控",
    solution: "使用缓存、增量处理、选择合适的模型"
  },

  {
    pitfall: "泄露敏感信息",
    description: "将代码中的密钥发送给 AI",
    consequence: "安全漏洞",
    solution: "预先扫描、使用占位符、审查 AI 输出"
  },

  {
    pitfall: "延长 CI 时间",
    description: "AI 审查增加太多时间",
    consequence: "开发体验下降",
    solution: "并行处理、异步审查、设置超时"
  },

  {
    pitfall: "缺乏上下文",
    description: "AI 只看到单个文件",
    consequence: "审查质量差",
    solution: "提供充分上下文、使用 CLAUDE.md"
  }
];
```

---

## 34.9 练习

### 练习 1：基础 AI 审查

创建一个简单的 AI 代码审查工作流：
1. 检测 PR 变更
2. 调用 Claude Code 审查
3. 发布评论

### 练习 2：测试生成

实现自动测试生成：
1. 识别没有测试的文件
2. 使用 AI 生成测试
3. 运行并验证测试

### 练习 3：文档生成

创建文档生成工作流：
1. 监听 API 文件变更
2. 生成 OpenAPI 文档
3. 自动提交

### 练习 4：依赖管理

实现智能依赖升级：
1. 检查过时的依赖
2. AI 分析升级风险
3. 创建建议 Issue

---

## 34.10 进一步阅读

- [Chapter 35: Enterprise Integration](chapter-35-enterprise-integration.md) - 下一章
- [Chapter 36: The Future of AI-Assisted Coding](chapter-36-future-of-ai-coding.md) - 未来趋势
- [Claude Code 官方文档](https://docs.anthropic.com/claude-code/) - 官方指南

---

## 视频脚本

### Episode 34: Claude Code in CI/CD (20 分钟)

#### [0:00-1:00] 引入

**视觉元素**：
- 标题："CI/CD 中的 AI：自动化代码审查"
- CI/CD 管道图

**内容**：
> CI/CD 是现代软件开发的基石。
>
> 将 Claude Code 集成到 CI/CD 管道中，让 AI 成为持续集成流程的一部分。
>
> 这可以自动化代码审查、生成测试、更新文档。

#### [1:00-5:00] AI 代码审查

**视觉元素**：
- GitHub Actions 工作流示例
- 审查流程图

**内容**：
> **AI 代码审查工作流**：
>
> 1. 检测 PR 事件
> 2. 获取变更文件
> 3. 调用 Claude Code 审查
> 4. 解析审查结果
> 5. 发布 PR 评论
>
> [展示完整的 GitHub Actions 配置]
>
> 关键要点：
> - 使用 secrets 管理 API 密钥
> - 只审查变更的文件
> - 结构化输出便于解析

#### [5:00-9:00] 测试生成

**视觉元素**：
- 测试生成工作流
- 覆盖率报告

**内容**：
> **自动化测试生成**：
>
> 1. 识别没有测试的文件
> 2. 读取源代码
> 3. 使用 AI 生成测试
> 4. 运行并验证测试
> 5. 创建 PR 提交测试
>
> **测试覆盖率增强**：
> - 分析未覆盖的代码
> - 为未覆盖分支生成测试
> - 提高整体覆盖率
>
> [展示测试生成配置]

#### [9:00-13:00] 文档生成

**视觉元素**：
- API 文档示例
- README 生成

**内容**：
> **文档自动化**：
>
> **API 文档**：
> - 监听 API 文件变更
> - 生成 OpenAPI 规范
> - 更新 API 文档
>
> **项目文档**：
> - README 自动生成
> - 贡献指南更新
> - 变更日志维护
>
> [展示文档生成工作流]

#### [13:00-16:00] 依赖管理

**视觉元素**：
- 依赖分析流程
- 升级建议示例

**内容**：
> **智能依赖管理**：
>
> 1. 定期检查过时依赖
> 2. AI 分析升级风险
> 3. 考虑 breaking changes
> 4. 生成升级建议
> 5. 创建 Issue 跟踪
>
> 分析考虑：
> - 安全漏洞
> - 性能改进
> - 维护状态
> - 升级复杂度

#### [16:00-20:00] 最佳实践与总结

**视觉元素**：
- 性能优化技巧
- 安全检查清单

**内容**：
> **最佳实践**：
>
> **性能优化**：
> - 缓存 AI 响应
> - 增量处理
> - 并行执行
>
> **成本控制**：
> - 选择合适模型
> - 限制审查范围
> - 批处理请求
>
> **安全考虑**：
> - 扫描敏感信息
> - 使用 OIDC
> - 审查 AI 输出
>
> **常见陷阱**：
> 1. ❌ 过度依赖 AI
> 2. ❌ 忽视成本
> 3. ❌ 泄露敏感信息
> 4. ❌ 延长 CI 时间
>
> **总结**：
> CI/CD 中的 AI 应该是**辅助**而非**替代**。人类仍然做最终决策。
>
> 下一章，我们将学习企业级集成。
