# Chapter 14: mybatis-boost 项目概览与架构

**模块**: Module 4 - mybatis-boost 实战案例
**预计阅读时间**: 18 分钟
**难度**: ⭐⭐⭐⭐

---

## 学习目标

本章结束后，你将能够：

- [ ] 了解 mybatis-boost 项目的设计理念和功能
- [ ] 掌握项目的整体架构设计
- [ ] 理解模块化组织和职责分离
- [ ] 学习企业级 VS Code 扩展开发最佳实践

---

## 前置知识

- [ ] 已完成 Module 3 - 高级功能
- [ ] 了解 MyBatis 框架基础
- [ ] 熟悉 VS Code 扩展 API

---

## 项目简介

### 什么是 mybatis-boost？

**mybatis-boost** 是一个功能强大的 VS Code 扩展，
为 MyBatis 框架提供一站式开发支持。

```
┌─────────────────────────────────────────────────────────┐
│              mybatis-boost 核心功能                      │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  🔍 双向导航                                            │
│     • Java ↔ XML Mapper                               │
│     • 方法 ↔ SQL 语句                                  │
│     • 10 种导航模式                                     │
│                                                         │
│  🤖 AI 代码生成                                         │
│     • DDL → 代码生成                                    │
│     • MCP 支持（Cursor/Copilot）                        │
│     • EJS 模板引擎                                      │
│                                                         │
│  📋 SQL 控制台拦截                                      │
│     • 实时日志拦截                                      │
│     • 参数替换                                          │
│     • 可执行 SQL                                        │
│                                                         │
│  🎨 格式化与高亮                                        │
│     • CST 解析器                                        │
│     • 动态 SQL 支持                                     │
│     • 语法高亮                                          │
│                                                         │
│  ✅ 实时验证                                            │
│     • 参数检查                                          │
│     • 诊断信息                                          │
│     • 快速修复                                          │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 项目规模

```
┌─────────────────────────────────────────────────────────┐
│              项目统计数据                                │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  📊 代码量                                              │
│     • 99 个 TypeScript 源文件                          │
│     • ~24,123 行代码                                    │
│     • 106+ 单元测试                                     │
│                                                         │
│  📦 依赖                                                │
│     • 主要依赖: 20+                                     │
│     • 开发依赖: 15+                                     │
│     • TypeScript 5.9.3                                  │
│                                                         │
│  🧪 测试覆盖                                            │
│     • 单元测试: 106+ 通过                              │
│     • 集成测试: 15+ 通过                               │
│     • 测试框架: Mocha                                   │
│                                                         │
│  📚 文档                                                │
│     • README.md                                         │
│     • CLAUDE.md                                         │
│     • PRD.md                                            │
│     • MCP 服务器文档                                    │
│                                                         │
│  🌍 国际化                                              │
│     • 英语 (en)                                         │
│     • 简体中文 (zh-cn)                                  │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 项目架构

### 整体架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                    mybatis-boost 架构                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │                    VS Code Extension API                   │ │
│  └───────────────────────────────────────────────────────────┘ │
│                              ↑↓                                │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │                   Extension Layer                         │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │ │
│  │  │   Navigator  │  │  Generator   │  │   Console    │    │ │
│  │  │   System     │  │    System    │  │  Interceptor │    │ │
│  │  └──────────────┘  └──────────────┘  └──────────────┘    │ │
│  └───────────────────────────────────────────────────────────┘ │
│                              ↑↓                                │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │                    Core Services                          │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │ │
│  │  │  FileMapper  │  │   Formatter  │  │  Diagnostic  │    │ │
│  │  │  (LRU Cache) │  │  (CST Parse) │  │   System     │    │ │
│  │  └──────────────┘  └──────────────┘  └──────────────┘    │ │
│  └───────────────────────────────────────────────────────────┘ │
│                              ↑↓                                │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │                    Parsers Layer                          │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │ │
│  │  │ Java Parser  │  │   XML Parser │  │  SQL Parser  │    │ │
│  │  └──────────────┘  └──────────────┘  └──────────────┘    │ │
│  └───────────────────────────────────────────────────────────┘ │
│                              ↑↓                                │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │                    Utilities & Utils                      │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │ │
│  │  │   Path Utils │  │  Config Mgr  │  │   I18n       │    │ │
│  │  └──────────────┘  └──────────────┘  └──────────────┘    │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │                    MCP Integration                        │ │
│  │  ┌──────────────┐  ┌──────────────┐                       │ │
│  │  │ MCP Manager  │  │  MCP Tools   │                       │ │
│  │  │(Provider Mode)│  │  (AI Tools)  │                       │ │
│  │  └──────────────┘  └──────────────┘                       │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 模块组织

