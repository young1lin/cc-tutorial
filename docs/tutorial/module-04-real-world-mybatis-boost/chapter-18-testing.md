# Chapter 18: 测试与质量保证

**模块**: Module 4 - mybatis-boost 实战案例
**预计阅读时间**: 16 分钟
**难度**: ⭐⭐⭐

---

## 学习目标

本章结束后，你将能够：

- [ ] 理解 mybatis-boost 的测试策略
- [ ] 掌握单元测试的编写方法
- [ ] 学习集成测试的组织
- [ ] 了解 CI/CD 的集成实践

---

## 前置知识

- [ ] 已完成 Chapter 17 - 性能优化
- [ ] 了解 Mocha 测试框架
- [ ] 熟悉 TypeScript 测试

---

## 测试策略概述

### 测试金字塔

```
┌─────────────────────────────────────────────────────────┐
│              测试金字塔                                  │
├─────────────────────────────────────────────────────────┤
│                                                         │
│                   /E2E Tests\                          │
│                  /------------\                         │
│                 /  15 tests   \                        │
│                /   (slow)      \                       │
│               /----------------\                       │
│              / Integration Tests \                    │
│             /--------------------\                     │
│            /      ~30 tests        \                  │
│           /      (medium)            \                │
│          /----------------------------\               │
│         /      Unit Tests                \            │
│        /      ~106 tests                   \          │
│       /      (fast)                          \        │
│      /------------------------------------------\     │
│                                                         │
│  单元测试 (Unit Tests)                                   │
│  • 测试单个函数、类                                    │
│  • 快速执行 (~1ms each)                                │
│  • 106+ 测试                                            │
│                                                         │
│  集成测试 (Integration Tests)                           │
│  • 测试模块交互                                        │
│  • 中等执行时间 (~10-100ms each)                       │
│  • ~30 测试                                             │
│                                                         │
│  E2E 测试 (End-to-End Tests)                            │
│  • 测试完整用户流程                                    │
│  • 较慢执行 (~1-5s each)                               │
│  • ~15 测试                                             │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 测试覆盖目标

```
┌─────────────────────────────────────────────────────────┐
│              测试覆盖目标                                │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  代码覆盖率：                                            │
│  • 语句覆盖: > 80%                                      │
│  • 分支覆盖: > 75%                                      │
│  • 函数覆盖: > 85%                                      │
│                                                         │
│  模块覆盖：                                              │
│  ✓ FileMapper (LRU 缓存)                              │
│  ✓ 解析器 (Java, XML, SQL)                             │
│  ✓ Provider (Cursor, Copilot)                          │
│  ✓ 转换器 (SQL, 参数)                                  │
│  ✓ 格式化器 (CST)                                       │
│                                                         │
│  场景覆盖：                                              │
│  ✓ 正常路径                                             │
│  ✓ 边界条件                                             │
│  ✓ 错误处理                                             │
│  ✓ 并发场景                                             │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 单元测试

### 测试框架配置

**package.json**:

```json
{
  "scripts": {
    "test": "mocha out/test/**/*.test.js",
    "test:unit": "mocha out/test/unit/**/*.test.js",
    "test:integration": "mocha out/test/integration/**/*.test.js",
    "test:coverage": "nyc mocha out/test/**/*.test.js"
  },
  "devDependencies": {
    "@types/mocha": "^10.0.0",
    "@vscode/test-electron": "^2.3.0",
    "mocha": "^10.0.0",
    "nyc": "^15.0.0",
    "assert": "^2.0.0"
  }
}
```

**.mocharc.json**:

```json
{
  "timeout": 5000,
  "require": ["source-map-support/register"],
  "include": ["out/test/**/**/*.test.js"],
  "reporter": ["spec"],
  "recursive": true
}
```

### FileMapper 单元测试

**src/test/unit/FileMapper.test.ts**:

