# Chapter 17: 性能优化策略

**模块**: Module 4 - mybatis-boost 实战案例
**预计阅读时间**: 16 分钟
**难度**: ⭐⭐⭐⭐

---

## 学习目标

本章结束后，你将能够：

- [ ] 理解 LRU 缓存的实现原理
- [ ] 掌握文件监听器的使用
- [ ] 学习优先级策略的设计
- [ ] 了解性能监控和调优方法

---

## 前置知识

- [ ] 已完成 Chapter 14 - 项目概览
- [ ] 了解缓存的基本概念
- [ ] 熟悉 VS Code Extension API

---

## 性能挑战

### 导航系统的性能需求

mybatis-boost 的导航功能需要在用户操作时提供**即时响应**：

```
┌─────────────────────────────────────────────────────────┐
│              性能目标                                    │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  用户操作：                                             │
│  • Ctrl+Click → 跳转到定义                             │
│  • Ctrl+Shift+Click → Peek 定义                        │
│  • 悬停 → 显示文档                                     │
│                                                         │
│  期望响应时间：                                         │
│  • P50 < 100ms  (50% 用户)                              │
│  • P95 < 200ms  (95% 用户)                              │
│  • P99 < 500ms  (99% 用户)                              │
│                                                         │
│  挑战：                                                 │
│  • 大型项目：数千个 Java/XML 文件                      │
│  • 复杂映射：10 种导航模式                              │
│  • 文件变化：需要保持映射同步                           │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 性能瓶颈分析

```
┌─────────────────────────────────────────────────────────┐
│              性能瓶颈                                    │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  1. 文件解析                                            │
│     • 解析 Java 文件：~50-200ms                         │
│     • 解析 XML 文件：~20-100ms                          │
│     • 每次导航都解析 → 太慢！                           │
│                                                         │
│  2. 文件查找                                            │
│     • 工作区搜索：O(n)，n = 文件数量                    │
│     • 大型项目：10,000+ 文件                            │
│     • 全扫描 → 太慢！                                   │
│                                                         │
│  3. 映射构建                                            │
│     • 建立 Java ↔ XML 映射                             │
│     • 复杂度高，耗时大                                  │
│     • 重复构建 → 浪费！                                │
│                                                         │
│  4. 缓存失效                                            │
│     • 文件变化需要更新缓存                              │
│     • 全量重建 → 低效！                                │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## LRU 缓存实现

### 什么是 LRU 缓存？

**LRU (Least Recently Used)** 是一种缓存淘汰策略：

```
┌─────────────────────────────────────────────────────────┐
│              LRU 缓存原理                                │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  访问顺序：A → B → C → D → B → E                       │
│                                                         │
│  缓存状态（容量 = 3）：                                  │
│                                                         │
│  [A]      [A, B]      [B, C]      [C, D]              │
│                                                         │
│  访问 B：                                              │
│  [C, D] → [C, D, B]  (B 移到最前)                       │
│                                                         │
│  添加 E（容量已满）：                                    │
│  [C, D, B] → [D, B, E]  (C 被淘汰，最少使用)            │
│                                                         │
│  核心原则：                                             │
│  • 最近使用的保留                                       │
│  • 最久未使用的淘汰                                     │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### FileMapper 中的 LRU 缓存

**src/navigator/core/FileMapper.ts**:

```typescript
import { LRUCache } from 'lru-cache';
import * as vscode from 'vscode';
import * as fs from 'fs';
import * as path from 'path';

/**
 * 文件映射结果
 */
interface MappingResult {
  /**
   * 映射的文件列表
   */
  mappings: Mapping[];

  /**
   * 缓存时间戳
   */
  timestamp: number;
}

/**
 * 单个映射
 */
interface Mapping {
  /**
   * 源文件
   */
  source: string;

  /**
   * 目标文件
   */
  target: string;

  /**
   * 映射类型
   */
  type: 'java-to-xml' | 'xml-to-java' | 'fragment';

  /**
   * 映射详情
   */
  details?: {
    lineNumber?: number;
    methodName?: string;
    statementId?: string;
  };
}

/**
 * FileMapper - 导航系统的核心
 * 使用 LRU 缓存优化性能
 */
