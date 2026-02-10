# Chapter 31: 创建 CLAUDE.md 模板

## 学习目标

完成本章后，你将能够：

- 理解 CLAUDE.md 的结构和最佳实践
- 创建适合你项目的 CLAUDE.md 模板
- 针对不同技术栈定制 CLAUDE.md
- 迭代优化 CLAUDE.md 内容
- 避免常见的 CLAUDE.md 错误

## 前置知识

- [Chapter 26: Boris Power 官方建议](../module-07-expert-wisdom/chapter-26-boris-power.md)
- [Chapter 30: 评估你的需求](chapter-30-assessing-needs.md)

---

## 31.1 CLAUDE.md 的价值

```typescript
/**
 * CLAUDE.md：AI 辅助开发的"项目记忆"
 */

const claudeMdValue = {
  definition: `
    CLAUDE.md 是一个特殊的 Markdown 文件，
    Claude Code 会自动读取它作为项目上下文。

    它就像是项目的"记忆"和"说明书"，
    帮助 AI 更好地理解你的代码库。
  `,

  benefits: [
    "提供项目上下文 - 无需反复解释",
    "定义编码规范 - 保持代码一致性",
    "说明架构设计 - AI 理解整体结构",
    "列出常用命令 - 快速执行任务",
    "强调重要事项 - 避免常见错误",
    "加速新项目上手 - 快速启动开发"
  ],

  impact: `
    好的 CLAUDE.md 可以：
    - 减少提示词长度 30-50%
    - 提高输出相关性 40-60%
    - 减少迭代次数 50-70%
    - 提升 AI 辅助效率 2-3 倍
  `
};
```

---

## 31.2 CLAUDE.md 的结构

### 31.2.1 核心组件

```typescript
/**
 * CLAUDE.md 的标准结构
 */

interface ClaudeMdStructure {
  // 1. 项目概述
  overview: string;

  // 2. 技术栈
  techStack: {
    language: string;
    framework: string;
    buildTool: string;
    testing: string;
    other: string[];
  };

  // 3. 项目结构
  projectStructure: string;

  // 4. 架构说明
  architecture: {
    pattern: string;
    keyPrinciples: string[];
    diagram?: string;
  };

  // 5. 编码规范
  codingStandards: {
    style: string;
    naming: string;
    patterns: string[];
    antiPatterns: string[];
  };

  // 6. 常用命令
  commands: {
    dev: string;
    build: string;
    test: string;
    lint: string;
    other: Record<string, string>;
  };

  // 7. 重要提醒
  importantNotes: string[];

  // 8. 开发指南
  developmentGuide?: {
    setup: string;
    workflow: string;
    debugging: string;
  };
}
```

### 31.2.2 完整模板

```markdown
# CLAUDE.md 模板

## 项目概述

[简要描述项目是什么，它的目标用户，主要功能]

- **项目名称**: [项目名称]
- **项目类型**: [Web 应用 / CLI 工具 / 库 / 等]
- **主要功能**: [2-3 句话描述核心功能]
- **目标用户**: [谁使用这个项目]
- **当前状态**: [开发中 / 生产中 / 维护模式]

## 技术栈

### 核心技术
- **语言**: [TypeScript 5.3+ / Python 3.11 / 等]
- **框架**: [React 18 / Next.js 14 / Express / Django / 等]
- **构建工具**: [Vite / Webpack / esbuild / 等]

### 依赖
- **状态管理**: [Redux / Zustand / Pinia / 等]
- **UI 库**: [Tailwind CSS / Material-UI / Ant Design / 等]
- **数据库**: [PostgreSQL / MongoDB / 等]
- **ORM**: [Prisma / TypeORM / SQLAlchemy / 等]

### 开发工具
- **包管理器**: [pnpm / npm / yarn]
- **代码质量**: [ESLint + Prettier / Black / Ruff / 等]
- **测试**: [Jest / Vitest / Pytest / 等]
- **版本控制**: [Git + GitHub]

## 项目结构

```
project-root/
├── src/
│   ├── components/     # [描述组件组织方式]
│   ├── pages/          # [页面或路由]
│   ├── services/       # [API 和业务逻辑]
│   ├── utils/          # [工具函数]
│   ├── types/          # [类型定义]
│   └── index.[ext]     # [入口文件]
├── tests/              # [测试文件]
├── docs/               # [文档]
└── [其他重要目录]
```

## 架构说明

### 架构模式
[描述使用的架构模式：整洁架构 / 洋葱架构 / MVC / 等]

### 关键原则
1. [原则 1 - 例如：依赖倒置]
2. [原则 2 - 例如：单一职责]
3. [原则 3 - 例如：接口隔离]

### 层次结构
[描述代码如何分层]

```
[表示层]
    ↓