```typescript
import * as assert from 'assert';
import * as vscode from 'vscode';
import { FileMapper } from '../../navigator/core/FileMapper';
import { createTestContext } from '../helpers';

/**
 * FileMapper 单元测试
 */
suite('FileMapper', () => {
  let fileMapper: FileMapper;
  let testContext: vscode.ExtensionContext;

  setup(() => {
    // 创建测试上下文
    testContext = createTestContext();

    // 创建 FileMapper 实例
    fileMapper = new FileMapper();
  });

  teardown(() => {
    // 清理资源
    fileMapper.dispose();
    testContext?.dispose();
  });

  /**
   * 测试快速路径（策略 1）
   */
  suite('Quick Path Strategy', () => {
    test('should find XML in same directory', async () => {
      // Arrange
      const javaFile = '/test/UserMapper.java';
      const expectedXml = '/test/UserMapper.xml';

      // 创建测试文件
      await createTestFile(expectedXml, '<mapper></mapper>');

      // Act
      const result = await fileMapper.findXmlForJava(javaFile);

      // Assert
      assert.strictEqual(result.length, 1);
      assert.strictEqual(result[0].target, expectedXml);
      assert.strictEqual(result[0].type, 'java-to-xml');
    });

    test('should return empty array when XML not found', async () => {
      // Arrange
      const javaFile = '/test/NonExistentMapper.java';

      // Act
      const result = await fileMapper.findXmlForJava(javaFile);

      // Assert
      assert.strictEqual(result.length, 0);
    });
  });

  /**
   * 测试缓存功能
   */
  suite('LRU Cache', () => {
    test('should cache mapping results', async () => {
      // Arrange
      const javaFile = '/test/UserMapper.java';
      const xmlFile = '/test/UserMapper.xml';
      await createTestFile(xmlFile, '<mapper></mapper>');

      // Act - 第一次调用
      const startTime1 = Date.now();
      const result1 = await fileMapper.findXmlForJava(javaFile);
      const duration1 = Date.now() - startTime1;

      // Act - 第二次调用（应该命中缓存）
      const startTime2 = Date.now();
      const result2 = await fileMapper.findXmlForJava(javaFile);
      const duration2 = Date.now() - startTime2;

      // Assert
      assert.strictEqual(result1.length, result2.length);
      assert.strictEqual(result1[0].target, result2[0].target);

      // 缓存命中应该快得多
      assert.ok(duration2 < duration1, 'Cache should be faster');
    });

    test('should invalidate cache on file change', async () => {
      // Arrange
      const javaFile = '/test/UserMapper.java';
      const xmlFile = '/test/UserMapper.xml';

      // 创建初始文件
      await createTestFile(xmlFile, '<mapper namespace="old"></mapper>');

      // 第一次调用并缓存
      const result1 = await fileMapper.findXmlForJava(javaFile);
      assert.strictEqual(result1.length, 1);

      // 修改文件
      await updateTestFile(xmlFile, '<mapper namespace="new"></mapper>');

      // 等待文件监听器处理
      await sleep(100);

      // 第二次调用（缓存应该失效）
      const result2 = await fileMapper.findXmlForJava(javaFile);
      assert.strictEqual(result2.length, 1);
      // 验证是否获取了新内容
    });

    test('should respect cache size limit', async () => {
      // Arrange
      const cacheSize = 10; // 设置较小的缓存
      const config = vscode.workspace.getConfiguration('mybatis-boost');
      await config.update('cacheSize', cacheSize, vscode.ConfigurationTarget.Workspace);

      // 创建超过缓存大小的映射
      for (let i = 0; i < cacheSize + 5; i++) {
        const javaFile = `/test/Mapper${i}.java`;
        const xmlFile = `/test/Mapper${i}.xml`;
        await createTestFile(xmlFile, `<mapper id="mapper${i}"></mapper>`);

        await fileMapper.findXmlForJava(javaFile);
      }

      // Act
      const stats = fileMapper.getCacheStats();

      // Assert
      assert.ok(stats.javaToXml.size <= cacheSize, 'Cache should not exceed max size');
    });
  });

  /**
   * 测试自定义路径（策略 2）
   */
  suite('Custom Path Strategy', () => {
    test('should find XML in custom directory', async () => {
      // Arrange
      const customDir = '/test/custom/mappers';
      const javaFile = '/test/UserMapper.java';
      const xmlFile = `${customDir}/UserMapper.xml`;

      // 配置自定义路径
      const config = vscode.workspace.getConfiguration('mybatis-boost');
      await config.update(
        'customXmlDirectories',
        [customDir],
        vscode.ConfigurationTarget.Workspace
      );

      await createTestFile(xmlFile, '<mapper></mapper>');

      // Act
      const result = await fileMapper.findXmlForJava(javaFile);

      // Assert
      assert.strictEqual(result.length, 1);
      assert.strictEqual(result[0].target, xmlFile);
    });
  });

  /**
   * 测试工作区搜索（策略 3）
   */
  suite('Workspace Search Strategy', () => {
    test('should search workspace when quick path fails', async () => {
      // Arrange
      const javaFile = '/test/UserMapper.java';
      const xmlFile = '/some/other/path/UserMapper.xml';

      await createTestFile(xmlFile, '<mapper></mapper>');

      // Act
      const result = await fileMapper.findXmlForJava(javaFile);

      // Assert
      assert.ok(result.length > 0);
      assert.ok(result.some(r => r.target === xmlFile));
    });
  });

  /**
   * 测试双向映射
   */
  suite('Bi-directional Mapping', () => {
    test('should map Java → XML and XML → Java', async () => {
      // Arrange
      const javaFile = '/test/UserMapper.java';
      const xmlFile = '/test/UserMapper.xml';

      await createTestFile(xmlFile, `
        <mapper namespace="com.example.mapper.UserMapper">
          <select id="findUser">SELECT * FROM users</select>
        </mapper>
      `);

      // Act - Java → XML
      const javaToXml = await fileMapper.findXmlForJava(javaFile);

      // Act - XML → Java
      const xmlToJava = await fileMapper.findJavaForXml(xmlFile);

      // Assert
      assert.strictEqual(javaToXml.length, 1);
      assert.strictEqual(javaToXml[0].target, xmlFile);

      assert.strictEqual(xmlToJava.length, 1);
      assert.strictEqual(xmlToJava[0].target, javaFile);
    });
  });

  /**
   * 测试错误处理
   */
  suite('Error Handling', () => {
    test('should handle file not found gracefully', async () => {
      // Arrange
      const javaFile = '/test/NonExistent.java';

      // Act & Assert - 不应该抛出异常
      const result = await fileMapper.findXmlForJava(javaFile);

      assert.strictEqual(result.length, 0);
    });

    test('should handle invalid XML gracefully', async () => {
      // Arrange
      const xmlFile = '/test/Invalid.xml';
      await createTestFile(xmlFile, '<invalid xml content');

      // Act & Assert
      const result = await fileMapper.findJavaForXml(xmlFile);

      // 应该返回空数组，不抛出异常
      assert.ok(Array.isArray(result));
    });
  });

  /**
   * 测试并发场景
   */
  suite('Concurrent Access', () => {
    test('should handle concurrent requests', async () => {
      // Arrange
      const requests = [];
      for (let i = 0; i < 100; i++) {
        const javaFile = `/test/Mapper${i}.java`;
        const xmlFile = `/test/Mapper${i}.xml`;
        await createTestFile(xmlFile, `<mapper id="mapper${i}"></mapper>`);
        requests.push(fileMapper.findXmlForJava(javaFile));
      }

      // Act - 并发执行
      const results = await Promise.all(requests);

      // Assert
      assert.strictEqual(results.length, 100);
      for (const result of results) {
        assert.ok(Array.isArray(result));
      }
    });
  });
});

/**
 * 测试辅助函数
 */
async function createTestFile(path: string, content: string): Promise<void> {
  const uri = vscode.Uri.file(path);
  await vscode.workspace.fs.writeFile(uri, Buffer.from(content));
}

async function updateTestFile(path: string, content: string): Promise<void> {
  const uri = vscode.Uri.file(path);
  await vscode.workspace.fs.writeFile(uri, Buffer.from(content));
}

function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}
```

