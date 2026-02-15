# Skill: skill-creator

## 概述

`skill-creator` 是用于创建高效 Skills 的指导 Skill。当你需要构建新的可重用 Skill 或更新现有 Skill 时，使用这个 Skill 来获得专业的指引。

**核心能力**:
- 分析需求，设计 Skill 架构
- 生成符合规范的 Skill 文件
- 提供 Skill 文件结构和最佳实践
- 帮助迭代和优化已有 Skill

---

## 触发方式

### 斜杠命令

```bash
/skill-creator
```

### 自然语言触发

```
"创建一个新的 Skill"
"帮我写一个 Skill 用于 [任务描述]"
"如何创建自定义 Skill"
"更新这个 Skill"
```

---

## Skill 文件规范

### 目录结构

Claude Code 会在以下位置搜索 Skills：

```
~/.claude/skills/           # 用户级别 Skills（全局）
.claude/skills/             # 项目级别 Skills
project/.skills/            # 项目 Skills（旧版兼容）
```

### 基本文件结构

```
~/.claude/skills/
├── my-skill.md             # 简单 Skill（单文件）
└── complex-skill/          # 复杂 Skill（目录）
    ├── skill.md            # 主文件
    ├── examples/           # 示例文件
    │   ├── example-1.md
    │   └── example-2.md
    └── templates/          # 模板文件
        └── output-template.md
```

### Skill 文件格式

```markdown
---
name: "skill-name"
description: "简短描述，用于触发 Skill 的识别"
version: "1.0.0"
author: "作者名"
tags: ["tag1", "tag2"]
---

# Skill 标题

## 概述

[Skill 的功能和价值说明]

## 使用场景

使用此 Skill 当：
- 场景1
- 场景2

## 指令

[给 Claude 的详细操作指令]

## 示例

### 示例1: [场景名]

**输入**: [用户会提供什么]

**输出**: [Claude 应该产生什么]

## 注意事项

[重要的约束、限制或特别说明]
```

---

## 实际演示

### 示例 1: 创建代码注释生成器 Skill

**用户请求**:
```
帮我创建一个 Skill，用于为代码自动生成中文注释。
要求：
- 支持多种编程语言
- 注释风格要专业
- 解释复杂逻辑
```

**生成的 Skill 文件**:

```markdown
---
name: "code-commenter"
description: "为代码生成专业的中文注释，支持多种编程语言"
version: "1.0.0"
author: "你的名字"
tags: ["documentation", "comments", "code-quality"]
---

# 代码注释生成器

## 概述

为代码自动生成专业的中文注释，提升代码可读性和可维护性。
支持 Python、JavaScript/TypeScript、Java、Go 等主流编程语言。

## 使用场景

使用此 Skill 当：
- 接手没有注释的遗留代码
- 代码 review 发现注释不足
- 需要为开源项目添加文档
- 帮助团队成员理解复杂代码

## 指令

### 阶段1：分析代码

1. **识别语言**
   - 根据文件扩展名或语法判断编程语言
   - 选择对应的注释格式（`#`/`//`/`/* */`）

2. **理解代码结构**
   - 识别类、函数、变量的作用
   - 理解算法逻辑
   - 找出复杂或不直观的地方

3. **确定注释级别**
   - 文件级：描述文件用途
   - 类级：描述类的职责
   - 函数级：描述功能、参数、返回值
   - 行内：解释复杂的单行逻辑

### 阶段2：生成注释

**文件级注释**（适用于较长文件）:
```
"""
文件描述：一句话说明文件用途
主要功能：
  - 功能1
  - 功能2
依赖：外部依赖说明
作者：（可选）
"""
```

**函数/方法级注释**:
```python
def function_name(param1, param2):
    """
    函数功能的简短描述。

    详细说明（如果需要）：
    - 特殊情况处理
    - 算法说明

    参数:
        param1 (类型): 参数1的描述
        param2 (类型): 参数2的描述

    返回:
        类型: 返回值描述

    异常:
        ExceptionType: 在什么情况下抛出

    示例:
        >>> result = function_name("hello", 42)
        >>> print(result)  # 预期输出
    """
```

**行内注释原则**:
```
✅ 解释"为什么"，不是"做什么"：
# 使用位运算代替除法，提升性能约40%
n = n >> 1

❌ 重复代码已说明的内容：
# 将 n 右移一位
n = n >> 1
```

### 阶段3：质量检查

生成注释后验证：
- [ ] 注释语言为中文（专业词汇可保留英文）
- [ ] 函数注释包含参数和返回值说明
- [ ] 复杂算法有流程说明
- [ ] 注释与代码逻辑一致
- [ ] 没有多余的废话

## 示例

### 示例1: Python 函数注释

**输入代码**:
```python
def find_longest_palindrome(s):
    if not s:
        return ""
    start, end = 0, 0
    for i in range(len(s)):
        len1 = expand(s, i, i)
        len2 = expand(s, i, i + 1)
        max_len = max(len1, len2)
        if max_len > end - start:
            start = i - (max_len - 1) // 2
            end = i + max_len // 2
    return s[start:end + 1]

def expand(s, left, right):
    while left >= 0 and right < len(s) and s[left] == s[right]:
        left -= 1
        right += 1
    return right - left - 1
```

