# Claude Code 全面教程项目

## 项目概述

这是一个全面的 Claude Code 教程项目，用于视频脚本制作。

**项目路径**: `C:\PythonProject\cc-tutorial`
**实战案例**: `C:\PythonProject\mybatis-boost`

## 项目结构

```
cc-tutorial/
├── docs/
│   ├── tutorial/           # 教程内容（10个模块，39章）
│   ├── video-scripts/      # 视频脚本
│   ├── examples/           # 示例代码
│   └── research/           # 研究材料（已完成）
├── scripts/                # 生成脚本
└── CLAUDE.md              # 本文件
```

## 教程模块

1. **模块 1**: 入门基础 - 安装、配置、快捷键、Plan Mode
2. **模块 2**: 核心工作流 - 探索/计划/编码/提交、TDD、多实例
3. **模块 3**: 高级功能 - Plugin、MCP、Skills、Hooks、Commands
4. **模块 4**: 实战案例 - mybatis-boost 项目深度解析
5. **模块 5**: 架构与设计模式 - 整洁架构、洋葱架构、AAA 模式
6. **模块 6**: LLM 局限性 - 工作原理、失败案例、辅助 vs 自动化
7. **模块 7**: 专家建议 - Boris Power、Addy Osmani、Andrew Ng
8. **模块 8**: 构建自己的工作流
9. **模块 9**: 高级话题 - CI/CD、企业集成
10. **模块 10**: 快速参考 - 命令速查、故障排除

## 向量知识库

项目包含一个本地向量知识库，用于实时检索相似内容。

### 位置
`vector-kb-mcp/` - 向量知识库服务

### 使用方式

**1. CLI 模式**
```bash
cd vector-kb-mcp
uv run python -m src.cli add "文本内容" "来源标识"
uv run python -m src.cli search "查询关键词"
```

**2. MCP 服务器**
```bash
cd vector-kb-mcp
uv run python -m src.cli mcp
```

**3. Python 代码**
```python
from src.vector_store import VectorStore

# 使用上下文管理器确保资源释放
with VectorStore() as store:
    store.add_text("文档内容", source="文档来源")
    results = store.search("查询关键词")
    for metadata, score in results:
        print(f"相似度: {score:.4f}, 来源: {metadata.get('source')}")
```

### 知识库状态
- 文档数: 40 个
- 总块数: 1675 个
- 模型: paraphrase-multilingual-MiniLM-L12-v2 (384 维)
- 内存占用: ~850 MB

### 注意事项
- 使用上下文管理器 (`with VectorStore() as store:`) 确保资源释放
- 避免在循环中重复创建 VectorStore 实例
- GPU 内存会自动清理，但系统内存会保留模型缓存 (~350 MB)

## 核心快捷键

- `Shift+Tab`: 切换 Plan Mode（最重要！）
- `Alt+V`: 粘贴图片
- `Escape`: 中断操作
- `/clear`: 清空上下文
- `/help`: 帮助信息

## 工作建议

### 当编写教程内容时：
1. 使用 Markdown 格式
2. 包含代码示例和实际应用场景
3. 添加视频脚本部分（使用 `docs/video-scripts/episode-outline-template.md`）
4. 参考研究材料（`docs/research/`）

### 当创建示例代码时：
1. 放在 `docs/examples/` 对应目录
2. 包含详细注释
3. 提供使用说明

### 当引用专家建议时：
1. 标注来源（作者、文档）
2. 引用研究材料
3. 提供原始链接

## 关键参考文件

### 研究材料 (docs/research/)
- `00-research-summary.md` - 完整研究总结
- `01-claude-code-best-practices-anthropic-official.md` - Boris Cherny 最佳实践
- `02-plan-mode-guide-official.md` - Plan Mode 官方指南
- `03-andrew-ng-course-outline.md` - Andrew Ng 课程大纲
- `04-addy-osmani-2026-workflow.md` - Addy Osmani 2026 工作流

### mybatis-boost 实战案
- `CLAUDE.md` - CLAUDE.md 示例
- `src/formatter/MybatisSqlFormatter.ts` - CST 解析实现
- `src/mcp/MCPManager.ts` - MCP 管理器和 Provider 模式
- `package.json` - 项目配置
- `docs/` - 项目文档

## 核心原则

### Plan Mode 优先
> "始终以 Plan Mode 开始" - Boris Power (Claude Code 之父)

- 按 `Shift+Tab` 两次激活
- 多文件/多步骤任务必须使用
- 让 Claude 先规划，不要立即编码

### 人在循环中
> "AI 编码助手是倍增器，但人类工程师仍然是导演" - Addy Osmani

- 必须审查所有 AI 生成的代码
- 保持对软件产出的责任
- AI 放大专业知识，不是替代

### 小迭代原则
- 将工作分解为小的迭代块
- 避免大型、单一的输出
- 每个小迭代后测试和提交

## 文档编写指南

### 教程章节格式
每个章节应包含：
1. **学习目标** - 读者将学到什么
2. **前置知识** - 需要先了解什么
3. **核心概念** - 详细解释
4. **实战示例** - 代码和演示
5. **常见陷阱** - 需要避免什么
6. **进一步阅读** - 相关资源
7. **视频脚本** - 适合视频制作的部分

### 视频脚本格式
使用 `docs/video-scripts/episode-outline-template.md` 模板：
- 引入（30-60秒）
- 概念讲解（2-3分钟）
- 实战演示（5-8分钟）
- 总结（1-2分钟）
- 练习（可选）

## 代码风格

- 使用清晰的变量命名
- 添加详细的注释
- 提供使用示例
- 说明为什么这样写

## 测试

教程中的示例代码应该：
1. 可运行
2. 有测试
3. 包含预期输出

## 状态

- ✅ 基础设施：已完成
- 🚧 教程内容：编写中
- 📋 视频脚本：规划中

---

**版本**: 1.0.0
**创建时间**: 2026-01-10
**维护者**: cc-tutorial 项目