```
mybatis-boost/src/
├── extension.ts              # 扩展入口点
│
├── navigator/                # 导航系统（核心功能）
│   ├── core/
│   │   └── FileMapper.ts    # 文件映射 + LRU 缓存
│   ├── diagnostics/
│   │   └── ParameterValidator.ts  # 参数验证
│   ├── parsers/
│   │   ├── javaParser.ts
│   │   ├── javaFieldParser.ts
│   │   └── xmlParser.ts
│   └── providers/            # 8 个 Definition Providers
│       ├── JavaToXmlDefinitionProvider.ts
│       ├── XmlToJavaDefinitionProvider.ts
│       └── ... (6 more)
│
├── generator/                # 代码生成系统
│   ├── parser/
│   │   ├── ddlParser.ts      # DDL 解析
│   │   └── libraryParser.ts  # 库文件解析
│   ├── template/
│   │   └── templateGenerator.ts  # EJS 模板生成
│   └── GeneratorService.ts   # 生成服务
│
├── console/                  # SQL 控制台拦截
│   ├── interceptor/
│   │   └── ConsoleInterceptor.ts
│   ├── parser/
│   │   ├── LogParser.ts
│   │   └── ParameterParser.ts
│   └── converter/
│       └── SqlConverter.ts
│
├── formatter/                # 格式化器
│   └── MybatisSqlFormatter.ts  # CST 解析实现
│
├── mcp/                      # MCP 集成
│   ├── MCPManager.ts         # MCP 管理器
│   ├── core/                 # MCP 核心服务
│   └── tools/                # MCP 工具
│
├── decorator/                # 装饰器
│   ├── MybatisBindingDecorator.ts
│   └── DynamicSqlHighlighter.ts
│
├── hover/                    # 悬停提示
├── webview/                  # WebView 面板
├── test/                     # 测试文件
└── utils/                    # 工具函数
```

---

## 核心模块详解

### 1. 导航系统 (Navigator)

**职责**: 提供 Java ↔ XML Mapper 的双向导航

```
┌─────────────────────────────────────────────────────────┐
│              导航系统架构                                │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  User Action (Ctrl+Click)                               │
│     ↓                                                   │
│  ┌───────────────────────────────────────────────┐     │
│  │         DefinitionProvider (8个)              │     │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐      │     │
│  │  │ Java →  │  │  XML →  │  │  XML →  │      │     │
│  │  │  XML    │  │  Java   │  │ Fragment│      │     │
│  │  └─────────┘  └─────────┘  └─────────┘      │     │
│  └───────────────────────────────────────────────┘     │
│     ↓                                                   │
│  ┌───────────────────────────────────────────────┐     │
│  │         FileMapper (LRU Cache)                │     │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐      │     │
│  │  │ Parse   │  │  Map    │  │  Cache  │      │     │
│  │  │ Files   │  │ Files   │  │ Results │      │     │
│  │  └─────────┘  └─────────┘  └─────────┘      │     │
│  └───────────────────────────────────────────────┘     │
│     ↓                                                   │
│  Location (VS Code URI)                                  │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**10 种导航模式**：

| 模式 | 源 | 目标 | Provider |
|------|-----|------|----------|
| 1 | Java interface | XML mapper | JavaToXmlDefinitionProvider |
| 2 | Java method | XML statement | JavaToXmlDefinitionProvider |
| 3 | XML namespace | Java interface | XmlToJavaDefinitionProvider |
| 4 | XML statement | Java method | XmlToJavaDefinitionProvider |
| 5 | XML include | SQL fragment | XmlSqlFragmentDefinitionProvider |
| 6 | XML class | Java class | JavaClassDefinitionProvider |
| 7 | XML result | Java field | XmlResultMapPropertyDefinitionProvider |
| 8 | XML resultMap | resultMap definition | XmlResultMapDefinitionProvider |
| 9 | XML param | Java field | XmlParameterDefinitionProvider |
| 10 | 实时验证 | 参数检查 | ParameterValidator |

### 2. FileMapper 核心

**src/navigator/core/FileMapper.ts** (简化版):

```typescript
import * as vscode from 'vscode';
import { LRUCache } from 'lru-cache';