### 解析器单元测试

**src/test/unit/parser/javaParser.test.ts**:

```typescript
import * as assert from 'assert';
import { JavaParser } from '../../../navigator/parsers/javaParser';

suite('JavaParser', () => {
  let parser: JavaParser;

  setup(() => {
    parser = new JavaParser();
  });

  suite('parseInterface', () => {
    test('should parse simple interface', () => {
      // Arrange
      const javaCode = `
        package com.example.mapper;

        public interface UserMapper {
          User findById(Long id);
          List<User> findAll();
        }
      `;

      // Act
      const result = parser.parseInterface(javaCode, 'UserMapper.java');

      // Assert
      assert.strictEqual(result.package, 'com.example.mapper');
      assert.strictEqual(result.name, 'UserMapper');
      assert.strictEqual(result.methods.length, 2);
      assert.strictEqual(result.methods[0].name, 'findById');
      assert.strictEqual(result.methods[1].name, 'findAll');
    });

    test('should parse method with annotations', () => {
      // Arrange
      const javaCode = `
        @Mapper
        public interface UserMapper {
          @Select("SELECT * FROM users WHERE id = #{id}")
          User findById(@Param("id") Long id);
        }
      `;

      // Act
      const result = parser.parseInterface(javaCode, 'UserMapper.java');

      // Assert
      assert.strictEqual(result.methods.length, 1);
      assert.strictEqual(result.methods[0].annotations.length, 2);
    });
  });

  suite('parseMethod', () => {
    test('should parse method signature', () => {
      // Arrange
      const method = 'List<User> findByStatusAndEmail(@Param("status") String status, @Param("email") String email);';

      // Act
      const result = parser.parseMethod(method);

      // Assert
      assert.strictEqual(result.returnType, 'List<User>');
      assert.strictEqual(result.name, 'findByStatusAndEmail');
      assert.strictEqual(result.parameters.length, 2);
      assert.strictEqual(result.parameters[0].type, 'String');
      assert.strictEqual(result.parameters[0].name, 'status');
    });
  });
});
```