[应用层]
    ↓
[领域层]
    ↓
[基础设施层]
```

## 编码规范

### 代码风格
- [遵循的代码风格指南：例如 Airbnb Style Guide]
- [使用 Prettier 配置：.prettierrc]
- [使用 ESLint 配置：.eslintrc]

### 命名约定
- **文件命名**: [kebab-case / camelCase / PascalCase]
- **变量命名**: [camelCase / snake_case]
- **常量命名**: [UPPER_SNAKE_CASE]
- **类/组件命名**: [PascalCase]
- **接口命名**: [PascalCase with I prefix / without I prefix]

### 设计模式
[鼓励使用的设计模式]
- [例如：Factory Pattern]
- [例如：Observer Pattern]
- [例如：Repository Pattern]

### 反模式
[避免使用或谨慎使用的模式]
- [例如：避免 God Objects]
- [例如：避免深层嵌套]
- [例如：避免直接操作 DOM]

## 常用命令

### 开发
```bash
# 启动开发服务器
pnpm dev

# 启动生产构建
pnpm start
```

### 构建
```bash
# 开发构建
pnpm build:dev

# 生产构建
pnpm build
```

### 测试
```bash
# 运行所有测试
pnpm test

# 运行测试并监听
pnpm test:watch

# 运行测试覆盖率
pnpm test:coverage
```

### 代码质量
```bash
# Lint 代码
pnpm lint

# 自动修复 Lint 问题
pnpm lint:fix

# 格式化代码
pnpm format
```

### 其他命令
```bash
[其他常用命令]
```

## 重要提醒

### 必须遵守
- [ ] [重要规则 1 - 例如：所有 API 调用必须通过 services 层]
- [ ] [重要规则 2 - 例如：绝不在组件中直接调用第三方 API]
- [ ] [重要规则 3 - 例如：所有新代码必须有测试]

### 安全注意事项
- [ ] [安全考虑 1 - 例如：API 密钥必须使用环境变量]
- [ ] [安全考虑 2 - 例如：用户输入必须验证和清理]

### 性能注意事项
- [ ] [性能考虑 1 - 例如：大列表必须使用虚拟滚动]
- [ ] [性能考虑 2 - 例如：图片必须优化和懒加载]

## 开发指南

### 环境设置
[描述如何设置开发环境]

### 开发工作流
[描述推荐的开发流程]

### 调试技巧
[描述有用的调试技巧]

## 相关资源

- [项目文档链接]
- [API 文档链接]
- [设计规范链接]
- [部署指南链接]

## 联系方式

- [项目负责人]
- [团队沟通渠道]
- [问题反馈方式]
```

---

## 31.3 针对不同项目的模板

### 31.3.1 React/Next.js 项目

```markdown
# CLAUDE.md - React/Next.js 项目

## 项目概述
[项目描述]

## 技术栈
- **框架**: Next.js 14 (App Router)
- **语言**: TypeScript 5.3+
- **样式**: Tailwind CSS
- **状态管理**: Zustand
- **表单**: React Hook Form + Zod
- **API**: Next.js Route Handlers
- **数据库**: PostgreSQL + Prisma

## 项目结构
```
app/
├── (auth)/           # 认证路由组
│   ├── login/
│   └── register/
├── (dashboard)/      # 主应用路由组
│   ├── dashboard/
│   └── settings/
├── api/              # API 路由
├── layout.tsx        # 根布局
└── page.tsx          # 首页
components/
├── ui/               # 可复用 UI 组件
├── forms/            # 表单组件
└── features/         # 功能特定组件
lib/
├── db.ts             # 数据库客户端
├── auth.ts           # 认证逻辑
└── utils.ts          # 工具函数
hooks/                # 自定义 Hooks
types/                # TypeScript 类型
prisma/
└── schema.prisma     # 数据库模型
```

## 架构原则
1. **服务端优先**: 尽可能在服务端处理逻辑
2. **组件最小化**: 保持组件小而专注
3. **类型安全**: 所有数据必须有类型定义
4. **错误边界**: 关键路由使用错误边界

## 编码规范

### 组件规范
```typescript
// ✅ 好的组件
interface UserProfileProps {
  userId: string;
  onUpdate?: () => void;
}

