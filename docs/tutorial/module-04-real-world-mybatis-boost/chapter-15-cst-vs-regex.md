# Chapter 15: MyBatis XML 格式化器 - CST vs 正则表达式

**模块**: Module 4 - mybatis-boost 实战案例
**预计阅读时间**: 20 分钟
**难度**: ⭐⭐⭐⭐⭐

---

## 学习目标

本章结束后，你将能够：

- [ ] 理解为什么正则表达式不适合处理 XML
- [ ] 掌握 CST (Concrete Syntax Tree) 的概念
- [ ] 学习 mybatis-boost 的 CST 解析器实现
- [ ] 了解如何正确处理 MyBatis 动态 SQL 标签

---

## 前置知识

- [ ] 已完成 Chapter 14 - 项目概览
- [ ] 了解 XML 基础语法
- [ ] 熟悉正则表达式的基本概念

---

## 问题背景

### MyBatis XML 的格式化挑战

MyBatis 使用 XML 格式的 Mapper 文件，其中包含：
- 普通 SQL 语句
- 动态 SQL 标签 (`<if>`, `<choose>`, `<foreach>` 等)
- 参数绑定 (`#{param}`, `${param}`)
- 结果映射 (`<resultMap>`)
- SQL 片段引用 (`<include>`)

**示例 MyBatis XML**：

```xml
<select id="findUsers" resultMap="BaseResultMap">
    SELECT * FROM users
    <where>
        <if test="name != null and name != ''">
            AND name LIKE #{name}
        </if>
        <if test="email != null">
            AND email = #{email}
        </if>
        <choose>
            <when test="status == 'ACTIVE'">
                AND status = 1
            </when>
            <otherwise>
                AND status = 0
            </otherwise>
        </choose>
    </where>
    <if test="orderBy != null">
        ORDER BY ${orderBy}
    </if>
</select>
```

### 格式化的目标

1. **格式化 SQL 语句**：正确缩进、大小写、换行
2. **保留动态标签**：不破坏 MyBatis 特有的标签结构
3. **正确处理嵌套**：标签嵌套时的缩进
4. **多方言支持**：MySQL, PostgreSQL, Oracle, TSQL 等

---

## 为什么正则表达式不够用？

### 正则表达式的局限性

```
┌─────────────────────────────────────────────────────────┐
│         正则表达式 vs 结构化解析                         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  正则表达式：                                           │
│  ──────────────                                         │
│  ✓ 适合：简单的模式匹配                                 │
│  ✗ 不适合：嵌套结构、上下文相关                         │
│                                                         │
│  结构化解析 (CST)：                                     │
│  ────────────────────                                  │
│  ✓ 适合：嵌套结构、复杂语法                             │
│  ✓ 保持：语法树结构，支持精确操作                       │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 具体问题示例

#### 问题 1: 嵌套标签

```xml
<!-- 原始 XML -->
<where>
  <if test="a">
    <if test="b">
      SQL HERE
    </if>
  </if>
</where>
```

**使用正则表达式的尝试**：

```javascript
// 尝试 1: 简单替换
function formatWithRegex(xml) {
  return xml
    .replace(/\s+/g, ' ')      // 多个空格 → 单个空格
    .replace(/>\s+</g, '><\n  ')  // 标签间换行
    .replace(/\n\s*\n/g, '\n');    // 多个换行 → 单个
}

// 结果: 破坏了嵌套结构！
// <where>\n  <if test="a">\n  <if test="b">\n    SQL HERE\n  </if>\n  </if>\n</where>
// 缩进完全错误，无法区分层级
```

#### 问题 2: 保留动态标签内的 SQL

```xml
<!-- 原始 XML -->
<select id="getUser">
  SELECT id, name, email FROM users WHERE 1=1
  <if test="name != null">
    AND name = #{name}
  </if>
</select>
```

**使用正则表达式的问题**：

```javascript
// 尝试格式化 SQL
function formatSQL(sql) {
  return sql
    .replace(/\s+/g, ' ')
    .replace(/SELECT/gi, '\nSELECT')
    .replace(/FROM/gi, '\nFROM')
    .replace(/WHERE/gi, '\nWHERE');
}

// 问题：无法区分 SQL 关键字和标签内的文本
// <if test="name != null"> 中的 test 属性可能包含 "SELECT"
// 正则表达式会错误地处理这种情况
```

#### 问题 3: 注释和字符串

```xml
<select id="search">
  SELECT * FROM users
  -- 这是一个注释
  WHERE name LIKE '%test%'
  <if test="type == 'special'">
    AND type = 'special'
  </if>
