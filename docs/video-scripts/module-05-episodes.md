# Module 5: 架构与设计模式 - 视频脚本

## Episode 19: 整洁架构原则 (15 分钟)

### [0:00-1:00] 引入

**视觉元素**：
- 标题文字："整洁架构：依赖方向决定一切"
- 整洁架构同心圆图（动画效果，从内到外逐层出现）
- Uncle Bob (Robert C. Martin) 照片

**内容**：
> 什么是好的软件架构？不是使用最新的框架，不是应用最复杂的设计模式。好的架构让你的代码**易于测试、易于修改、易于理解**。
>
> 今天我们学习 Uncle Bob 的整洁架构，一个改变了整个行业的架构模式。

**屏幕录制**：
- 展示整洁架构的官方文章链接
- 展示 Uncle Bob 的书籍《Clean Architecture》

### [1:00-3:00] 概念讲解

**视觉元素**：
- 大型同心圆图解（每层用不同颜色）
- 箭头动画：依赖方向由外向内
- 数据流向动画：由内向外

**内容**：
> 整洁架构的核心是**依赖规则**：源代码依赖只能由外向内。
>
> **四个层次**：
> 1. **Entities (实体层)** - 最内层，企业级业务规则
> 2. **Use Cases (用例层)** - 应用特定业务规则
> 3. **Interface Adapters (接口适配器层)** - 连接外部世界
> 4. **Frameworks & Drivers (框架层)** - 最外层，外部工具
>
> 关键点：**内层不知道外层的存在**！Entity 不依赖任何框架，Use Case 不依赖数据库。

**动画**：
- 每层依次高亮，显示其职责
- 箭头显示依赖方向
- 显示"数据跨越边界"的动画

### [3:00-8:00] 实战演示

**视觉元素**：
- VS Code 分屏：左侧代码，右侧架构图
- 实时代码编写

**内容**：
> 让我们用 Claude Code 从零开始构建一个用户注册功能。首先激活 Plan Mode (Shift+Tab 两次)，让 Claude 帮我们设计架构。

**屏幕录制**：
```
# 演示步骤

1. 按 Shift+Tab 两次激活 Plan Mode
2. 输入任务："创建用户注册功能，遵循整洁架构"
3. 展示 Claude 的规划输出
4. 逐层实现代码
```

> 看到没有？
> - **Entity 层**：User、UserEntity，只包含业务规则，不知道数据库的存在
> - **Use Case 层**：RegisterUserUseCase，定义了 UserGateway 接口
> - **Adapter 层**：UserController，处理 HTTP 请求
> - **Framework 层**：PostgresUserGateway，实现具体的数据库操作
>
> 每一层都可以独立测试！

### [8:00-12:00] mybatis-boost 案例分析

**视觉元素**：
- mybatis-boost 架构图
- 代码高亮显示关键部分

**内容**：
> 让我们看看真实项目 mybatis-boost 是如何应用整洁架构的。

**屏幕录制**：
```
# 展示文件结构
- src/core/entities/MappingResult.ts
- src/core/use-cases/FindMappingUseCase.ts
- src/adapters/DefinitionProvider.ts
- src/frameworks/VSCodeFileGateway.ts
```

> **Entity 层**：
> - MappingResult、MappingType
> - MappingValidator（业务规则：验证映射有效性）
>
> **Use Case 层**：
> - FindMappingUseCase
> - 定义了 IFileGateway、IParserGateway 接口
>
> **Adapter 层**：
> - DefinitionProvider：连接 VS Code API 和 Use Case
>
> **Framework 层**：
> - VSCodeFileGateway：实现文件系统访问
> - MyBatisParserGateway：实现 XML 解析
>
> 这种架构让 mybatis-boost 可以轻松支持新的文件系统、新的解析器，而不影响核心导航逻辑。

### [12:00-14:00] 常见陷阱

**视觉元素**：
- 错误代码示例（红色 X 标记）
- 正确代码示例（绿色 ✓ 标记）
- 并列对比