/**
 * 文件映射器 - 导航系统的核心
 * 负责 Java ↔ XML 文件的映射和缓存
 */
export class FileMapper {
  // LRU 缓存存储映射结果
  private cache = new LRUCache<string, MappingResult>({
    max: 5000,  // 默认缓存 5000 条
    ttl: 1000 * 60 * 30,  // 30 分钟过期
  });

  // 文件监听器，用于失效缓存
  private fileWatcher: vscode.FileSystemWatcher;

  constructor() {
    // 监听文件变化，失效相关缓存
    this.fileWatcher = vscode.workspace.createFileSystemWatcher(
      '**/*.{java,xml}'
    );

    this.fileWatcher.onDidChange(uri => this.invalidate(uri));
    this.fileWatcher.onDidDelete(uri => this.invalidate(uri));
    this.fileWatcher.onDidCreate(uri => this.invalidate(uri));
  }

  /**
   * 查找 Java 对应的 XML 文件
   */
  async findXmlForJava(javaFile: string): Promise<XmlMapping[]> {
    const cacheKey = `java->xml:${javaFile}`;

    // 检查缓存
    const cached = this.cache.get(cacheKey);
    if (cached && this.isCacheValid(cached)) {
      return cached.mappings;
    }

    // 解析 XML 文件
    const mappings = await this.parseXmlMappings(javaFile);

    // 缓存结果
    this.cache.set(cacheKey, {
      mappings,
      timestamp: Date.now()
    });

    return mappings;
  }

  /**
   * 查找 XML 对应的 Java 文件
   */
  async findJavaForXml(xmlFile: string): Promise<JavaMapping[]> {
    const cacheKey = `xml->java:${xmlFile}`;

    // 检查缓存
    const cached = this.cache.get(cacheKey);
    if (cached && this.isCacheValid(cached)) {
      return cached.mappings;
    }

    // 解析 Java 文件
    const mappings = await this.parseJavaMappings(xmlFile);

    // 缓存结果
    this.cache.set(cacheKey, {
      mappings,
      timestamp: Date.now()
    });

    return mappings;
  }

  /**
   * 使用优先级策略查找 XML
   */
  private async parseXmlMappings(javaFile: string): Promise<XmlMapping[]> {
    // 策略 1: 快速路径 - 同目录同名 XML
    const quickPath = this.getQuickPath(javaFile);
    if (quickPath && await this.fileExists(quickPath)) {
      return [this.parseXmlFile(quickPath)];
    }

    // 策略 2: 配置的自定义目录
    const customPaths = this.getCustomPaths();
    for (const path of customPaths) {
      const xmlPath = path.join(path, this.getXmlName(javaFile));
      if (await this.fileExists(xmlPath)) {
        return [this.parseXmlFile(xmlPath)];
      }
    }

    // 策略 3: 工作区搜索
    return await this.searchWorkspace(javaFile);
  }

  /**
   * 失效缓存
   */
  private invalidate(uri: vscode.Uri): void {
    const filePath = uri.fsPath;

    // 失效相关的缓存条目
    for (const key of this.cache.keys()) {
      if (key.includes(filePath)) {
        this.cache.delete(key);
      }
    }
  }

  /**
   * 检查缓存是否有效
   */
  private isCacheValid(cached: CachedResult): boolean {
    // 检查文件是否仍然存在且未修改
    const stats = fs.statSync(cached.mappings[0].file);
    return stats.mtimeMs <= cached.timestamp;
  }