</select>
```

**正则表达式的问题**：

```javascript
// 尝试处理注释
function removeComments(sql) {
  return sql.replace(/--.*$/gm, '');
}

// 问题：
// 1. 字符串中的 "--" 会被误认为是注释
// 2. 字符串中的 "test" 会被处理
// 3. 标签属性中的内容可能包含 SQL 关键字
```

### CST 的优势

```
┌─────────────────────────────────────────────────────────┐
│              CST (Concrete Syntax Tree) 的优势           │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  1. 结构感知                                            │
│     → 理解嵌套关系                                      │
│     → 正确处理层级                                      │
│                                                         │
│  2. 上下文相关                                          │
│     → 区分 SQL 和标签内容                               │
│     → 正确处理字符串和注释                               │
│                                                         │
│  3. 精确操作                                            │
│     → 可以只格式化 SQL 部分                             │
│     → 保持标签结构不变                                  │
│                                                         │
│  4. 可扩展                                              │
│     → 易于添加新的 SQL 方言                             │
│     → 易于支持新的 MyBatis 标签                          │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## CST 解析器实现

### 架构设计

```
┌─────────────────────────────────────────────────────────┐
│           MybatisSqlFormatter 架构                       │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Input: MyBatis XML 文本                                 │
│     ↓                                                   │
│  ┌───────────────────────────────────────────────┐     │
│  │        XML Tokenizer                           │     │
│  │  • 识别开始标签 <if>                            │     │
│  │  • 识别结束标签 </if>                           │     │
│  │  • 识别属性 test="condition"                   │     │
│  │  • 识别文本内容 (SQL)                           │     │
│  └───────────────────────────────────────────────┘     │
│     ↓                                                   │
│  Tokens: 开始标签, 结束标签, 文本, 属性                 │
│     ↓                                                   │
│  ┌───────────────────────────────────────────────┐     │
│  │        CST Parser                              │     │
│  │  • 构建语法树                                   │     │
│  │  • 处理嵌套结构                                 │     │
│  │  • 区分 SQL 和标签                              │     │
│  └───────────────────────────────────────────────┘     │
│     ↓                                                   │
│  CST: 树形结构，节点类型包括：                          │
│        - Element (标签)                                │
│        - Attribute (属性)                              │
│        - Text (文本/SQL)                               │
│     ↓                                                   │
│  ┌───────────────────────────────────────────────┐     │
│  │        SQL Formatter                           │     │
│  │  • 只格式化 Text 节点                           │     │
│  │  • 使用 sql-formatter 库                        │     │
│  │  • 支持多种方言                                 │     │
│  └───────────────────────────────────────────────┘     │
│     ↓                                                   │
│  ┌───────────────────────────────────────────────┐     │
│  │        CST Serializer                          │     │
│  │  • 重建 XML 字符串                              │     │
│  │  • 正确处理缩进                                 │     │
│  │  • 保持标签属性顺序                             │     │
│  └───────────────────────────────────────────────┘     │
│     ↓                                                   │
│  Output: 格式化后的 MyBatis XML                          │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 代码实现 (简化版)

**src/formatter/MybatisSqlFormatter.ts** (核心逻辑):

```typescript
import { format } from 'sql-formatter';
import * as vscode from 'vscode';

/**
 * MyBatis XML CST 节点类型
 */
interface CSTNode {
  type: 'element' | 'attribute' | 'text' | 'comment';
  name?: string;        // 元素名称 (如 'if', 'choose')
  attributes?: Map<string, string>;  // 属性
  children?: CSTNode[];  // 子节点
  value?: string;        // 文本值
  parent?: CSTNode;      // 父节点
  startLine: number;     // 开始行号
  endLine: number;       // 结束行号
}

/**
 * MyBatis SQL 格式化器
 * 使用 CST (Concrete Syntax Tree) 解析和格式化
 */
export class MybatisSqlFormatter {
  private config: vscode.WorkspaceConfiguration;

  constructor() {
    this.config = vscode.workspace.getConfiguration('mybatis-boost.formatter');
  }

  /**
   * 格式化 MyBatis XML
   */
  public format(xmlContent: string): string {
    // 1. 解析为 CST
    const root = this.parseToCST(xmlContent);

    // 2. 格式化 SQL (只处理 Text 节点)
    this.formatSQLInCST(root);

    // 3. 序列化回 XML
    return this.serializeCST(root);
  }

  /**
   * 解析 XML 为 CST
   */
  private parseToCST(xml: string): CSTNode {
    const tokens = this.tokenize(xml);
    return this.buildCST(tokens);
  }