export function UserProfile({ userId, onUpdate }: UserProfileProps) {
  // 组件逻辑
}
```

### Hooks 使用
- 优先使用 Next.js 内置 Hooks（useParams, usePathname）
- 自定义 Hooks 放在 `hooks/` 目录
- Hooks 命名以 "use" 开头

### 数据获取
- 使用 Server Components 获取数据
- 客户端数据使用 SWR 或 React Query
- 所有 API 调用通过 `lib/api/` 模块

## 常用命令
```bash
pnpm dev          # 开发服务器
pnpm build        # 生产构建
pnpm lint         # ESLint
pnpm test         # Vitest
pnpm db:push      # 推送 schema 到数据库
pnpm db:studio    # 打开 Prisma Studio
```

## 重要提醒
- 所有表单必须使用 React Hook Form + Zod 验证
- Server Actions 用于数据变更
- 客户端组件必须添加 'use client' 指令
- API 路由必须验证用户身份
```

### 31.3.2 Node.js/Express API 项目

```markdown
# CLAUDE.md - Node.js API 项目

## 项目概述
[项目描述]

## 技术栈
- **运行时**: Node.js 20+
- **框架**: Express 4.x
- **语言**: TypeScript 5.3+
- **数据库**: PostgreSQL
- **ORM**: TypeORM
- **认证**: JWT + Passport.js
- **验证**: Joi / Zod
- **日志**: Winston / Pino
- **测试**: Jest + Supertest

## 项目结构
```
src/
├── controllers/     # 请求处理逻辑
├── services/        # 业务逻辑
├── repositories/    # 数据访问层
├── models/          # 数据模型
├── middlewares/     # Express 中间件
├── routes/          # 路由定义
├── utils/           # 工具函数
├── config/          # 配置文件
├── types/           # TypeScript 类型
└── index.ts         # 应用入口
tests/
├── unit/            # 单元测试
├── integration/     # 集成测试
└── fixtures/        # 测试数据
```

## 架构模式
采用分层架构：

```
Routes → Controllers → Services → Repositories → Models
```

- **Routes**: 定义端点和中间件
- **Controllers**: 处理请求/响应
- **Services**: 业务逻辑
- **Repositories**: 数据库操作
- **Models**: 数据模型定义

## 编码规范

### 错误处理
```typescript
// ✅ 统一错误处理
export class AppError extends Error {
  constructor(
    public statusCode: number,
    public message: string,
    public isOperational = true
  ) {
    super(message);
  }
}

// 在控制器中
throw new AppError(404, 'User not found');
```

### 异步处理
```typescript
// ✅ 使用 async/await
router.get('/users/:id', async (req, res, next) => {
  try {
    const user = await userService.findById(req.params.id);
    res.json(user);
  } catch (error) {
    next(error);
  }
});
```

### 验证
```typescript
// ✅ 请求数据验证
const userSchema = Joi.object({
  email: Joi.string().email().required(),
  password: Joi.string().min(8).required(),
});

router.post('/users', validateRequest(userSchema), createUserController);
```

## 常用命令
```bash
pnpm dev           # 开发模式（nodemon）
pnpm build         # 构建 JavaScript
pnpm start         # 生产模式
pnpm test          # 运行测试
pnpm test:watch    # 监听模式测试
pnpm lint          # ESLint
pnpm migrate       # 运行数据库迁移
pnpm seed          # 种子数据
```

## 重要提醒
- 所有路由必须验证请求
- 敏感操作必须验证 JWT
- 数据库查询使用参数化（防 SQL 注入）
- 所有密码使用 bcrypt 哈希
- API 响应使用统一格式
```

### 31.3.3 Python/Django 项目