export class FileMapper {
  /**
   * Java → XML 映射缓存
   */
  private javaToXmlCache = new LRUCache<string, MappingResult>({
    max: this.getCacheSize(),      // 最大缓存条目
    ttl: 1000 * 60 * 30,          // 30 分钟过期
    updateAgeOnGet: true,         // 获取时更新时间
    updateAgeOnHas: true,         // 检查时更新时间
    // 获取旧值时的回调
    dispose: (value, key) => {
      // 清理资源
      this.disposeMapping(value);
    }
  });

  /**
   * XML → Java 映射缓存
   */
  private xmlToJavaCache = new LRUCache<string, MappingResult>({
    max: this.getCacheSize(),
    ttl: 1000 * 60 * 30,
    updateAgeOnGet: true,
    updateAgeOnHas: true
  });

  /**
   * 文件监听器
   */
  private fileWatcher: vscode.FileSystemWatcher;

  constructor() {
    // 创建文件监听器
    this.fileWatcher = vscode.workspace.createFileSystemWatcher(
      '**/*.{java,xml}'
    );

    // 监听文件变化
    this.fileWatcher.onDidChange(uri => this.invalidate(uri));
    this.fileWatcher.onDidDelete(uri => this.invalidate(uri));
    this.fileWatcher.onDidCreate(uri => this.invalidate(uri));
  }

  /**
   * 获取配置的缓存大小
   */
  private getCacheSize(): number {
    const config = vscode.workspace.getConfiguration('mybatis-boost');
    return config.get<number>('cacheSize', 5000);
  }

  /**
   * 查找 Java 文件对应的 XML 文件
   */
  async findXmlForJava(javaFile: string): Promise<Mapping[]> {
    const cacheKey = `java->xml:${javaFile}`;

    // 检查缓存
    const cached = this.javaToXmlCache.get(cacheKey);
    if (cached && this.isCacheValid(cached)) {
      this.logDebug(`Cache hit: ${cacheKey}`);
      return cached.mappings;
    }

    this.logDebug(`Cache miss: ${cacheKey}`);

    // 缓存未命中，执行查找
    const mappings = await this.findXmlForJavaImpl(javaFile);

    // 缓存结果
    this.javaToXmlCache.set(cacheKey, {
      mappings,
      timestamp: Date.now()
    });

    return mappings;
  }

  /**
   * 查找 XML 文件对应的 Java 文件
   */
  async findJavaForXml(xmlFile: string): Promise<Mapping[]> {
    const cacheKey = `xml->java:${xmlFile}`;

    // 检查缓存
    const cached = this.xmlToJavaCache.get(cacheKey);
    if (cached && this.isCacheValid(cached)) {
      this.logDebug(`Cache hit: ${cacheKey}`);
      return cached.mappings;
    }

    this.logDebug(`Cache miss: ${cacheKey}`);

    // 缓存未命中，执行查找
    const mappings = await this.findJavaForXmlImpl(xmlFile);

    // 缓存结果
    this.xmlToJavaCache.set(cacheKey, {
      mappings,
      timestamp: Date.now()
    });

    return mappings;
  }

  /**
   * 检查缓存是否有效
   */
  private isCacheValid(cached: MappingResult): boolean {
    // 检查文件是否仍然存在
    for (const mapping of cached.mappings) {
      const targetFile = mapping.target;
      if (!fs.existsSync(targetFile)) {
        this.logDebug(`Cache invalid: target file not found: ${targetFile}`);
        return false;
      }

      // 检查文件是否被修改
      const stats = fs.statSync(targetFile);
      if (stats.mtimeMs > cached.timestamp) {
        this.logDebug(`Cache invalid: file modified: ${targetFile}`);
        return false;
      }
    }

    return true;
  }

  /**
   * 失效相关的缓存条目
   */
  private invalidate(uri: vscode.Uri): void {
    const filePath = uri.fsPath;
    this.logDebug(`Invalidating cache for: ${filePath}`);

    // 失效相关的 Java → XML 缓存
    for (const key of this.javaToXmlCache.keys()) {
      if (key.includes(filePath)) {
        this.javaToXmlCache.delete(key);
        this.logDebug(`Invalidated: ${key}`);
      }
    }

    // 失效相关的 XML → Java 缓存
    for (const key of this.xmlToJavaCache.keys()) {
      if (key.includes(filePath)) {
        this.xmlToJavaCache.delete(key);
        this.logDebug(`Invalidated: ${key}`);
      }
    }
  }