  /**
   * 词法分析：将 XML 分解为 tokens
   */
  private tokenize(xml: string): Token[] {
    const tokens: Token[] = [];
    let pos = 0;

    while (pos < xml.length) {
      // 跳过空白
      if (this.isWhitespace(xml[pos])) {
        pos++;
        continue;
      }

      // 开始标签: <xxx>
      if (xml[pos] === '<' && xml[pos + 1] !== '/') {
        const match = xml.slice(pos).match(/^<(\w+)([^>]*)>/);
        if (match) {
          tokens.push({
            type: 'startTag',
            name: match[1],
            attributes: this.parseAttributes(match[2]),
            position: pos
          });
          pos += match[0].length;
          continue;
        }
      }

      // 结束标签: </xxx>
      if (xml[pos] === '<' && xml[pos + 1] === '/') {
        const match = xml.slice(pos).match(/^<\/(\w+)>/);
        if (match) {
          tokens.push({
            type: 'endTag',
            name: match[1],
            position: pos
          });
          pos += match[0].length;
          continue;
        }
      }

      // 文本内容
      const textEnd = xml.indexOf('<', pos);
      if (textEnd === -1) {
        // 剩余都是文本
        tokens.push({
          type: 'text',
          value: xml.slice(pos).trim(),
          position: pos
        });
        break;
      } else {
        const text = xml.slice(pos, textEnd).trim();
        if (text) {
          tokens.push({
            type: 'text',
            value: text,
            position: pos
          });
        }
        pos = textEnd;
      }
    }

    return tokens;
  }

  /**
   * 构建 CST
   */
  private buildCST(tokens: Token[]): CSTNode {
    const root: CSTNode = {
      type: 'element',
      name: 'root',
      children: [],
      startLine: 1,
      endLine: 1
    };

    const stack: CSTNode[] = [root];

    for (const token of tokens) {
      if (token.type === 'startTag') {
        const node: CSTNode = {
          type: 'element',
          name: token.name,
          attributes: token.attributes,
          children: [],
          startLine: this.lineAt(token.position),
          endLine: 0
        };

        // 添加到父节点的子节点
        const parent = stack[stack.length - 1];
        parent.children!.push(node);
        node.parent = parent;

        // 压入栈（等待匹配的结束标签）
        stack.push(node);
      } else if (token.type === 'endTag') {
        // 弹出栈，匹配开始标签
        const node = stack.pop();
        if (node && node.name === token.name) {
          node.endLine = this.lineAt(token.position);
        }
      } else if (token.type === 'text') {
        // 文本节点
        const parent = stack[stack.length - 1];
        parent.children!.push({
          type: 'text',
          value: token.value,
          parent,
          startLine: this.lineAt(token.position),
          endLine: this.lineAt(token.position)
        });
      }
    }

    return root;
  }

  /**
   * 格式化 CST 中的 SQL
   */
  private formatSQLInCST(node: CSTNode): void {
    if (node.type === 'text') {
      // 这是 SQL 文本，格式化它
      node.value = this.formatSQL(node.value);
    } else if (node.children) {
      // 递归处理子节点
      for (const child of node.children) {
        this.formatSQLInCST(child);
      }
    }
  }

  /**
   * 格式化 SQL（使用 sql-formatter 库）
   */
  private formatSQL(sql: string): string {
    const language = this.config.get<string>('language', 'auto');
    const keywordCase = this.config.get<string>('keywordCase', 'upper');

    try {
      return format(sql, {
        language: language === 'auto' ? undefined : language,
        keywordCase: keywordCase as 'upper' | 'lower' | 'preserve',
        indentStyle: 'standard',
        tabWidth: this.config.get<number>('tabWidth', 4)
      });
    } catch (error) {
      // 如果格式化失败，返回原始 SQL
      return sql;
    }
  }

  /**
   * 序列化 CST 回 XML
   */
  private serializeCST(node: CSTNode, indent = 0): string {
    const indentStr = ' '.repeat(indent);
    let result = '';

    if (node.type === 'element') {
      if (node.name === 'root') {
        // 根节点不输出标签
        if (node.children) {
          for (const child of node.children) {
            result += this.serializeCST(child, indent);
          }
        }
      } else {
        // 开始标签
        result += `${indentStr}<${node.name}`;
        if (node.attributes) {
          for (const [key, value] of node.attributes) {
            result += ` ${key}="${value}"`;
          }
        }
        result += '>\n';

        // 子节点
        if (node.children && node.children.length > 0) {
          for (const child of node.children) {
            result += this.serializeCST(child, indent + this.config.get<number>('tabWidth', 4));
          }
        }

        // 结束标签
        result += `${indentStr}</${node.name}>\n`;
      }
    } else if (node.type === 'text') {
      // 文本节点（格式化后的 SQL）
      if (node.value && node.value.trim()) {
        result += `${indentStr}${node.value}\n`;
      }
    }

    return result;
  }