---

## 集成测试

### 集成测试框架

**src/test/integration/navigation.test.ts**:

```typescript
import * as assert from 'assert';
import * as vscode from 'vscode';
import { FileMapper } from '../../navigator/core/FileMapper';
import { JavaToXmlDefinitionProvider } from '../../navigator/providers/JavaToXmlDefinitionProvider';

/**
 * 导航功能集成测试
 */
suite('Navigation Integration Tests', () => {
  let extensionContext: vscode.ExtensionContext;
  let fileMapper: FileMapper;
  let definitionProvider: JavaToXmlDefinitionProvider;

  suiteSetup(async () => {
    // 激活扩展
    const ext = vscode.extensions.getExtension('young1lin.mybatis-boot');
    if (ext) {
      await ext.activate();
      extensionContext = ext.exports;
    }

    // 初始化组件
    fileMapper = new FileMapper();
    definitionProvider = new JavaToXmlDefinitionProvider(fileMapper);
  });

  suiteTeardown(() => {
    fileMapper?.dispose();
  });

  /**
   * 测试完整的导航流程
   */
  suite('Complete Navigation Flow', () => {
    test('should navigate from Java method to XML statement', async () => {
      // Arrange - 创建测试文件
      const workspaceFolder = vscode.workspace.workspaceFolders![0].uri;
      const javaUri = vscode.Uri.joinPath(workspaceFolder, 'UserMapper.java');
      const xmlUri = vscode.Uri.joinPath(workspaceFolder, 'UserMapper.xml');

      // 写入测试文件
      await vscode.workspace.fs.writeFile(javaUri, Buffer.from(`
        package com.example.mapper;

        public interface UserMapper {
          User findById(Long id);
        }
      `));

      await vscode.workspace.fs.writeFile(xmlUri, Buffer.from(`
        <?xml version="1.0" encoding="UTF-8"?>
        <!DOCTYPE mapper PUBLIC "-//mybatis.org//DTD Mapper 3.0//EN"
          "http://mybatis.org/dtd/mybatis-3-mapper.dtd">
        <mapper namespace="com.example.mapper.UserMapper">
          <select id="findById" resultType="User">
            SELECT * FROM users WHERE id = #{id}
          </select>
        </mapper>
      `));

      // 打开 Java 文件
      const document = await vscode.workspace.openTextDocument(javaUri);
      const editor = await vscode.window.showTextDocument(document);

      // 定位到方法名
      const position = new vscode.Position(4, 10); // "findById"

      // Act - 获取定义
      const definition = await definitionProvider.provideDefinition(
        document.uri,
        position,
        new vscode.CancellationTokenSource().token
      );

      // Assert
      assert.ok(definition);
      assert.ok(definition.length > 0);
      assert.strictEqual(definition[0].uri.path, xmlUri.path);
    });
  });

  /**
   * 测试复杂映射场景
   */
  suite('Complex Mapping Scenarios', () => {
    test('should handle multiple result maps', async () => {
      // 创建包含多个 resultMap 的 XML
      // 验证导航到正确的 resultMap 定义
    });

    test('should handle sql fragments', async () => {
      // 创建包含 <include refid> 的 XML
      // 验证导航到 SQL 片段定义
    });
  });
});
```