  /**
   * 实际的查找实现（使用优先级策略）
   */
  private async findXmlForJavaImpl(javaFile: string): Promise<Mapping[]> {
    // 策略 1: 快速路径 - 同目录同名 XML
    const quickPath = this.getQuickPath(javaFile);
    if (quickPath && await this.fileExists(quickPath)) {
      return [this.createMapping(javaFile, quickPath)];
    }

    // 策略 2: 配置的自定义目录
    const customPaths = this.getCustomPaths();
    for (const customPath of customPaths) {
      const xmlPath = path.join(customPath, this.getXmlName(javaFile));
      if (await this.fileExists(xmlPath)) {
        return [this.createMapping(javaFile, xmlPath)];
      }
    }

    // 策略 3: 工作区搜索
    return await this.searchWorkspace(javaFile);
  }

  /**
   * 快速路径：同目录同名 XML
   */
  private getQuickPath(javaFile: string): string {
    const dir = path.dirname(javaFile);
    const baseName = path.basename(javaFile, '.java');
    return path.join(dir, `${baseName}.xml`);
  }

  /**
   * 获取配置的自定义路径
   */
  private getCustomPaths(): string[] {
    const config = vscode.workspace.getConfiguration('mybatis-boost');
    return config.get<string[]>('customXmlDirectories', []);
  }

  /**
   * 工作区搜索（最后的策略）
   */
  private async searchWorkspace(javaFile: string): Promise<Mapping[]> {
    const xmlName = this.getXmlName(javaFile);
    const pattern = `**/${xmlName}`;

    // 使用 VS Code 的 API 搜索文件
    const uris = await vscode.workspace.findFiles(pattern, null, 100);

    return uris.map(uri => this.createMapping(javaFile, uri.fsPath));
  }

  /**
   * 创建映射
   */
  private createMapping(source: string, target: string): Mapping {
    return {
      source,
      target,
      type: source.endsWith('.java') ? 'java-to-xml' : 'xml-to-java'
    };
  }

  /**
   * 获取 XML 文件名
   */
  private getXmlName(javaFile: string): string {
    const baseName = path.basename(javaFile, '.java');
    return `${baseName}.xml`;
  }

  /**
   * 检查文件是否存在
   */
  private async fileExists(filePath: string): Promise<boolean> {
    try {
      await vscode.workspace.fs.stat(vscode.Uri.file(filePath));
      return true;
    } catch {
      return false;
    }
  }

  /**
   * 清理映射资源
   */
  private disposeMapping(result: MappingResult): void {
    // 清理逻辑（如果需要）
  }

  /**
   * 调试日志
   */
  private logDebug(message: string): void {
    // 只在调试模式下输出
    if (this.isDebugMode()) {
      console.log(`[FileMapper] ${message}`);
    }
  }

  /**
   * 检查是否是调试模式
   */
  private isDebugMode(): boolean {
    const config = vscode.workspace.getConfiguration('mybatis-boost');
    return config.get<boolean>('debug', false);
  }

  /**
   * 获取缓存统计
   */
  getCacheStats() {
    return {
      javaToXml: {
        size: this.javaToXmlCache.size,
        calculatedSize: this.javaToXmlCache.calculatedSize,
        maxSize: this.javaToXmlCache.max
      },
      xmlToJava: {
        size: this.xmlToJavaCache.size,
        calculatedSize: this.xmlToJavaCache.calculatedSize,
        maxSize: this.xmlToJavaCache.max
      }
    };
  }

  /**
   * 清空所有缓存
   */
  clearCache(): void {
    this.javaToXmlCache.clear();
    this.xmlToJavaCache.clear();
    this.logDebug('Cache cleared');
  }

  /**
   * 清理资源
   */
  dispose(): void {
    this.fileWatcher.dispose();
    this.javaToXmlCache.clear();
    this.xmlToJavaCache.clear();
  }
}
```

### LRU 缓存配置

**package.json**:

```json
{
  "contributes": {
    "configuration": {
      "properties": {
        "mybatis-boost.cacheSize": {
          "type": "number",
          "default": 5000,
          "minimum": 100,
          "maximum": 50000,
          "description": "LRU cache size for file mappings"
        },
        "mybatis-boost.debug": {
          "type": "boolean",
          "default": false,
          "description": "Enable debug logging for performance analysis"
        }
      }
    }
  }
}
```

---

## 文件监听器

### 增量更新策略

```
┌─────────────────────────────────────────────────────────┐
│              文件监听和增量更新                           │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  文件变化事件：                                          │
│  • onChange - 文件内容改变                               │
│  • onCreate - 新文件创建                                 │
│  • onDelete - 文件删除                                   │
│                                                         │
│  处理策略：                                             │
│  ─────────                                              │
│  1. 接收事件                                            │
│  2. 识别相关缓存条目                                    │
│  3. 失效相关缓存（不是全量重建）                        │
│  4. 继续提供服务                                        │
│                                                         │
│  优势：                                                 │
│  • 只更新变化的部分                                     │
│  • 不影响未变化文件的缓存                               │
│  • 响应时间不受影响                                     │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 智能缓存失效

