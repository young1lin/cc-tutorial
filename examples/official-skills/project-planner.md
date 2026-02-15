# Skill: project-planner

## 概述

`project-planner` 是企业级项目规划系统 Skill，能够生成需求文档（Requirements）、设计文档（Design）和实施文档（Implementation）。它支持需求追踪、领域模板和整洁架构模式，将复杂系统分解为可实施的任务。

**核心输出**:
- **需求文档（PRD）**: 功能和非功能需求
- **技术设计文档**: 架构、数据模型、API 设计
- **实施计划**: 分解为可执行的 TODO 列表

---

## 触发方式

### 斜杠命令

```bash
/project-planner
```

### 自然语言触发

```
"为 [功能/产品] 创建需求文档"
"规划 [项目名] 项目"
"设计 [功能] 的技术方案"
"帮我写 PRD"
"分解这个功能的实现任务"
```

---

## 工作原理

```
1. 理解项目背景
   ├─ 产品目标
   ├─ 目标用户
   ├─ 技术栈
   └─ 约束条件

2. 生成需求文档
   ├─ 功能需求（用例）
   ├─ 非功能需求（性能、安全）
   └─ 验收标准

3. 生成设计文档
   ├─ 系统架构
   ├─ 数据模型
   ├─ API 设计
   └─ 依赖关系

4. 生成实施计划
   ├─ 任务分解
   ├─ 优先级排序
   ├─ 工时估算
   └─ 里程碑定义

5. 需求追踪矩阵
   └─ 需求 → 设计 → 实施 的映射关系
```

---

## 实际演示

### 示例 1: 用户通知系统 PRD

**用户请求**:
```
为用户通知系统创建完整的规划文档：
- 发送邮件和推送通知
- 用户可以设置通知偏好
- 管理员可以创建通知模板
技术栈：Node.js + PostgreSQL + Redis
```

**生成的文档**:

---

#### 需求文档（Requirements）

```markdown
# 用户通知系统 - 需求文档

**版本**: 1.0.0
**状态**: 草稿
**最后更新**: 2026-02-10

---

## 1. 项目背景

### 1.1 问题陈述

当前系统缺乏统一的通知机制，导致：
- 用户无法及时收到重要更新
- 开发者重复实现各自的通知逻辑
- 无法追踪通知发送状态

### 1.2 目标

建立统一、可扩展的通知系统，支持多渠道（邮件/推送/站内信）通知。

### 1.3 成功指标

- 通知送达率 > 99.5%
- 平均延迟 < 1 秒（实时通知）
- 用户偏好设置完成率 > 70%

---

## 2. 用户角色

| 角色 | 描述 |
|------|------|
| 普通用户 | 接收通知，管理个人通知偏好 |
| 管理员 | 创建通知模板，查看发送统计 |
| 开发者 | 通过 API 触发通知 |

---

## 3. 功能需求

### FR-001: 通知发送

**优先级**: P0 (必须)

| 需求ID | 描述 | 验收标准 |
|--------|------|---------|
| FR-001-1 | 支持邮件通知 | 通过 SMTP/SES 发送 HTML 邮件 |
| FR-001-2 | 支持推送通知 | 集成 FCM/APNs，支持 iOS/Android |
| FR-001-3 | 支持站内信 | 实时推送，持久化存储 |
| FR-001-4 | 批量发送 | 单次最多 10,000 个接收者 |
| FR-001-5 | 定时发送 | 支持指定时间发送 |

### FR-002: 通知模板

**优先级**: P0 (必须)

| 需求ID | 描述 | 验收标准 |
|--------|------|---------|
| FR-002-1 | 创建模板 | 支持 Markdown + 变量占位符 |
| FR-002-2 | 模板版本 | 支持版本历史和回滚 |
| FR-002-3 | 多语言支持 | 每个模板支持多语言版本 |
| FR-002-4 | 预览功能 | 创建时可预览实际效果 |

### FR-003: 用户偏好

**优先级**: P1 (重要)

| 需求ID | 描述 | 验收标准 |
|--------|------|---------|
| FR-003-1 | 渠道偏好 | 可选择接收哪些渠道的通知 |
| FR-003-2 | 类型偏好 | 可关闭特定类型的通知 |
| FR-003-3 | 静默时段 | 设置不打扰时间段 |
| FR-003-4 | 全局关闭 | 一键关闭所有通知 |

### FR-004: 通知历史

**优先级**: P1 (重要)

| 需求ID | 描述 | 验收标准 |
|--------|------|---------|
| FR-004-1 | 查看历史 | 展示最近 90 天的通知历史 |
| FR-004-2 | 已读状态 | 追踪通知的已读/未读状态 |
| FR-004-3 | 删除通知 | 用户可删除通知 |

---

## 4. 非功能需求

### NFR-001: 性能
- 实时通知延迟 < 1 秒（P99）
- 批量任务处理速度 > 1000条/秒
- API 响应时间 < 200ms（P95）

### NFR-002: 可靠性
- 通知发送成功率 > 99.5%
- 失败自动重试（最多 3 次）
- 重试间隔：1分钟、5分钟、30分钟

### NFR-003: 安全
- API 调用需要认证
- 敏感数据加密存储
- 日志中不记录通知内容

### NFR-004: 可扩展性
- 水平扩展支持
- 新渠道可插件化添加

---

## 5. 约束条件

- 技术栈：Node.js + PostgreSQL + Redis
- 邮件发送使用 AWS SES（成本控制）
- 初期不需要国际化（中文优先）
```