---

## 测试夹具

### 测试数据准备

**src/test/fixtures/createTestProject.ts**:

```typescript
import * as vscode from 'vscode';
import * as path from 'path';

/**
 * 创建测试项目
 */
export async function createTestProject(workspaceFolder: vscode.Uri): Promise<void> {
  // 创建目录结构
  const dirs = [
    'src/main/java/com/example/mapper',
    'src/main/java/com/example/model',
    'src/main/resources/mapper',
    'src/test/java/com/example'
  ];

  for (const dir of dirs) {
    const dirUri = vscode.Uri.joinPath(workspaceFolder, dir);
    await vscode.workspace.fs.createDirectory(dirUri);
  }

  // 创建测试文件
  await createMapperFiles(workspaceFolder);
  await createModelFiles(workspaceFolder);
  await createXmlFiles(workspaceFolder);
}

/**
 * 创建 Mapper 接口
 */
async function createMapperFiles(workspaceFolder: vscode.Uri): Promise<void> {
  const mapperDir = 'src/main/java/com/example/mapper';

  const userMapper = `
    package com.example.mapper;

    import com.example.model.User;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import java.util.List;

@Mapper
public interface UserMapper {
    User findById(Long id);
    List<User> findAll();
    List<User> findByStatus(@Param("status") String status);
    int insert(User user);
    int updateById(User user);
    int deleteById(Long id);
}
  `;

  const uri = vscode.Uri.joinPath(workspaceFolder, `${mapperDir}/UserMapper.java`);
  await vscode.workspace.fs.writeFile(uri, Buffer.from(userMapper));
}

/**
 * 创建 XML Mapper 文件
 */
async function createXmlFiles(workspaceFolder: vscode.Uri): Promise<void> {
  const xmlDir = 'src/main/resources/mapper';

  const userMapperXml = `
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE mapper PUBLIC "-//mybatis.org//DTD Mapper 3.0//EN"
  "http://mybatis.org/dtd/mybatis-3-mapper.dtd">