  /**
   * 清理资源
   */
  dispose(): void {
    this.fileWatcher.dispose();
    this.cache.clear();
  }
}
```

**关键设计决策**：

1. **LRU 缓存**: 使用 `lru-cache` 库，自动管理缓存大小和过期
2. **文件监听**: 监听文件变化，自动失效相关缓存
3. **优先级策略**: 快速路径 → 自定义路径 → 工作区搜索
4. **时间戳验证**: 检查文件修改时间，确保缓存有效性

### 3. 生成器系统 (Generator)

**职责**: 从 DDL 或库文件生成 MyBatis 代码

```
┌─────────────────────────────────────────────────────────┐
│              代码生成流程                                │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Input (DDL / Library)                                  │
│     ↓                                                   │
│  ┌───────────────────────────────────────────────┐     │
│  │            Parser                              │     │
│  │  ┌─────────────┐  ┌─────────────┐            │     │
│  │  │  DDL Parser │  │Library Parser│           │     │
│  │  │(MySQL/PG/   │  │  (existing  │           │     │
│  │  │ Oracle)     │  │   files)    │           │     │
│  │  └─────────────┘  └─────────────┘            │     │
│  └───────────────────────────────────────────────┘     │
│     ↓                                                   │
│  Schema (JSON representation)                            │
│     ↓                                                   │
│  ┌───────────────────────────────────────────────┐     │
│  │         EJS Template Engine                    │     │
│  │  ┌─────────────┐  ┌─────────────┐            │     │
│  │  │ Mapper.ejs  │  │ Model.ejs   │            │     │
│  │  │ Service.ejs │  │Controller   │            │     │
│  │  └─────────────┘  └─────────────┘            │     │
│  └───────────────────────────────────────────────┘     │
│     ↓                                                   │
│  Generated Code                                         │
│     ↓                                                   │
│  ┌───────────────────────────────────────────────┐     │
│  │           Preview & Export                      │     │
│  │  • WebView Preview                             │     │
│  │  • File Generation                             │     │
│  │  • History Recording                           │     │
│  └───────────────────────────────────────────────┘     │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 4. MCP 集成

**职责**: 支持 AI IDE (Cursor/Copilot) 的代码生成

```
┌─────────────────────────────────────────────────────────┐
│              MCP 集成架构                                │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  AI IDE                                                 │
│  ┌──────────────┐  ┌──────────────┐                   │
│  │  Cursor IDE  │  │VS Code +     │                   │
│  │  + MCP       │  │Copilot + MCP │                   │
│  └──────┬───────┘  └──────┬───────┘                   │
│         │                  │                           │
│         └──────────┬───────┘                           │
│                    ↓                                   │
│  ┌───────────────────────────────────────────────┐    │
│  │         MCP Manager (Provider Mode)           │    │
│  │  ┌─────────────┐  ┌─────────────┐            │    │
│  │  │Cursor Provider│ │Copilot     │            │    │
│  │  │             │  │Provider    │            │    │
│  │  └─────────────┘  └─────────────┘            │    │
│  └───────────────────────────────────────────────┘    │
│                    ↓                                   │
│  ┌───────────────────────────────────────────────┐    │
│  │            MCP Tools                          │    │
│  │  ┌─────────────────────────────────────┐     │    │
│  │  │ parseSqlAndGenerate                  │     │    │
│  │  │ exportGeneratedFiles                 │     │    │
│  │  │ queryGenerationHistory               │     │    │
│  │  │ parseAndExport                       │     │    │
│  │  └─────────────────────────────────────┘     │    │
│  └───────────────────────────────────────────────┘    │
│                    ↓                                   │
│  Generator Service → Generated Code                   │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 配置系统

### 配置层次

```
┌─────────────────────────────────────────────────────────┐
│              配置优先级                                  │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  1. 项目配置 (.vscode/settings.json)                    │
│     ────────────────────────────────────                │
│     最高优先级，项目特定设置                             │
│                                                         │
│  2. 用户配置 (VS Code Settings)                         │
│     ────────────────────────────────                   │
│     用户全局设置                                         │
│                                                         │
│  3. 默认配置 (package.json)                             │
│     ────────────────────────────────                   │
│     扩展默认值                                           │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 关键配置项