**内容**：
> 三个最常见的错误：
>
> **1. 在 Entity 中导入框架代码** ❌
> ```typescript
> import { Request } from 'express'; // 错误！
> ```
>
> **2. 在 Use Case 中直接访问数据库** ❌
> ```typescript
> private db = new Database(); // 错误！
> ```
>
> **3. 让内层知道外层的数据结构** ❌
> ```typescript
> httpResponse?: { status: number } // 错误！
> ```

**屏幕录制**：
- 展示每个错误及其修复方法

### [14:00-15:00] 总结

**视觉元素**：
- 关键要点列表（动画逐条出现）
- Next Chapter 预告

**内容**：
> 整洁架构的核心要点：
> - **依赖方向由外向内**
> - **内层不依赖外层**
> - **通过接口解耦各层**
>
> 好的架构让你能够：
> - 轻松替换框架
> - 独立测试每一层
> - 清晰理解业务逻辑
>
> 下一章，我们将学习洋葱架构和六边形架构，看看它们与整洁架构的关系。

---

## Episode 20: 洋葱架构与六边形架构 (18 分钟)

### [0:00-1:00] 引入

**视觉元素**：
- 标题："三种架构，同一核心"
- 三种架构并列对比图

**内容**：
> 上章我们学习了整洁架构。今天我们看看另外两个重要的架构模式：洋葱架构和六边形架构。
>
> 它们看起来不同，但核心思想是一致的：**让业务逻辑独立于外部技术**。

### [1:00-3:00] 洋葱架构

**视觉元素**：
- 洋葱架构分层图
- 与整洁架构对照

**内容**：
> 洋葱架构由 Jeffrey Palermo 在 2008 年提出，和整洁架构**几乎一样**，只是术语不同：
>
> - **Core Domain** → Entities
> - **Domain Services** → Use Cases
> - **Application Services** → Interface Adapters
> - **Infrastructure** → Frameworks & Drivers
>
> 洋葱架构特别适合 **DDD (Domain-Driven Design)** 项目，因为它强调 Domain 的层次划分。

**动画**：
- 洋葱分层动画
- 与整洁架构的对应关系

### [3:00-8:00] 六边形架构

**视觉元素**：
- 六边形架构图（六边形形状）
- Ports 和 Adapters 动画
- 驱动方向动画

**内容**：
> 六边形架构由 Alistair Cockburn 在 2005 年提出，也叫 **Ports and Adapters** 架构。
>
> 核心概念：
> - **Port**: 应用程序定义的接口
> - **Adapter**: 实现 Port 的具体技术
>
> **两种 Port**：
> - **Driving Port (Primary)**: 由外部驱动的端口（输入）
> - **Driven Port (Secondary)**: 驱动外部的端口（输出）
>
> **两种 Adapter**：
> - **Driving Adapter**: HTTP、CLI、Message Queue
> - **Driven Adapter**: Database、Email、Cache

**屏幕录制**：
```
# 演示六边形架构实现
1. 定义 Ports（接口）
2. 实现 Application Core
3. 实现 Adapters
4. 组装应用程序
```

> 注意看，Application Core 不知道 HTTP 的存在，不知道 PostgreSQL 的存在。它只知道 IEmailSenderPort 和 IUserRepositoryPort 接口。
>
> 这意味着我们可以轻松替换：
> - PostgreSQL → MongoDB
> - SendGrid → AWS SES
> - HTTP API → CLI → Message Queue
>
> 都不需要修改 Application Core！

### [8:00-12:00] 架构对比

**视觉元素**：
- 三种架构并列对比表
- 选择决策树（交互式）

**内容**：
> **三种架构的核心共同点**：
> - ✅ 依赖倒置
> - ✅ 业务逻辑独立
> - ✅ 可测试
> - ✅ 框架独立
>
> **如何选择**：
>
> [决策树动画]
>
> 1. 你的项目使用 DDD 吗？
>    - 是 → 洋葱架构
>    - 否 ↓
> 2. 你需要支持多种输入/输出吗？
>    - 是 → 六边形架构
>    - 否 ↓
> 3. 默认选择：整洁架构