```markdown
# CLAUDE.md - Django 项目

## 项目概述
[项目描述]

## 技术栈
- **Python**: 3.11+
- **框架**: Django 5.0
- **数据库**: PostgreSQL
- **ORM**: Django ORM
- **认证**: Django Auth + JWT
- **API**: Django REST Framework
- **任务队列**: Celery + Redis
- **测试**: Pytest + Factory Boy
- **代码质量**: Black, Ruff, isort

## 项目结构
```
config/             # Django 设置
├── settings/
│   ├── base.py
│   ├── development.py
│   └── production.py
├── urls.py
└── wsgi.py
apps/
├── users/          # 用户应用
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
├── products/       # 产品应用
└── orders/         # 订单应用
core/
├── permissions.py  # 自定义权限
├── pagination.py   # 分页
└── utils.py        # 工具函数
templates/          # 模板
static/             # 静态文件
media/              # 用户上传文件
```

## 架构原则
1. **应用独立性**: 每个 Django 应用是自包含的
2. **瘦视图，胖模型**: 业务逻辑放在模型中
3. **序列化器验证**: 所有输入验证在序列化器中

## 编码规范

### 模型设计
```python
# ✅ 好的模型
from django.db import models
from django.core.validators import MinValueValidator

class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['name']),
        ]

    def __str__(self):
        return self.name
```

### 视图和序列化器
```python
# ✅ 使用 ViewSets 和序列化器
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
```

### 查询优化
```python
# ✅ 优化查询
# 避免 N+1 查询
products = Product.objects.select_related('category').prefetch_related('tags')

# 使用 exists() 而不是 count()
if Product.objects.filter(name='Test').exists():
    pass
```

## 常用命令
```bash
python manage.py runserver     # 开发服务器
python manage.py migrate       # 运行迁移
python manage.py makemigrations  # 创建迁移
python manage.py createsuperuser  # 创建管理员
python -m pytest               # 运行测试
ruff check .                   # Lint
black .                        # 格式化
```

## 重要提醒
- 永远不要直接运行 `python manage.py shell --settings=settings.production`
- 所有敏感配置使用环境变量
- 使用 Django 的迁移系统，不要手动修改数据库
- 生产环境必须设置 DEBUG=False
- 使用 ALLOWED_HOSTS 限制访问
```

### 31.3.4 Go 项目

```markdown
# CLAUDE.md - Go 项目

## 项目概述
[项目描述]

## 技术栈
- **Go**: 1.21+
- **框架**: Gin / Chi / Fiber
- **数据库**: PostgreSQL
- **ORM**: GORM
- **配置**: Viper
- **日志**: zap / logrus
- **测试**: testing 包 + testify

## 项目结构
```
cmd/
└── server/
    └── main.go         # 应用入口
internal/
├── api/                # HTTP 处理器
│   ├── handler/
│   ├── middleware/
│   └── router/
├── domain/             # 领域逻辑
│   ├── entity/
│   ├── repository/
│   └── service/
├── infrastructure/     # 基础设施
│   ├── database/
│   ├── config/
│   └── logger/
├── pkg/                # 可复用包
└── configs/            # 配置文件
go.mod
go.sum
```

## 架构原则
1. **清洁架构**: 依赖方向向内
2. **接口隔离**: 定义清晰的接口
3. **错误处理**: 显式处理所有错误

## 编码规范

### 错误处理
```go
// ✅ 好的错误处理
func (s *UserService) GetUser(id string) (*User, error) {
    user, err := s.repo.FindByID(id)
    if err != nil {
        if errors.Is(err, ErrNotFound) {
            return nil, ErrUserNotFound
        }
        return nil, fmt.Errorf("failed to get user: %w", err)
    }
    return user, nil
}
```

### 接口定义
```go
// ✅ 定义清晰的接口
type UserRepository interface {
    FindByID(ctx context.Context, id string) (*User, error)
    Create(ctx context.Context, user *User) error
    Update(ctx context.Context, user *User) error
    Delete(ctx context.Context, id string) error
}
```

### 并发模式
```go
// ✅ 使用 context 和 goroutines
func (s *Service) ProcessItems(ctx context.Context, items []Item) error {
    errChan := make(chan error, len(items))
    var wg sync.WaitGroup

    for _, item := range items {
        wg.Add(1)
        go func(i Item) {
            defer wg.Done()
            if err := s.processItem(ctx, i); err != nil {
                errChan <- err
            }
        }(item)
    }

    wg.Wait()
    close(errChan)

    for err := range errChan {
        if err != nil {
            return err
        }
    }
    return nil
}
```

## 常用命令
```bash
go run cmd/server/main.go    # 运行应用
go build -o bin/server       # 构建
go test ./...                # 运行测试
go test -race ./...          # 竞态检测
go vet ./...                 # 静态分析
golangci-lint run            # Lint
go mod tidy                  # 整理依赖
```

## 重要提醒
- 总是检查错误
- 使用 context 管理生命周期
- 避免全局状态
- 使用 interface{} 作为最后手段
- 生产代码不要使用 panic
```