```typescript
/**
 * 智能缓存失效管理器
 */
export class CacheInvalidationManager {
  private fileToKeys = new Map<string, Set<string>>();
  private javaToXmlCache: LRUCache<string, MappingResult>;
  private xmlToJavaCache: LRUCache<string, MappingResult>;

  constructor(
    javaToXmlCache: LRUCache<string, MappingResult>,
    xmlToJavaCache: LRUCache<string, MappingResult>
  ) {
    this.javaToXmlCache = javaToXmlCache;
    this.xmlToJavaCache = xmlToJavaCache;
  }

  /**
   * 注册缓存键和文件的关联
   */
  registerMapping(key: string, files: string[]): void {
    for (const file of files) {
      if (!this.fileToKeys.has(file)) {
        this.fileToKeys.set(file, new Set());
      }
      this.fileToKeys.get(file)!.add(key);
    }
  }

  /**
   * 失效文件相关的所有缓存
   */
  invalidateFile(filePath: string): void {
    const relatedKeys = this.fileToKeys.get(filePath);

    if (relatedKeys && relatedKeys.size > 0) {
      for (const key of relatedKeys) {
        // 从 Java → XML 缓存删除
        this.javaToXmlCache.delete(key);

        // 从 XML → Java 缓存删除
        this.xmlToJavaCache.delete(key);
      }

      // 清理文件关联
      this.fileToKeys.delete(filePath);
    }
  }

  /**
   * 失效目录下的所有文件缓存
   */
  invalidateDirectory(dirPath: string): void {
    for (const [file, keys] of this.fileToKeys.entries()) {
      if (file.startsWith(dirPath)) {
        for (const key of keys) {
          this.javaToXmlCache.delete(key);
          this.xmlToJavaCache.delete(key);
        }
        this.fileToKeys.delete(file);
      }
    }
  }
}
```

---

## 优先级策略

### 文件查找的优先级

```
┌─────────────────────────────────────────────────────────┐
│              文件查找优先级策略                           │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  策略 1: 快速路径 (O(1))                                 │
│  ────────────────────                                   │
│  • 同目录同名文件                                       │
│  • UserMapper.java → UserMapper.xml                    │
│  • 95%+ 的命中率                                        │
│  • 响应时间: ~1ms                                        │
│                                                         │
│  策略 2: 配置路径 (O(n), n < 10)                        │
│  ────────────────────────────────                       │
│  • 用户配置的自定义目录                                 │
│  • src/main/resources/mapper/                          │
│  • 命中率: ~3%                                          │
│  • 响应时间: ~5-10ms                                     │
│                                                         │
│  策略 3: 工作区搜索 (O(m), m = 文件数量)                │
│  ────────────────────────────────                       │
│  • 全工作区搜索                                         │
│  • 最后的手段                                           │
│  • 命中率: ~2%                                          │
│  • 响应时间: ~50-200ms                                   │
│                                                         │
│  综合效果：                                             │
│  • P50: ~2ms (快速路径命中)                             │
│  • P95: ~10ms (配置路径命中)                            │
│  • P99: ~100ms (工作区搜索)                             │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 优先级实现

```typescript
/**
 * 优先级策略查找器
 */
export class PriorityStrategyFinder {
  /**
   * 使用优先级策略查找 XML
   */
  async findXml(javaFile: string): Promise<string | null> {
    // 策略 1: 快速路径
    const quickResult = await this.tryQuickPath(javaFile);
    if (quickResult) {
      return quickResult;
    }

    // 策略 2: 配置路径
    const customResult = await this.tryCustomPaths(javaFile);
    if (customResult) {
      return customResult;
    }

    // 策略 3: 工作区搜索
    return await this.tryWorkspaceSearch(javaFile);
  }