```json
{
  // 导航配置
  "mybatis-boost.cacheSize": 5000,
  "mybatis-boost.customXmlDirectories": [],
  "mybatis-boost.showBindingIcons": true,

  // 生成器配置
  "mybatis-boost.generator.mapperPackage": "com.example.mapper",
  "mybatis-boost.generator.modelPackage": "com.example.model",
  "mybatis-boost.generator.servicePackage": "com.example.service",
  "mybatis-boost.generator.useLombok": true,
  "mybatis-boost.generator.useService": true,
  "mybatis-boost.generator.useController": true,

  // SQL 控制台配置
  "mybatis-boost.console.enabled": true,
  "mybatis-boost.console.autoDetectDatabase": true,
  "mybatis-boost.console.historyLimit": 5000,

  // 格式化器配置
  "mybatis-boost.formatter.enabled": true,
  "mybatis-boost.formatter.language": "auto",
  "mybatis-boost.formatter.keywordCase": "upper",
  "mybatis-boost.formatter.tabWidth": 4
}
```

---

## 性能优化策略

### 1. LRU 缓存

```typescript
// 默认配置
const cache = new LRUCache<string, T>({
  max: 5000,              // 最多缓存 5000 条
  ttl: 1000 * 60 * 30,    // 30 分钟过期
  updateAgeOnGet: true,   // 获取时更新时间
  updateAgeOnHas: true,   // 检查时更新时间
});

// 可配置
const userSize = vscode.workspace.getConfiguration('mybatis-boost')
  .get<number>('cacheSize', 5000);

const cache = new LRUCache({ max: userSize });
```

### 2. 优先级策略

```typescript
/**
 * 文件查找优先级策略
 */
async function findXmlFile(javaFile: string): Promise<string | null> {
  // 策略 1: 快速路径 (O(1))
  const quickPath = getQuickPath(javaFile);
  if (await fileExists(quickPath)) {
    return quickPath;
  }

  // 策略 2: 配置路径 (O(n), n 通常 < 5)
  const customPaths = getCustomPaths();
  for (const path of customPaths) {
    const xmlPath = join(path, getXmlName(javaFile));
    if (await fileExists(xmlPath)) {
      return xmlPath;
    }
  }

  // 策略 3: 工作区搜索 (O(m), m = 文件数量)
  return await searchWorkspace(javaFile);
}
```

### 3. 延迟解析

```typescript
/**
 * 按需解析，不预加载所有文件
 */
class LazyFileParser {
  private parsedFiles = new Map<string, ParsedFile>();

  async parse(file: string): Promise<ParsedFile> {
    // 检查是否已解析
    if (this.parsedFiles.has(file)) {
      return this.parsedFiles.get(file)!;
    }

    // 按需解析
    const parsed = await this.doParse(file);
    this.parsedFiles.set(file, parsed);

    return parsed;
  }
}
```

### 4. 增量更新

```typescript
/**
 * 只更新变化的文件，不重建整个索引
 */
class IncrementalIndexer {
  private index: Map<string, FileIndex>;

  constructor() {
    this.index = new Map();

    // 监听文件变化
    const watcher = vscode.workspace.createFileSystemWatcher('**/*.{java,xml}');

    watcher.onDidChange(uri => {
      this.updateIndex(uri.fsPath);  // 只更新变化文件
    });

    watcher.onDidDelete(uri => {
      this.removeFromIndex(uri.fsPath);  // 只删除相关条目
    });

    watcher.onDidCreate(uri => {
      this.addToIndex(uri.fsPath);  // 只添加新文件
    });
  }
}
```

### 性能目标