---

## 31.4 CLAUDE.md 优化技巧

### 31.4.1 迭代式优化

```typescript
/**
 * CLAUDE.md 是活的文档，持续优化
 */

const claudeMdOptimization = {
  phase1: {
    name: "第 1 版：基础框架（第 1 天）",
    content: [
      "项目概述",
      "技术栈列表",
      "基本目录结构",
      "启动命令"
    ],
    effort: "30-60 分钟"
  },

  phase2: {
    name: "第 2 版：补充细节（第 1 周）",
    additions: [
      "编码规范",
      "命名约定",
      "常用命令完整列表",
      "开发工作流说明"
    ],
    effort: "持续添加，每次 5-10 分钟"
  },

  phase3: {
    name: "第 3 版：深度定制（第 2-4 周）",
    additions: [
      "架构图示",
      "设计模式说明",
      "常见问题和解决方案",
      "代码示例",
      "团队特定约定"
    ],
    effort: "根据实际需求持续优化"
  },

  phase4: {
    name: "第 4 版：维护更新（持续）",
    maintenance: [
      "更新技术栈变化",
      "添加新学习到的最佳实践",
      "移除过时信息",
      "根据 AI 交互反馈优化"
    ],
    effort: "每次技术变更时更新"
  }
};
```

### 31.4.2 使用强调标记

```markdown
# CLAUDE.md - 强调重要内容

## 使用 # 标记关键信息

### # 重要：数据库迁移
# 所有数据库更改必须通过迁移！
# 永远不要手动修改生产数据库

### # 关键：API 认证
# 所有 API 端点必须验证 JWT Token
# 使用中间件：requireAuth

### # 警告：敏感数据
# API 密钥必须存储在环境变量中
# 永远不要提交到代码库

### # 注意：性能
# 大数据集必须使用分页
# 默认每页 20 条记录
```

### 31.4.3 提供代码示例

```markdown
# CLAUDE.md - 代码示例

## 组件示例

```typescript
// ✅ 推荐的组件结构
interface Props {
  title: string;
  onAction: () => void;
}

export function MyComponent({ title, onAction }: Props) {
  return (
    <div className="p-4 border rounded">
      <h2 className="text-xl font-bold">{title}</h2>
      <button onClick={onAction}>
        Click me
      </button>
    </div>
  );
}
```

## API 调用示例

```typescript
// ✅ 正确的 API 调用方式
import { apiClient } from '@/lib/api-client';

export async function getUser(id: string) {
  return apiClient.get(`/users/${id}`);
}
```

## 测试示例

```typescript
// ✅ 测试结构
describe('UserService', () => {
  it('should create a user', async () => {
    const user = await userService.create({
      name: 'John',
      email: 'john@example.com',
    });

    expect(user).toHaveProperty('id');
    expect(user.name).toBe('John');
  });
});
```
```

### 31.4.4 常见问题 FAQ

```markdown
## 常见问题

### Q: 如何添加新的 API 端点？
**A:**
1. 在 `routes/api/` 创建路由文件
2. 在 `controllers/` 创建控制器
3. 在 `services/` 实现业务逻辑
4. 在 `repositories/` 处理数据访问
5. 添加测试
6. 更新 API 文档

### Q: 如何处理数据库迁移？
**A:**
```bash
pnpm db:push     # 开发环境（直接推送）
pnpm db:migrate  # 生产环境（创建迁移文件）
```

### Q: 为什么我的测试失败了？
**A:** 检查以下几点：
1. 数据库种子数据是否正确
2. 环境变量是否设置
3. 依赖是否正确安装
4. 测试数据库是否隔离
```

---

## 31.5 团队协作

### 31.5.1 共享 CLAUDE.md