---

#### 设计文档（Design）

```markdown
# 用户通知系统 - 设计文档

---

## 1. 系统架构

```
┌────────────────────────────────────────────────────┐
│                   API Gateway                       │
└──────────────────────┬─────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│  Template    │ │Preference    │ │ History      │
│  Service     │ │ Service      │ │ Service      │
└──────┬───────┘ └──────┬───────┘ └──────┬───────┘
       │                │                │
       └────────────────┼────────────────┘
                        │
              ┌─────────▼─────────┐
              │  Notification     │
              │  Dispatcher       │
              └────────┬──────────┘
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│  Email       │ │  Push        │ │  In-App      │
│  Provider    │ │  Provider    │ │  Provider    │
│  (AWS SES)   │ │ (FCM/APNs)   │ │  (WebSocket) │
└──────────────┘ └──────────────┘ └──────────────┘
```

## 2. 数据模型

```sql
-- 通知模板
CREATE TABLE notification_templates (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name        VARCHAR(255) NOT NULL,
  type        VARCHAR(50) NOT NULL,  -- 'email' | 'push' | 'in_app'
  subject     VARCHAR(500),          -- 邮件主题/推送标题
  body        TEXT NOT NULL,          -- 支持 Handlebars 模板语法
  variables   JSONB DEFAULT '[]',     -- 变量定义
  version     INTEGER DEFAULT 1,
  is_active   BOOLEAN DEFAULT true,
  created_at  TIMESTAMP DEFAULT NOW(),
  updated_at  TIMESTAMP DEFAULT NOW()
);

-- 通知任务
CREATE TABLE notification_jobs (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  template_id  UUID REFERENCES notification_templates(id),
  recipients   JSONB NOT NULL,        -- [{ user_id, channel, address }]
  variables    JSONB DEFAULT '{}',    -- 模板变量值
  status       VARCHAR(20) DEFAULT 'pending',  -- pending/processing/done/failed
  scheduled_at TIMESTAMP,             -- 定时发送时间
  sent_at      TIMESTAMP,
  created_by   UUID NOT NULL,
  created_at   TIMESTAMP DEFAULT NOW()
);

-- 发送记录
CREATE TABLE notification_logs (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  job_id       UUID REFERENCES notification_jobs(id),
  user_id      UUID NOT NULL,
  channel      VARCHAR(50) NOT NULL,
  status       VARCHAR(20) NOT NULL,  -- success/failed/skipped
  error_msg    TEXT,
  attempts     INTEGER DEFAULT 1,
  delivered_at TIMESTAMP,
  created_at   TIMESTAMP DEFAULT NOW()
);