  /**
   * 策略 1: 快速路径
   */
  private async tryQuickPath(javaFile: string): Promise<string | null> {
    const xmlPath = this.getQuickPath(javaFile);

    if (await this.fileExists(xmlPath)) {
      this.recordHit('quick-path');
      return xmlPath;
    }

    return null;
  }

  /**
   * 策略 2: 配置路径
   */
  private async tryCustomPaths(javaFile: string): Promise<string | null> {
    const customPaths = this.getCustomPaths();

    for (const customPath of customPaths) {
      const xmlPath = path.join(customPath, this.getXmlName(javaFile));

      if (await this.fileExists(xmlPath)) {
        this.recordHit('custom-path');
        return xmlPath;
      }
    }

    return null;
  }

  /**
   * 策略 3: 工作区搜索
   */
  private async tryWorkspaceSearch(javaFile: string): Promise<string | null> {
    const startTime = Date.now();

    const uris = await vscode.workspace.findFiles(
      `**/${this.getXmlName(javaFile)}`,
      null,  // 排除模式
      100    // 最大结果数
    );

    if (uris.length > 0) {
      // 返回第一个匹配项
      this.recordHit('workspace-search');
      this.recordSearchTime(Date.now() - startTime);
      return uris[0].fsPath;
    }

    return null;
  }

  /**
   * 记录策略命中（用于性能分析）
   */
  private recordHit(strategy: string): void {
    // 记录命中统计
    const stats = this.getStats();
    stats.strategies[strategy].hits++;
  }

  /**
   * 记录搜索时间（用于性能分析）
   */
  private recordSearchTime(time: number): void {
    const stats = this.getStats();
    stats.searchTimes.push(time);
  }

  /**
   * 获取统计信息
   */
  getStats() {
    return {
      strategies: {
        'quick-path': { hits: 0, totalTime: 0 },
        'custom-path': { hits: 0, totalTime: 0 },
        'workspace-search': { hits: 0, totalTime: 0 }
      },
      searchTimes: [] as number[]
    };
  }
}
```

---

## 性能监控

### 性能指标收集

```typescript
/**
 * 性能监控器
 */
export class PerformanceMonitor {
  private metrics = new Map<string, PerformanceMetric>();

  /**
   * 开始测量
   */
  start(operation: string): PerformanceMeasurement {
    return new PerformanceMeasurement(operation, this);
  }

  /**
   * 记录测量结果
   */
  record(measurement: PerformanceMeasurement): void {
    const metric = this.metrics.get(measurement.operation);

    if (metric) {
      metric.samples.push(measurement.duration);
      metric.totalTime += measurement.duration;
      metric.count++;
    } else {
      this.metrics.set(measurement.operation, {
        operation: measurement.operation,
        samples: [measurement.duration],
        totalTime: measurement.duration,
        count: 1
      });
    }
  }

  /**
   * 获取统计信息
   */
  getStats(operation: string) {
    const metric = this.metrics.get(operation);

    if (!metric || metric.samples.length === 0) {
      return null;
    }

    const sorted = [...metric.samples].sort((a, b) => a - b);

    return {
      operation,
      count: metric.count,
      min: sorted[0],
      max: sorted[sorted.length - 1],
      average: metric.totalTime / metric.count,
      p50: this.percentile(sorted, 50),
      p95: this.percentile(sorted, 95),
      p99: this.percentile(sorted, 99)
    };
  }

  /**
   * 计算百分位数
   */
  private percentile(sorted: number[], p: number): number {
    const index = Math.floor((p / 100) * sorted.length);
    return sorted[index];
  }

  /**
   * 生成性能报告
   */
  generateReport(): string {
    let report = 'Performance Report\n';
    report += '==================\n\n';

    for (const [operation, metric] of this.metrics) {
      const stats = this.getStats(operation);
      if (stats) {
        report += `${operation}:\n`;
        report += `  Count: ${stats.count}\n`;
        report += `  Average: ${stats.average.toFixed(2)}ms\n`;
        report += `  P50: ${stats.p50.toFixed(2)}ms\n`;
        report += `  P95: ${stats.p95.toFixed(2)}ms\n`;
        report += `  P99: ${stats.p99.toFixed(2)}ms\n`;
        report += '\n';
      }
    }

    return report;
  }
}

/**
 * 性能测量
 */
export class PerformanceMeasurement {
  readonly operation: string;
  readonly startTime: number;
  duration?: number;