```typescript
/**
 * 团队使用 CLAUDE.md 的最佳实践
 */

const teamCollaboration = {
  placement: {
    recommended: `
      推荐：将 CLAUDE.md 放在项目根目录

      优点：
      - 所有团队成员共享
      - Git 版本控制
      - 单一真相来源
    `,

    alternative: `
      备选：团队共享 CLAUDE.md 模板

      场景：
      - 不同项目有特殊需求
      - 个人有特定偏好

      实现：
      - 在团队文档中维护模板
      - 每个项目根据需要调整
    `
  },

  maintenance: {
    responsibility: `
      指定维护者：
      - 技术负责人
      - 或轮流负责

      定期审查：
      - 每月检查一次
      - 根据技术更新
      - 根据团队反馈
    `,

    updates: `
      更新流程：
      1. 提出变更建议
      2. 团队讨论
      3. 达成一致
      4. 更新 CLAUDE.md
      5. 通知团队变更
    `
  },

  onboarding: `
    新成员入职：
    1. 解释 CLAUDE.md 的作用
    2. 逐节讲解内容
    3. 示范如何使用
    4. 鼓励提出改进建议
  `
};
```

### 31.5.2 版本控制

```markdown
# .github/PULL_REQUEST_TEMPLATE.md

## CLAUDE.md 检查清单

提交 PR 时，确认：

- [ ] 如果技术栈变更，已更新 CLAUDE.md
- [ ] 如果新增命令，已添加到"常用命令"部分
- [ ] 如果架构变更，已更新"架构说明"
- [ ] 如果新有编码规范，已添加到"编码规范"
- [ ] 如果发现有用模式，已添加到"设计模式"

## CLAUDE.md 变更

如果此 PR 影响 CLAUDE.md，描述变更：
```

---

## 31.6 常见错误和修复

```typescript
/**
 * 避免 CLAUDE.md 的常见错误
 */

const commonMistakes = [
  {
    mistake: "信息过载",
    description: "CLAUDE.md 太长太详细",
    consequence: "AI 可能忽略关键信息",
    fix: `
      修复：
      - 保持简洁
      - 只包含关键信息
      - 详细文档放在其他文件
      - 使用链接引用
    `
  },

  {
    mistake: "信息过时",
    description: "技术栈变更后未更新",
    consequence: "AI 生成过时代码",
    fix: `
      修复：
      - 技术变更时立即更新
      - 定期审查 CLAUDE.md
      - 在 PR 模板中提醒
    `
  },

  {
    mistake: "缺少上下文",
    description: "只列出技术，没有说明用法",
    consequence: "AI 不了解项目特定约定",
    fix: `
      修复：
      - 添加代码示例
      - 说明项目特定模式
      - 解释架构决策
    `
  },

  {
    mistake: "过于通用",
    description: "使用模板而不定制",
    consequence: "CLAUDE.md 没有项目特定价值",
    fix: `
      修复：
      - 添加项目特定信息
      - 说明团队约定
      - 包含实际代码示例
    `
  },

  {
    mistake: "缺少架构说明",
    description: "只列目录结构",
    consequence: "AI 不理解代码关系",
    fix: `
      修复：
      - 添加架构图
      - 解释层次关系
      - 说明数据流
    `
  }
];
```

---

## 31.7 练习

### 练习 1：创建基础 CLAUDE.md

为你当前的项目创建一个基础的 CLAUDE.md：
1. 项目概述
2. 技术栈
3. 目录结构
4. 启动命令

### 练习 2：优化现有 CLAUDE.md

如果你已有 CLAUDE.md，评估并优化：
1. 信息是否最新？
2. 是否缺少关键部分？
3. 是否需要代码示例？
4. 是否有信息过载？

### 练习 3：团队 CLAUDE.md

如果你在团队中工作：
1. 比较团队成员的 CLAUDE.md
2. 识别共同模式和差异
3. 创建团队共享模板
4. 建立维护流程

### 练习 4：迭代改进

跟踪你使用 Claude Code 的体验：
1. 哪些问题重复出现？
2. 哪些指令经常需要重复？
3. 将这些添加到 CLAUDE.md
4. 测试改进效果

---

## 31.8 进一步阅读