### [12:00-16:00] mybatis-boost 实战

**视觉元素**：
- mybatis-boost 六边形架构图
- 代码展示

**内容**：
> [演示：查看 mybatis-boost 的架构]
>
> mybatis-boost 使用六边形架构：
> - **INavigationServicePort**: Driving Port（导航服务接口）
> - **IFileAccessPort**: Driven Port（文件访问接口）
> - **NavigationService**: Application Core
> - **VSCodeDefinitionAdapter**: Driving Adapter
> - **VSCodeFileAccessAdapter**: Driven Adapter
>
> 这种架构让 mybatis-boost 可以支持不同的文件系统、不同的解析器，而不影响核心导航逻辑。

### [16:00-18:00] 总结

**视觉元素**：
- 三种架构总结表
- Next Chapter 预告

**内容**：
> 三种架构，同一核心：
> - **整洁架构**：强调 Entities 和 Use Cases
> - **洋葱架构**：强调 Domain 层次
> - **六边形架构**：强调 Ports 和 Adapters
>
> 选择适合你的架构，但记住：**让业务逻辑独立于外部技术**是所有架构的核心目标。
>
> 下一章，我们将学习可测试性和 Mocking，看看这些架构如何让测试变得简单。

---

## Episode 21: 可测试性与 Mocking (16 分钟)

### [0:00-1:00] 引入

**视觉元素**：
- 标题："可测试代码：好的架构的自然结果"
- 代码对比：不可测试 vs 可测试

**内容**：
> 什么是可测试代码？不是"能写测试"的代码，而是"**容易写测试**"的代码。
>
> 好的架构自然产生可测试的代码。今天我们学习如何识别和编写可测试的代码。

### [1:00-3:00] 识别不可测试代码

**视觉元素**：
- 不可测试代码示例（红色高亮）
- 问题列表（逐个出现）

**内容**：
> 三个常见的不可测试代码特征：
>
> **1. 硬编码依赖** ❌
> ```typescript
> private db = new Database(); // 无法 mock
> ```
>
> **2. 全局状态** ❌
> ```typescript
> global.currentUser; // 无法控制
> ```
>
> **3. 静态方法** ❌
> ```typescript
> ExternalAPI.call(); // 无法测试
> ```

### [3:00-7:00] 测试替身

**视觉元素**：
- Test Doubles 分类图（五种类型）
- 每种 Double 的示例代码

**内容**：
> Gerard Meszaros 定义了五种测试替身：
>
> **1. Dummy (哑元)**
> - 只是为了满足参数要求
> - 实际不会被使用
>
> **2. Stub (桩)**
> - 返回预设值
> - 不验证调用
>
> **3. Spy (间谍)**
> - 记录调用信息
> - 用于验证交互
>
> **4. Mock (模拟)**
> - 预设期望行为
> - 验证调用次数和参数
>
> **5. Fake (伪造)**
> - 简化但可用的实现
> - 最强大的测试替身！

**屏幕录制**：
- 逐个演示每种 Test Double 的使用

> 记住：**Fake 是最强大的**，因为它提供了真实的实现！

### [7:00-11:00] 使用 Sinon.js

**视觉元素**：
- Sinon.js 代码演示
- 测试运行结果

**内容**：
> Sinon.js 是 JavaScript 测试的瑞士军刀。

**屏幕录制**：
```
# 演示 Sinon.js
1. 创建 Stub
2. 创建 Spy
3. 验证调用
4. 运行测试
```

> 看到没有？我们可以精确验证方法被调用的次数、参数、返回值。
>
> 但记住：**不要过度 Mock**！测试应该关注行为，而非实现细节。

### [11:00-14:00] mybatis-boost 测试实战

**视觉元素**：
- mybatis-boost 测试文件
- Fake Repository 实现

**内容**：
> [演示：查看 mybatis-boost 的测试]
>
> mybatis-boost 使用 **Fake Repository** 测试 FileMapper。这比 Mock 更好，因为它提供了真实的内存实现，让测试更接近真实场景。
>
> 注意看：FileMapper 的所有依赖都是接口，这让测试变得简单。