-- 用户偏好
CREATE TABLE notification_preferences (
  user_id      UUID PRIMARY KEY,
  email        BOOLEAN DEFAULT true,
  push         BOOLEAN DEFAULT true,
  in_app       BOOLEAN DEFAULT true,
  quiet_hours  JSONB DEFAULT '{"start": null, "end": null}',
  disabled_types JSONB DEFAULT '[]',  -- 关闭的通知类型
  updated_at   TIMESTAMP DEFAULT NOW()
);
```

## 3. API 设计

```yaml
# 发送通知
POST /api/v1/notifications/send
Authorization: Bearer {api_key}
{
  "template_id": "uuid",
  "recipients": [
    { "user_id": "uuid", "channels": ["email", "push"] }
  ],
  "variables": { "username": "张三", "action": "购买成功" },
  "scheduled_at": "2026-02-11T10:00:00Z"  # 可选
}

# 用户通知历史
GET /api/v1/notifications/history?page=1&size=20
Authorization: Bearer {user_token}

# 设置通知偏好
PUT /api/v1/notifications/preferences
Authorization: Bearer {user_token}
{
  "email": true,
  "push": false,
  "quiet_hours": { "start": "22:00", "end": "08:00" }
}
```
```

---

#### 实施计划（Implementation）

```markdown
# 用户通知系统 - 实施计划

---

## Sprint 1: 基础架构（1周）

### TODO: 后端开发者 A

- [ ] **[FR-001]** 初始化 Node.js 项目结构
  - 使用 Clean Architecture 分层
  - 配置 TypeScript + ESLint
  - 估时: 2h

- [ ] **[FR-001]** 创建 PostgreSQL 数据库 Schema
  - 执行迁移文件
  - 添加初始测试数据
  - 估时: 3h

- [ ] **[FR-001]** 实现 NotificationDispatcher 核心类
  - 策略模式支持多渠道
  - 队列化处理（Bull + Redis）
  - 估时: 8h

- [ ] **[FR-001-1]** 实现 EmailProvider
  - 集成 AWS SES SDK
  - HTML 邮件模板渲染
  - 估时: 4h

### TODO: 后端开发者 B

- [ ] **[FR-002]** 实现模板 CRUD API
  - POST/GET/PUT/DELETE /api/v1/templates
  - Handlebars 模板引擎集成
  - 估时: 6h

- [ ] **[FR-002-2]** 实现模板版本控制
  - 版本历史存储
  - 回滚 API
  - 估时: 4h

---

## Sprint 2: 核心功能（1周）

### TODO: 后端开发者 A

- [ ] **[FR-001-2]** 实现 PushProvider
  - FCM 集成（Android）
  - APNs 集成（iOS）
  - 估时: 8h

- [ ] **[FR-001-5]** 实现定时发送
  - Bull 延迟队列
  - 任务调度 API
  - 估时: 4h

### TODO: 后端开发者 B

- [ ] **[FR-003]** 实现用户偏好 API
  - GET/PUT /api/v1/preferences
  - 偏好过滤中间件
  - 估时: 6h

- [ ] **[NFR-002]** 实现失败重试机制
  - 指数退避算法
  - 最大重试次数配置
  - 估时: 4h

---

## Sprint 3: 历史记录与管理后台（1周）

### TODO: 前端开发者

- [ ] **[FR-004]** 通知历史列表页面
  - 分页、筛选功能
  - 已读/未读状态切换
  - 估时: 8h

- [ ] **[FR-003]** 通知偏好设置页面
  - 估时: 4h

- [ ] **[FR-001-3]** 站内信实时推送
  - WebSocket 集成
  - 未读消息角标
  - 估时: 8h

---

## 里程碑

| 里程碑 | 完成日期 | 交付内容 |
|--------|---------|---------|
| M1: 邮件通知可用 | 第1周末 | 可以发送邮件通知 |
| M2: 全渠道通知 | 第2周末 | 邮件+推送+站内信 |
| M3: 完整功能 | 第3周末 | 包含历史和偏好设置 |

---

## 需求追踪矩阵

| 需求ID | 设计文档 | 实施任务 | 状态 |
|--------|---------|---------|------|
| FR-001-1 | 架构图/EmailProvider | Sprint1/EmailProvider | ⬜ 待开始 |
| FR-001-2 | 架构图/PushProvider | Sprint2/PushProvider | ⬜ 待开始 |
| FR-002-1 | API设计/模板API | Sprint1/模板CRUD | ⬜ 待开始 |
| FR-003 | API设计/偏好API | Sprint2/偏好API | ⬜ 待开始 |
| NFR-001 | 架构图/队列设计 | Sprint1/Dispatcher | ⬜ 待开始 |
```