- [Chapter 30: 评估你的需求](chapter-30-assessing-needs.md) - 上一章
- [Chapter 32: 设置工具集](chapter-32-toolkit-setup.md) - 下一章
- [Claude Code 官方文档：CLAUDE.md](https://docs.anthropic.com/claude-code/) - 官方指南

---

## 视频脚本

### Episode 31: 创建 CLAUDE.md 模板 (18 分钟)

#### [0:00-1:00] 引入

**视觉元素**：
- 标题："CLAUDE.md：AI 的项目记忆"
- CLAUDE.md 文件示例

**内容**：
> CLAUDE.md 是 AI 辅助开发中最重要的配置文件。
>
> 它是你的项目"记忆"和"说明书"，帮助 Claude 更好地理解你的代码库。
>
> 好的 CLAUDE.md 可以将 AI 辅助效率提升 2-3 倍。

#### [1:00-4:00] 标准结构

**视觉元素**：
- CLAUDE.md 8 个核心部分
- 每部分的解释

**内容**：
> **CLAUDE.md 的 8 个核心部分**：
>
> 1. **项目概述** - 这是什么项目？
> 2. **技术栈** - 使用什么技术？
> 3. **项目结构** - 代码如何组织？
> 4. **架构说明** - 代码如何协作？
> 5. **编码规范** - 如何写代码？
> 6. **常用命令** - 如何执行任务？
> 7. **重要提醒** - 必须遵守什么？
> 8. **开发指南** - 如何开始开发？
>
> [展示完整模板]

#### [4:00-8:00] 不同项目的模板

**视觉元素**：
- React/Next.js 模板
- Node.js API 模板
- Python/Django 模板
- Go 模板

**内容**：
> 不同技术栈需要不同的 CLAUDE.md 侧重点。
>
> **React/Next.js**：
> - 强调组件结构
> - 说明路由组织
> - App Router vs Pages Router
>
> **Node.js API**：
> - 强调分层架构
> - 错误处理模式
> - 中间件使用
>
> **Python/Django**：
> - 强调应用结构
> - ORM 使用
> - 迁移管理
>
> **Go**：
> - 强调项目布局
> - 接口设计
> - 错误处理模式
>
> [展示各技术栈的关键差异]

#### [8:00-11:00] 优化技巧

**视觉元素**：
- 迭代式优化时间线
- 强调标记示例
- 代码示例

**内容**：
> **优化技巧 #1：迭代式优化**
>
> - 第 1 天：基础框架（30-60 分钟）
> - 第 1 周：补充细节（持续添加）
> - 第 2-4 周：深度定制（根据需求）
> - 持续：维护更新（技术变更时）
>
> **优化技巧 #2：使用强调标记**
>
> ```markdown
> ### # 重要：数据库迁移
> # 所有数据库更改必须通过迁移！
> ```
>
> **优化技巧 #3：提供代码示例**
>
> 展示期望的代码风格比描述更有效。

#### [11:00-14:00] 团队协作

**视觉元素**：
- 团队使用场景
- 版本控制策略

**内容**：
> **团队协作**：
>
> **共享策略**：
> - 项目根目录：团队共享
> - 团队文档：模板和指南
>
> **维护责任**：
> - 指定维护者
> - 定期审查
> - PR 时检查更新
>
> **新成员入职**：
> - 解释 CLAUDE.md 作用
> - 逐节讲解内容
> - 示范如何使用

#### [14:00-16:00] 常见错误

**视觉元素**：
- 错误列表
- 修复建议

**内容**：
> **常见错误**：
>
> 1. ❌ 信息过载 → ✅ 保持简洁
> 2. ❌ 信息过时 → ✅ 及时更新
> 3. ❌ 缺少上下文 → ✅ 添加示例
> 4. ❌ 过于通用 → ✅ 定制内容
> 5. ❌ 缺少架构说明 → ✅ 解释设计
>
> **核心原则**：
> CLAUDE.md 应该是"够用"的 - 包足够的信息，但不过量。

#### [16:00-18:00] 总结

**视觉元素**：
- 最佳实践总结
- 下一章预告

**内容**：
> **CLAUDE.md 最佳实践**：
>
> 1. ✅ 从基础框架开始
> 2. ✅ 持续迭代优化
> 3. ✅ 使用强调标记
> 4. ✅ 提供代码示例
> 5. ✅ 定期更新维护
> 6. ✅ 团队共享使用
>
> **记住**：CLAUDE.md 是活的文档，随着项目成长。
>
> 下一章，我们将学习如何设置完整的工具集。