  /**
   * 解析标签属性
   */
  private parseAttributes(attrString: string): Map<string, string> {
    const attrs = new Map<string, string>();
    const regex = /(\w+)="([^"]*)"/g;
    let match;

    while ((match = regex.exec(attrString)) !== null) {
      attrs.set(match[1], match[2]);
    }

    return attrs;
  }

  /**
   * 判断是否是空白字符
   */
  private isWhitespace(char: string): boolean {
    return /\s/.test(char);
  }

  /**
   * 获取位置所在的行号
   */
  private lineAt(position: number): number {
    // 简化实现，实际需要计算换行符
    return 1;
  }
}

interface Token {
  type: 'startTag' | 'endTag' | 'text';
  name?: string;
  value?: string;
  attributes?: Map<string, string>;
  position: number;
}
```

---

## 处理动态 SQL 标签

### MyBatis 动态标签类型

```typescript
/**
 * MyBatis 动态标签配置
 */
const MYBATIS_TAGS = {
  // 条件标签
  'if': { keepContent: true },
  'choose': { keepContent: true },
  'when': { keepContent: true },
  'otherwise': { keepContent: true },

  // 循环标签
  'foreach': { keepContent: true },

  // SQL 片段
  'sql': { keepContent: true },
  'include': { keepContent: false },

  // 结果映射
  'resultMap': { keepContent: true },
  'result': { keepContent: true },
  'association': { keepContent: true },
  'collection': { keepContent: true },

  // 其他
  'where': { keepContent: true, trim: true },
  'set': { keepContent: true, trim: true },
  'bind': { keepContent: true },
  'trim': { keepContent: true, custom: true }
};
```

### 实际格式化示例

**输入**：

```xml
<select id="findActiveUsersWithName" resultMap="BaseResultMap">
    SELECT id,username,email,create_time FROM users WHERE status = 1
    <if test="name != null and name != ''">
    AND username LIKE CONCAT('%',#{name},'%')
    </if>
    <choose>
    <when test="orderBy == 'username'">
    ORDER BY username ASC
    </when>
    <when test="orderBy == 'email'">
    ORDER BY email ASC
    </when>
    <otherwise>
    ORDER BY create_time DESC
    </otherwise>
    </choose>
</select>
```

**CST 解析后的结构**：

```
Element(select)
├── Attribute(id="findActiveUsersWithName")
├── Attribute(resultMap="BaseResultMap")
└── Children:
    ├── Text("SELECT id, username, email, create_time FROM users WHERE status = 1")
    ├── Element(if)
    │   ├── Attribute(test="name != null and name != ''")
    │   └── Children:
    │       └── Text("AND username LIKE CONCAT('%', #{name}, '%')")
    └── Element(choose)
        └── Children:
            ├── Element(when)
            │   ├── Attribute(test="orderBy == 'username'")
            │   └── Children:
            │       └── Text("ORDER BY username ASC")
            ├── Element(when)
            │   ├── Attribute(test="orderBy == 'email'")
            │   └── Children:
            │       └── Text("ORDER BY email ASC")
            └── Element(otherwise)
                └── Children:
                    └── Text("ORDER BY create_time DESC")
```

**格式化后的输出**：

```xml
<select id="findActiveUsersWithName" resultMap="BaseResultMap">
    SELECT
        id,
        username,
        email,
        create_time
    FROM
        users
    WHERE
        status = 1
    <if test="name != null and name != ''">
        AND username LIKE CONCAT('%', #{name}, '%')
    </if>
    <choose>
        <when test="orderBy == 'username'">
            ORDER BY username ASC
        </when>
        <when test="orderBy == 'email'">
            ORDER BY email ASC
        </when>
        <otherwise>
            ORDER BY create_time DESC
        </otherwise>
    </choose>
</select>
```

---

## 多方言支持

### 支持的 SQL 方言

```typescript
/**
 * 支持的 SQL 方言
 */
type SQLDialect =
  | 'auto'          // 自动检测
  | 'mysql'         // MySQL
  | 'postgresql'    // PostgreSQL
  | 'oracle'        // Oracle
  | 'tsql'          // T-SQL (SQL Server)
  | 'sqlite'        // SQLite
  | 'bigquery';     // Google BigQuery
```

### 方言特定格式化

```typescript
/**
 * 根据方言格式化 SQL
 */
private formatSQLWithDialect(sql: string, dialect: SQLDialect): string {
  const config: FormatConfig = {
    language: dialect === 'auto' ? undefined : dialect,
    keywordCase: this.getKeywordCase(),
    tabWidth: this.getTabWidth(),
    // 方言特定选项
    ...this.getDialectOptions(dialect)
  };

  return format(sql, config);
}

/**
 * 获取方言特定选项
 */
private getDialectOptions(dialect: SQLDialect): Partial<FormatConfig> {
  switch (dialect) {
    case 'mysql':
      return {
        // MySQL 特定格式化选项
        identifierStyle: 'quoted'  // `table_name`
      };

    case 'postgresql':
      return {
        // PostgreSQL 特定格式化选项
        identifierStyle: 'quoted'  // "table_name"
      };

    case 'oracle':
      return {
        // Oracle 特定格式化选项
        identifierStyle: 'upper'   // TABLE_NAME
      };

    case 'tsql':
      return {
        // T-SQL 特定格式化选项
        identifierStyle: 'bracket' // [table_name]
      };

    default:
      return {};
  }
}
```

---

## 性能优化

### 解析优化

```typescript
/**
 * 增量格式化：只格式化变更的部分
 */
export class IncrementalFormatter {
  private cache = new Map<string, CSTNode>();

  /**
   * 格式化（带缓存）
   */
  format(xmlContent: string, changedRanges: vscode.Range[]): string {
    // 如果没有变更范围，使用缓存
    if (changedRanges.length === 0 && this.cache.has('root')) {
      return this.serializeCST(this.cache.get('root')!);
    }

    // 重新解析
    const cst = this.parseToCST(xmlContent);
    this.cache.set('root', cst);

    // 只格式化变更范围内的 SQL
    for (const range of changedRanges) {
      this.formatRange(cst, range);
    }

    return this.serializeCST(cst);
  }

  /**
   * 格式化特定范围
   */
  private formatRange(cst: CSTNode, range: vscode.Range): void {
    // 找到范围内的节点
    const nodes = this.findNodesInRange(cst, range);

    // 只格式化这些节点
    for (const node of nodes) {
      if (node.type === 'text') {
        node.value = this.formatSQL(node.value);
      }
    }
  }
}
```

---

## 总结

### 关键要点

1. **正则表达式的局限**
   - 无法处理嵌套结构
   - 无法区分上下文
   - 难以正确处理字符串和注释

2. **CST 的优势**
   - 结构感知，理解嵌套
   - 上下文相关，精确操作
   - 可扩展，易于维护

3. **mybatis-boost 实现**
   - 自定义 Tokenizer
   - CST Parser
   - SQL Formatter 集成
   - CST Serializer

4. **动态标签支持**
   - 保留标签结构
   - 只格式化 SQL 文本
   - 正确处理缩进

5. **多方言支持**
   - MySQL, PostgreSQL, Oracle, TSQL
   - 方言特定格式化选项
   - 自动检测

### 下一步

在下一章中，我们将学习 **Provider 模式**：
- 为什么使用 Provider 模式
- MCP Manager 的实现
- 支持 Cursor 和 Copilot
- 中间抽象层设计

---

## 进一步阅读

### 源代码
- `C:\PythonProject\mybatis-boost\src\formatter\MybatisSqlFormatter.ts`
- `C:\PythonProject\mybatis-boost\src\test\unit\formatter\`

### 相关资源
- [sql-formatter 文档](https://github.com/sql-formatter/sql-formatter)
- [MyBatis 动态 SQL 文档](https://mybatis.org/mybatis-3/dynamic-sql.html)

### 相关章节
- [Chapter 14 - 项目概览](chapter-14-project-overview.md)
- [Chapter 16 - Provider 模式](chapter-16-provider-pattern.md)

---

## 练习

完成以下练习：

1. **理解练习**
   - [ ] 分析为什么正则表达式无法处理嵌套 XML
   - [ ] 理解 CST 的节点类型
   - [ ] 学习 MyBatis 动态标签类型

2. **代码练习**
   - [ ] 阅读 MybatisSqlFormatter.ts 源代码
   - [ ] 尝试编写一个简单的 XML tokenizer
   - [ ] 测试格式化不同方言的 SQL

3. **实战练习**
   - [ ] 使用 mybatis-boost 格式化你的 MyBatis XML
   - [ ] 对比正则表达式和 CST 的效果
   - [ ] 贡献对新的 SQL 方言的支持

---

**上一章**: [Chapter 14 - 项目概览](chapter-14-project-overview.md)
**下一章**: [Chapter 16 - Provider 模式](chapter-16-provider-pattern.md)