```
┌─────────────────────────────────────────────────────────┐
│              性能目标                                    │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  导航响应时间：                                          │
│  • P50 < 100ms  (50% 请求)                              │
│  • P95 < 200ms  (95% 请求)                              │
│  • P99 < 500ms  (99% 请求)                              │
│                                                         │
│  内存占用：                                              │
│  • 基础: ~50 MB                                         │
│  • 缓存 5000 条: ~100 MB                                │
│  • 缓存 10000 条: ~150 MB                               │
│                                                         │
│  启动时间：                                              │
│  • 激活: < 100ms                                        │
│  • 首次导航: < 200ms                                     │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 测试策略

### 测试组织

```
src/test/
├── unit/                    # 单元测试 (106+)
│   ├── FileMapper.test.ts
│   ├── GeneratorViewProvider.test.ts
│   └── console/
│       ├── LogParser.test.ts
│       ├── ParameterParser.test.ts
│       └── ...
├── integration/             # 集成测试 (15+)
│   └── ...
└── fixtures/                # 测试夹具
    ├── java/
    │   └── SimpleMapper.java
    └── xml/
        └── SimpleMapper.xml
```

### 测试覆盖

```
┌─────────────────────────────────────────────────────────┐
│              测试覆盖范围                                │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  核心功能：                                             │
│  ✓ FileMapper 缓存逻辑                                  │
│  ✓ Java/XML 解析器                                     │
│  ✓ Definition Providers (8个)                          │
│  ✓ DDL 解析器 (MySQL, PostgreSQL, Oracle)              │
│  ✓ 日志解析器                                           │
│  ✓ 参数解析器                                           │
│  ✓ SQL 转换器                                           │
│  ✓ MCP 工具                                             │
│                                                         │
│  测试类型：                                             │
│  ✓ 单元测试 - 隔离测试单个函数                         │
│  ✓ 集成测试 - 测试模块交互                              │
│  ✓ 夹具测试 - 使用真实示例文件                          │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 总结

### 关键要点

1. **项目规模**
   - 24,123 行 TypeScript 代码
   - 99 个源文件
   - 106+ 单元测试通过

2. **架构设计**
   - 分层架构：扩展层 → 服务层 → 解析层 → 工具层
   - 模块化组织：导航、生成、控制台、格式化
   - 职责分离：每个模块专注单一功能

3. **核心功能**
   - 10 种双向导航模式
   - AI 代码生成（MCP 支持）
   - SQL 日志拦截
   - CST 格式化
   - 实时参数验证

4. **性能优化**
   - LRU 缓存（可配置 5000+）
   - 优先级策略（快速路径优先）
   - 延迟解析（按需加载）
   - 增量更新（文件监听）

### 下一步

在下一章中，我们将深入学习 **MyBatis XML 格式化器**：
- 为什么使用 CST 而不是正则表达式
- CST 解析器的实现
- 处理动态 SQL 标签
- 多方言 SQL 支持

---

## 进一步阅读

### 项目文件
- `C:\PythonProject\mybatis-boost\CLAUDE.md`
- `C:\PythonProject\mybatis-boost\src\extension.ts`
- `C:\PythonProject\mybatis-boost\src\navigator\core\FileMapper.ts`

### 相关章节
- [Chapter 15 - CST vs Regex](chapter-15-cst-vs-regex.md) - 下一章
- [Chapter 16 - Provider 模式](chapter-16-provider-pattern.md)

---

## 练习

完成以下练习：

1. **探索练习**
   - [ ] 克隆或访问 mybatis-boost 项目
   - [ ] 阅读 package.json 和 CLAUDE.md
   - [ ] 运行扩展并测试导航功能

2. **代码练习**
   - [ ] 阅读一个 Definition Provider 实现
   - [ ] 理解 FileMapper 的缓存逻辑
   - [ ] 查看一个 MCP 工具的实现

3. **架构练习**
   - [ ] 绘制项目的模块依赖图
   - [ ] 分析配置系统的层次结构
   - [ ] 理解性能优化策略

---

**上一章**: [Chapter 13 - 自定义 Commands](../module-03-advanced-features/chapter-13-commands.md)
**下一章**: [Chapter 15 - CST vs Regex](chapter-15-cst-vs-regex.md)