<mapper namespace="com.example.mapper.UserMapper">

  <resultMap id="BaseResultMap" type="com.example.model.User">
    <id column="id" property="id" jdbcType="BIGINT"/>
    <result column="username" property="username" jdbcType="VARCHAR"/>
    <result column="email" property="email" jdbcType="VARCHAR"/>
    <result column="status" property="status" jdbcType="VARCHAR"/>
    <result column="create_time" property="createTime" jdbcType="TIMESTAMP"/>
  </resultMap>

  <sql id="Base_Column_List">
    id, username, email, status, create_time
  </sql>

  <select id="findById" resultMap="BaseResultMap">
    SELECT
    <include refid="Base_Column_List"/>
    FROM users
    WHERE id = #{id}
  </select>

  <select id="findAll" resultMap="BaseResultMap">
    SELECT
    <include refid="Base_Column_List"/>
    FROM users
    ORDER BY id
  </select>

  <select id="findByStatus" resultMap="BaseResultMap">
    SELECT
    <include refid="Base_Column_List"/>
    FROM users
    WHERE status = #{status}
    ORDER BY id
  </select>

  <insert id="insert" parameterType="com.example.model.User" useGeneratedKeys="true" keyProperty="id">
    INSERT INTO users (username, email, status, create_time)
    VALUES (#{username}, #{email}, #{status}, #{createTime})
  </insert>

  <update id="updateById" parameterType="com.example.model.User">
    UPDATE users
    <set>
      <if test="username != null">username = #{username},</if>
      <if test="email != null">email = #{email},</if>
      <if test="status != null">status = #{status},</if>
      <if test="createTime != null">create_time = #{createTime},</if>
    </set>
    WHERE id = #{id}
  </update>

  <delete id="deleteById">
    DELETE FROM users WHERE id = #{id}
  </delete>

</mapper>
  `;

  const uri = vscode.Uri.joinPath(workspaceFolder, `${xmlDir}/UserMapper.xml`);
  await vscode.workspace.fs.writeFile(uri, Buffer.from(userMapperXml));
}

/**
 * 创建 Model 文件
 */
async function createModelFiles(workspaceFolder: vscode.Uri): Promise<void> {
  const modelDir = 'src/main/java/com/example/model';

  const userModel = `
    package com.example.model;

    import java.io.Serializable;
    java.util.Date;

public class User implements Serializable {
    private Long id;
    private String username;
    private String email;
    private String status;
    private Date createTime;

    // Getters and Setters
    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getUsername() {
        return username;
    }

    public void setUsername(String username) {
        this.username = username;
    }

    public String getEmail() {
        return email;
    }

    public void setEmail(String email) {
        this.email = email;
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }

    public Date getCreateTime() {
        return createTime;
    }

    public void setCreateTime(Date createTime) {
        this.createTime = createTime;
    }
}
  `;

  const uri = vscode.Uri.joinPath(workspaceFolder, `${modelDir}/User.java`);
  await vscode.workspace.fs.writeFile(uri, Buffer.from(userModel));
}
```

---

## CI/CD 集成

### GitHub Actions 配置

**.github/workflows/test.yml**:

```yaml
name: Test

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  test:
    runs-on: ubuntu-latest

    strategy:
      matrix:
        node-version: [16.x, 18.x, 20.x]

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: ${{ matrix.node-version }}

      - name: Install pnpm
        run: npm install -g pnpm

      - name: Install dependencies
        run: pnpm install

      - name: Compile TypeScript
        run: pnpm run compile

      - name: Run linter
        run: pnpm run lint

      - name: Run type check
        run: pnpm run check-types

      - name: Run unit tests
        run: pnpm run test:unit

      - name: Run integration tests
        run: pnpm run test:integration

      - name: Generate coverage report
        run: pnpm run test:coverage

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage/lcov.info
          flags: unittests
          name: codecov-umbrella

  e2e:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: 20.x

      - name: Install pnpm
        run: npm install -g pnpm

      - name: Install dependencies
        run: pnpm install

      - name: Compile TypeScript
        run: pnpm run compile

      - name: Run E2E tests
        run: pnpm run test:e2e

      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: e2e-test-results
          path: test-results/
```

---

## 质量保证

### 代码质量检查

```bash
# 类型检查
pnpm run check-types

# 代码检查
pnpm run lint

# 自动修复
pnpm run lint:fix

# 测试
pnpm test

# 覆盖率
pnpm run test:coverage
```

### Pre-commit Hook

**.husky/pre-commit**:

```bash
#!/bin/sh
. "$(dirname "$0")/_/husky.sh"

# 类型检查
echo "Running type check..."
pnpm run check-types
if [ $? -ne 0 ]; then
  echo "❌ Type check failed"
  exit 1
fi

# 代码检查
echo "Running linter..."
pnpm run lint
if [ $? -ne 0 ]; then
  echo "❌ Lint failed"
  echo "Run 'pnpm run lint:fix' to auto-fix"
  exit 1
fi

# 运行测试
echo "Running tests..."
pnpm run test:unit
if [ $? -ne 0 ]; then
  echo "❌ Tests failed"
  exit 1
fi

echo "✅ All checks passed!"
```

---

## 总结

### 关键要点

1. **测试策略**
   - 单元测试：快速、独立
   - 集成测试：模块交互
   - E2E 测试：完整流程

2. **测试覆盖**
   - 代码覆盖率 > 80%
   - 核心模块 100% 覆盖
   - 关键路径全覆盖

3. **测试工具**
   - Mocha 测试框架
   - nyc 覆盖率工具
   - VS Code 测试 API

4. **CI/CD**
   - GitHub Actions
   - 多 Node.js 版本测试
   - 自动化覆盖率报告

### Module 4 总结

恭喜！你已完成 **Module 4 - mybatis-boost 实战案例**！

### 你已经掌握了：

**Chapter 14**: 项目概览与架构
- 项目规模和特点
- 整体架构设计
- 核心模块组织

**Chapter 15**: CST vs 正则表达式
- 为什么使用 CST
- CST 解析器实现
- 动态 SQL 标签处理

**Chapter 16**: Provider 模式
- 支持多种 AI 工具
- MCP Manager 实现
- 接口抽象和扩展

**Chapter 17**: 性能优化
- LRU 缓存实现
- 文件监听器
- 优先级策略

**Chapter 18**: 测试与 QA
- 单元测试
- 集成测试
- CI/CD 集成

### 项目亮点

mybatis-boost 展示了：
- ✅ 企业级 VS Code 扩展开发
- ✅ 高性能导航系统（P50 < 100ms）
- ✅ 创新的 CST 解析器
- ✅ Provider 模式的灵活架构
- ✅ 完善的测试覆盖

### 当前进度

```
总进度: 25/39 章节 (64.1%)

✅ Module 1: Fundamentals (4/4) - 100% COMPLETE
✅ Module 2: Core Workflows (4/4) - 100% COMPLETE
✅ Module 3: Advanced Features (5/5) - 100% COMPLETE
✅ Module 4: mybatis-boost 实战 (5/5) - 100% COMPLETE
📋 Module 5: 架构与设计模式 (0/4) - NEXT
📋 Modules 6-10: PENDING
```

### 准备好继续学习了吗？

**Module 5 - 架构与设计模式** 将教你：
- 整洁架构原则
- 洋葱架构与六边形架构
- 可测试性与 Mocking
- AAA 模式与测试最佳实践

继续你的学习之旅吧！

---

## 进一步阅读

### 项目文件
- `C:\PythonProject\mybatis-boost\src\test\`
- `C:\PythonProject\mybatis-boost\.github\workflows\`

### 相关章节
- [Chapter 5 - TDD](../module-02-core-workflows/chapter-06-tdd.md)
- [Chapter 22 - AAA 模式](../module-05-architecture/chapter-22-aaa-pattern.md)

---

## 练习

完成以下练习：

1. **理解练习**
   - [ ] 分析 mybatis-boost 的测试策略
   - [ ] 理解测试金字塔的应用
   - [ ] 学习 CI/CD 的最佳实践

2. **代码练习**
   - [ ] 阅读单元测试示例
   - [ ] 编写一个 FileMapper 测试
   - [ ] 创建测试夹具

3. **实战练习**
   - [ ] 为你的项目设置测试框架
   - [ ] 配置 GitHub Actions
   - [ ] 实现测试覆盖率目标

---

**上一章**: [Chapter 17 - 性能优化](chapter-17-performance.md)
**下一模块**: [Module 5 - 架构与设计模式](../module-05-architecture/)