### [14:00-16:00] 总结

**视觉元素**：
- 关键要点列表
- Next Chapter 预告

**内容**：
> 可测试性关键要点：
> - **所有依赖必须可注入**
> - **使用接口抽象**
> - **优先使用 Fake 而非 Mock**
> - **测试行为，而非实现细节**
>
> 好的架构 = 可测试的代码。
>
> 下一章，我们将学习 AAA 模式，看看如何组织清晰、易读的测试。

---

## Episode 22: AAA 模式与测试最佳实践 (14 分钟)

### [0:00-1:00] 引入

**视觉元素**：
- 标题："AAA：让测试清晰易读"
- 代码对比：混乱的测试 vs AAA 测试

**内容**：
> 什么是好的测试？不是覆盖率高的测试，而是"**清晰、易读、易维护**"的测试。
>
> AAA 模式——Arrange、Act、Assert——是编写清晰测试的金标准。

### [1:00-3:00] AAA 模式

**视觉元素**：
- AAA 三阶段图解（用颜色区分）
- 每阶段的代码示例

**内容**：
> AAA 模式将测试分为三个阶段：
>
> **1. Arrange (准备)** - 设置测试环境
> - 创建对象
> - 设置 Mock/Stubs
> - 准备数据
>
> **2. Act (执行)** - 执行被测试的行为
> - 调用被测试的方法
> - 触发事件
>
> **3. Assert (断言)** - 验证结果
> - 检查返回值
> - 验证状态变化

**屏幕录制**：
- 展示 AAA 模式的代码示例
- 用注释标记三个阶段

> 看到这三个清晰的区块了吗？任何人都能立即理解测试在做什么！

### [3:00-6:00] 测试命名

**视觉元素**：
- 好的命名 vs 差的命名对比
- 命名模式列表

**内容**：
> 好的测试名称应该像一个故事：
>
> ❌ "test1" 或 "checkLogin"
>
> ✅ "should_authenticate_user_when_credentials_valid"
>
> 推荐的命名模式：
> - **should_ExpectedBehavior_When_StateUnderTest**
> - **MethodUnderTest_ExpectedBehavior_StateUnderTest**

**屏幕录制**：
- 演示重构测试命名

### [6:00-10:00] 测试组织

**视觉元素**：
- 测试文件结构
- Nested Suites 示例

**内容**：
> 好的测试组织让测试套件易于维护。
>
> **推荐结构**：
> - 顶层 suite: 类名
> - 二层 suite: 方法名
> - 三层 suite: 场景描述
>
> 这样每个测试的完整路径就是一个清晰的故事描述！

**屏幕录制**：
- 展示嵌套 suite 的代码
- 展示测试运行输出

### [10:00-12:00] 覆盖场景

**视觉元素**：
- 测试金字塔
- 测试清单

**内容**：
> 完整的测试应该覆盖：
> - **快乐路径**（成功场景）
> - **边界条件**（空值、最大值）
> - **错误情况**（失败场景）
> - **边缘情况**（特殊字符）
> - **并发场景**
>
> 记住：**70% 单元测试，20% 集成测试，10% E2E 测试**。

### [12:00-14:00] 总结与 Module 5 总结

**视觉元素**：
- AAA 模式总结
- Module 5 总结（所有四章）
- Module 6 预告

**内容**：
> **AAA 模式和测试最佳实践**：
> - 三个阶段：Arrange、Act、Assert
> - 描述性命名
> - 清晰的组织结构
> - 覆盖关键场景
>
> **Module 5 总结**：
> 我们学习了四种架构模式：
> - **整洁架构**：依赖规则
> - **洋葱架构**：Domain 层次
> - **六边形架构**：Ports 和 Adapters
> - **可测试性**：测试替身和 AAA 模式
>
> 这些架构有一个共同核心：**让业务逻辑独立于外部技术**。
>
> 下一章，我们将进入 **Module 6**，理解 LLM 的真实工作原理和局限性。这将帮助我们更好地使用 Claude Code！