---

## 不同项目类型的模板

`project-planner` 针对不同领域有专门的模板：

### SaaS 产品

```bash
> 为我的 SaaS 项目规划一个订阅管理功能
```

重点：
- 用户生命周期
- 计费和退款逻辑
- 数据隔离

### 微服务架构

```bash
> 设计一个用户服务微服务的技术方案
```

重点：
- 服务边界
- 通信协议（gRPC/REST）
- 数据一致性

### 移动端 App

```bash
> 为移动端 App 规划一个离线支持功能
```

重点：
- 本地存储策略
- 同步机制
- 冲突解决

---

## 输出格式定制

```bash
# 只需要需求文档
> 为 [功能] 创建需求文档（PRD），不需要技术设计

# 只需要技术设计
> 为这个 PRD 创建技术设计文档

# 只需要任务分解
> 将这个设计分解为具体的实施任务

# 全套文档
> 为 [功能] 创建完整的规划文档（需求+设计+实施）
```

---

## 最佳实践

### 提供充分背景

```bash
# 好的请求：
> 为电商平台的"积分商城"功能创建需求文档
> 背景：
> - 现有用户 50 万，月活 10 万
> - 技术栈：React + Node.js + MongoDB
> - 预算：3 名开发者，4 周
> - 竞品参考：京东积分商城

# 缺少背景（效果较差）：
> 创建积分系统需求文档
```

### 指定技术约束

```bash
> 在以下约束下设计通知系统：
> - 必须兼容现有的 Django REST Framework
> - 使用 Celery 处理异步任务
> - 部署在 AWS（已有 SES 和 SNS）
```

### 迭代细化

```bash
# 第一轮：高层规划
> 为用户系统创建高层次的技术架构

# 第二轮：深入某个模块
> 详细设计认证模块，包括 JWT + Refresh Token 机制

# 第三轮：任务分解
> 将认证模块分解为具体的实施任务，按优先级排序
```

---

## 常见问题

### Q1: 生成的文档格式可以定制吗？

**A**: 可以，直接在请求中说明：

```bash
> 创建需求文档，使用我们公司的格式：
> - 需求 ID 格式：REQ-XXXX
> - 每个需求需要有"业务价值"字段
> - 需要 RACI 矩阵（谁负责、谁批准、谁咨询、谁知情）
```

### Q2: 如何确保生成的内容准确？

**A**: 提供越多上下文越好：
- 现有代码和文档
- 类似系统的截图
- 竞品分析
- 技术约束

### Q3: 生成的文档可以直接用于开发吗？

**A**: 通常需要人工 review 和调整，特别是：
- 工时估算（AI 可能不了解团队情况）
- 优先级（需要业务判断）
- 技术选型（需要结合团队技能）

---

## 相关 Skills

- [mcp-builder](./mcp-builder.md) - 规划后实现 MCP 集成
- [skill-creator](./skill-creator.md) - 创建项目专属 Skill
- [code-review](./code-review.md) - 审查实施的代码

---

**Skill 版本**: 内置
**最后更新**: 2026-02-10