**期望输出**:
```python
def find_longest_palindrome(s: str) -> str:
    """
    使用中心扩展算法找到字符串中最长的回文子串。

    算法思路：
    - 遍历每个字符作为回文中心
    - 分别考虑奇数长度（单字符中心）和偶数长度（双字符中心）
    - 记录最长回文的起止位置
    - 时间复杂度 O(n²)，空间复杂度 O(1)

    参数:
        s (str): 输入字符串

    返回:
        str: 最长回文子串，若输入为空则返回空字符串

    示例:
        >>> find_longest_palindrome("babad")
        'bab'  # 或 'aba'，两者都是正确答案
        >>> find_longest_palindrome("cbbd")
        'bb'
    """
    if not s:
        return ""

    start, end = 0, 0  # 记录最长回文的起止下标

    for i in range(len(s)):
        # 尝试以 s[i] 为中心扩展（奇数长度回文）
        len1 = expand(s, i, i)
        # 尝试以 s[i] 和 s[i+1] 为中心扩展（偶数长度回文）
        len2 = expand(s, i, i + 1)

        max_len = max(len1, len2)

        # 更新最长回文的边界
        if max_len > end - start:
            start = i - (max_len - 1) // 2
            end = i + max_len // 2

    return s[start:end + 1]


def expand(s: str, left: int, right: int) -> int:
    """
    从给定的中心位置向两侧扩展，计算最长回文的长度。

    参数:
        s (str): 原始字符串
        left (int): 扩展起点左侧下标
        right (int): 扩展起点右侧下标

    返回:
        int: 以给定位置为中心的最长回文长度
    """
    # 当左右字符相同且未越界时继续扩展
    while left >= 0 and right < len(s) and s[left] == s[right]:
        left -= 1
        right += 1

    # 扩展结束后，right-left-1 即为回文长度
    return right - left - 1
```

## 注意事项

- **保留代码逻辑不变**：只添加注释，不修改任何代码
- **中英文混合**：中文为主，专业术语（如函数名、类名、API名）保留英文
- **避免过度注释**：简单明了的代码不需要注释每一行
- **注释与代码同步**：修改代码时也要更新注释
- **类型标注**：如果语言支持且代码没有类型注解，可以在注释中补充类型信息
```

**安装方式**:
```bash
# 将 Skill 文件保存到用户 Skills 目录
cp code-commenter.md ~/.claude/skills/

# 或者保存到项目 Skills 目录
mkdir -p .claude/skills/
cp code-commenter.md .claude/skills/
```

---

### 示例 2: 创建数据库迁移助手 Skill

**用户请求**:
```
我们团队经常需要写数据库迁移脚本（Django），
帮我创建一个 Skill 来生成标准化的迁移文件
```

**生成的 Skill 文件**:

```markdown
---
name: "django-migration"
description: "生成标准化的 Django 数据库迁移文件"
version: "1.0.0"
tags: ["django", "database", "migration"]
---

# Django 迁移生成器

## 概述

生成符合团队规范的 Django 数据库迁移文件，
包括数据迁移、Schema 迁移和回滚逻辑。

## 使用场景

- 添加新的数据库字段
- 修改字段类型
- 添加索引或约束
- 数据迁移（填充初始数据）
- 重命名表或字段

## 指令

### 阶段1：分析变更

1. 阅读相关的 Django Model 文件
2. 理解需要做的 Schema 变更
3. 确认是否需要数据迁移

### 阶段2：生成迁移文件

**文件命名规范**:
```
{序号}_{描述}_{YYYY_MM_DD}.py
例如: 0042_add_user_avatar_2026_02_10.py
```

**标准迁移结构**:
```python
# Generated by Django migrations
# Team convention: always include rollback

from django.db import migrations, models


class Migration(migrations.Migration):

    # 明确声明依赖
    dependencies = [
        ('app_name', '0041_previous_migration'),
    ]

    operations = [
        # Schema 变更
        migrations.AddField(
            model_name='user',
            name='avatar',
            field=models.ImageField(
                upload_to='avatars/',
                null=True,
                blank=True,
                verbose_name='用户头像',
            ),
        ),
    ]
```

**数据迁移模板**:
```python
from django.db import migrations


def migrate_data_forward(apps, schema_editor):
    """正向数据迁移：详细说明做什么"""
    Model = apps.get_model('app_name', 'ModelName')
    # 迁移逻辑
    Model.objects.filter(条件).update(字段=新值)


def migrate_data_backward(apps, schema_editor):
    """回滚数据迁移：恢复原始状态"""
    Model = apps.get_model('app_name', 'ModelName')
    # 回滚逻辑


class Migration(migrations.Migration):
    dependencies = [...]

    operations = [
        migrations.RunPython(
            migrate_data_forward,
            migrate_data_backward,  # 必须提供回滚函数
        ),
    ]
```