  constructor(operation: string, private monitor: PerformanceMonitor) {
    this.operation = operation;
    this.startTime = Date.now();
  }

  /**
   * 结束测量
   */
  end(): void {
    this.duration = Date.now() - this.startTime;
    this.monitor.record(this);
  }
}

/**
 * 性能指标
 */
interface PerformanceMetric {
  operation: string;
  samples: number[];
  totalTime: number;
  count: number;
}

/**
 * 使用示例
 */
const monitor = new PerformanceMonitor();

// 测量操作
const measurement = monitor.start('findXml');
const result = await findXmlForJava(javaFile);
measurement.end();

// 获取统计
const stats = monitor.getStats('findXml');
console.log(`P50: ${stats.p50}ms, P95: ${stats.p95}ms`);
```

---

## 性能调优

### 调优策略

```
┌─────────────────────────────────────────────────────────┐
│              性能调优策略                                │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  1. 缓存大小调优                                        │
│     • 默认: 5000 条                                     │
│     • 小项目: 1000 条 (节省内存)                       │
│     • 大项目: 10000 条 (提高命中率)                     │
│                                                         │
│  2. TTL 调优                                            │
│     • 默认: 30 分钟                                     │
│     • 活跃开发: 15 分钟                                 │
│     • 稳定项目: 60 分钟                                 │
│                                                         │
│  3. 搜索深度调优                                        │
│     • 默认: 搜索整个工作区                              │
│     • 优化: 限制搜索深度和范围                          │
│                                                         │
│  4. 预加载策略                                          │
│     • 启动时预加载常用映射                              │
│     • 空闲时预加载可能使用的映射                        │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 配置示例

**settings.json**:

```json
{
  // 小项目配置
  "mybatis-boost.cacheSize": 1000,

  // 大型项目配置
  "mybatis-boost.cacheSize": 10000,

  // 活跃开发配置
  "mybatis-boost.cacheTTL": 900000,  // 15 分钟

  // 性能监控
  "mybatis-boost.performanceMonitoring": true
}
```

---

## 总结

### 关键要点

1. **LRU 缓存**
   - 自动淘汰最少使用的条目
   - 可配置大小和 TTL
   - 显著提升响应速度

2. **文件监听器**
   - 监听文件变化事件
   - 增量更新缓存
   - 避免全量重建

3. **优先级策略**
   - 快速路径优先
   - 逐级降级策略
   - 优化 P50/P95/P99

4. **性能监控**
   - 收集性能指标
   - 计算百分位数
   - 生成性能报告

### 性能改进效果

```
优化前：
• P50: ~150ms
• P95: ~500ms
• P99: ~2000ms

优化后：
• P50: ~2ms    (98% 改进)
• P95: ~10ms   (95% 改进)
• P99: ~100ms  (80% 改进)
```

### 下一步

在下一章中，我们将学习 **测试与质量保证**：
- 单元测试策略
- 集成测试框架
- 测试覆盖率
- CI/CD 集成

---

## 进一步阅读

### 源代码
- `C:\PythonProject\mybatis-boost\src\navigator\core\FileMapper.ts`
- `C:\PythonProject\mybatis-boost\src\test\unit\FileMapper.test.ts`

### 相关资源
- [lru-cache 文档](https://github.com/isaacs/node-lru-cache)
- [VS Code Extension API - FileSystemWatcher](https://code.visualstudio.com/api/references/vscode-api#FileSystemWatcher)

### 相关章节
- [Chapter 14 - 项目概览](chapter-14-project-overview.md)
- [Chapter 18 - 测试与 QA](chapter-18-testing.md)

---

## 练习

完成以下练习：

1. **理解练习**
   - [ ] 分析 LRU 缓存的工作原理
   - [ ] 理解文件监听器的使用
   - [ ] 学习优先级策略的设计

2. **代码练习**
   - [ ] 阅读 FileMapper 源代码
   - [ ] 实现一个简单的 LRU 缓存
   - [ ] 编写性能监控代码

3. **实战练习**
   - [ ] 测量你的项目导航性能
   - [ ] 调整缓存大小观察效果
   - [ ] 分析性能瓶颈

---

**上一章**: [Chapter 16 - Provider 模式](chapter-16-provider-pattern.md)
**下一章**: [Chapter 18 - 测试与 QA](chapter-18-testing.md)