### 阶段3：安全检查

- [ ] 是否有回滚（backward）逻辑
- [ ] 数据迁移是否考虑了大表性能
- [ ] 是否会锁表（ALTER TABLE 会锁表）
- [ ] 是否需要添加 atomic = False（大表迁移）

## 示例

**输入**: "需要给 User 表添加 last_login_ip 字段"

**输出**: 完整的迁移文件

## 注意事项

- 迁移文件一旦运行不能修改，有问题要新建迁移
- 大表（>100万行）的 ADD COLUMN 考虑分批处理
- 生产环境迁移前必须在测试环境验证
```

---

## Skill 创建流程

### 步骤 1: 明确需求

回答以下问题：

```
1. 这个 Skill 解决什么问题？
2. 谁会使用它？（开发者/测试/运维）
3. 触发场景是什么？
4. 期望的输出是什么？
5. 有哪些约束和限制？
```

### 步骤 2: 设计 Skill 结构

```
简单 Skill（单一任务）:
- 单文件: ~/.claude/skills/my-skill.md

复杂 Skill（多步骤工作流）:
- 目录:
  ~/.claude/skills/complex-skill/
  ├── skill.md         # 主指令文件
  ├── examples/        # 多个示例
  └── templates/       # 输出模板
```

### 步骤 3: 编写 Skill 文件

遵循以下原则：

```
1. 清晰的描述（frontmatter description 字段）
2. 明确的使用场景
3. 分阶段的操作指令
4. 具体的输入/输出示例
5. 重要的注意事项
```

### 步骤 4: 测试 Skill

```bash
# 触发 Skill 的测试
> 使用 my-skill 处理: [测试输入]

# 检查结果是否符合预期
# 迭代优化
```

### 步骤 5: 版本管理

```markdown
## Changelog

### 1.1.0 (2026-02-10)
- 新增: 支持 TypeScript 注释格式
- 修复: 修复了对泛型类型的处理

### 1.0.0 (2026-01-15)
- 初始版本
```

---

## Skill 质量评估

### 好的 Skill 的特征

```
✅ 描述清晰，一看就知道用途
✅ 使用场景具体（不模糊）
✅ 指令详细且可执行
✅ 有完整的输入/输出示例
✅ 注意事项提醒了关键限制
✅ 输出格式一致（每次调用结果格式相同）
```

### 需要改进的 Skill

```
❌ 描述模糊（"帮助处理代码"）
❌ 指令太过原则性，没有具体步骤
❌ 没有示例，Claude 无法理解期望输出
❌ 缺少边界条件说明
❌ 每次调用结果格式不一致
```

---

## 高级功能

### Skill 之间的调用

```markdown
## 指令

1. 首先使用 `code-commenter` Skill 分析代码
2. 然后使用 `test-generator` Skill 生成测试
3. 最后生成完整的技术文档
```

### 参数化 Skill

通过用户输入动态调整行为：

```markdown
## 指令

根据用户指定的语言风格（formal/casual/technical）调整输出：
- **formal**: 使用正式的技术写作风格
- **casual**: 使用轻松的对话风格
- **technical**: 深入技术细节

如果未指定，默认使用 technical 风格。
```

### 条件逻辑

```markdown
## 指令

根据代码类型执行不同策略：

**如果是 API 接口**:
- 生成 OpenAPI/Swagger 文档
- 包含请求/响应示例

**如果是数据模型**:
- 生成字段说明
- 包含关系图描述

**如果是工具函数**:
- 生成 JSDoc 注释
- 包含使用示例
```

---

## 常见问题

### Q1: Skill 和 CLAUDE.md 中的指令有什么区别？

**A**:

| 特性 | Skill | CLAUDE.md |
|------|-------|-----------|
| 作用域 | 特定任务 | 整个项目 |
| 触发方式 | 主动调用 | 始终生效 |
| 可复用性 | 高 | 项目特定 |
| 详细程度 | 高 | 中 |

### Q2: Skill 文件放在哪里才会生效？

**A**: Claude Code 按以下顺序搜索 Skills：

```
优先级（由高到低）:
1. .claude/skills/ （项目目录下）
2. ~/.claude/skills/ （用户主目录）
3. 内置 Skills
```

### Q3: 如何调试 Skill 效果？

**A**: 可以直接测试并迭代：

```bash
# 测试1: 基本功能
> 使用 code-commenter 为这段代码添加注释:
  [粘贴代码]

# 测试2: 边界情况
> 使用 code-commenter 处理空函数

# 如果效果不好，修改 Skill 文件后再测试
```

### Q4: Skill 支持中文吗？

**A**: 完全支持！Skill 文件可以完全使用中文编写，包括 description、标签等。

---

## 相关文档

- [Layer 06 - 高级特性](../../../video-scripts/layer-06-advanced.md)
- [mcp-builder Skill](./mcp-builder.md) - 创建 MCP 服务器
- [code-review Skill](./code-review.md) - 代码审查示例 Skill

---

**Skill 版本**: 内置
**最后更新**: 2026-02-10
