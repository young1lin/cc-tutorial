# Claude Code 全面教程 - 概述

## 教程简介

欢迎来到 Claude Code 全面教程！这是一个专为视频制作设计的完整学习资源，旨在帮助你从零开始掌握 Claude Code，并将其融入到你的日常开发工作流中。

### 本教程将帮助你：

- ✅ 理解 Claude Code 的核心概念和设计哲学
- ✅ 掌握从基础到高级的所有功能
- ✅ 学习业界专家的最佳实践
- ✅ 通过真实项目案例（mybatis-boost）理解实战应用
- ✅ 构建适合自己的 AI 辅助开发工作流

---

## 教程结构

本教程分为 **10 个模块**，共 **39 章**，涵盖从入门到精通的所有内容：

### 模块 1: 入门基础 (4 章)
适合 Claude Code 新手，涵盖安装、配置、核心快捷键和最重要的 Plan Mode 功能。

### 模块 2: 核心工作流 (4 章)
学习 Claude Code 用户日常使用的核心工作模式，包括探索-计划-编码-提交循环、TDD、多实例协作等。

### 模块 3: 高级功能 (5 章)
深入了解 Plugin、MCP、Skills、Hooks 和自定义命令等高级功能。

### 模块 4: 实战案例 - mybatis-boost (5 章)
通过一个真实的 VSCode 插件项目，学习如何在实际项目中应用 Claude Code。

### 模块 5: 架构与设计模式 (4 章)
学习如何设计适合 AI 辅助开发的系统架构，包括整洁架构、洋葱架构、六边形架构等。

### 模块 6: 理解大模型局限性 (3 章)
建立对 LLM 能力和边界的正确理解，避免常见陷阱。

### 模块 7: 专家建议与最佳实践 (4 章)
汇集 Claude Code 之父 Boris Power、Andrew Ng、Addy Osmani 等专家的权威建议。

### 模块 8: 构建自己的工作流 (4 章)
帮助你根据个人和团队需求定制 Claude Code 工作流。

### 模块 9: 高级话题与未来方向 (3 章)
探讨 CI/CD 集成、企业级应用和 AI 辅助编码的未来趋势。

### 模块 10: 快速参考与故障排除 (3 章)
提供实用的速查表、故障排除指南和社区资源。

---

## 学习路径建议

### 初学者路径
如果你是 Claude Code 的新手，建议按顺序学习：
1. **模块 1** → 掌握基础
2. **模块 2** → 学习核心工作流
3. **模块 6** → 理解 LLM 局限性（重要！）
4. **模块 7** → 学习专家建议
5. **模块 8** → 构建自己的工作流

### 进阶者路径
如果你已经有 Claude Code 基础，可以直接跳到：
1. **模块 3** → 高级功能
2. **模块 4** → 实战案例
3. **模块 5** → 架构设计
4. **模块 9** → 高级话题

### 快速参考路径
需要快速查找特定内容：
- **模块 10** → 命令速查表和故障排除

---

## 核心概念预览

### Plan Mode：最重要的功能

> **"始终以 Plan Mode 开始"** - Boris Power (Claude Code 之父)

**激活方式**: 按 `Shift+Tab` 两次

**何时使用**:
- 多文件/多步骤实现
- 理解大型代码库
- 端到端重构规划
- 测试生成和 QA 规划
- 复杂任务分解

**何时不使用**:
- 快速修复
- 简单单文件编辑
- 样板代码生成
- 需要低延迟的实验性迭代

### 核心快捷键

| 快捷键 | 功能 |
|--------|------|
| `Shift+Tab` | 切换 Plan Mode |
| `Alt+V` | 粘贴图片 |
| `Escape` | 中断操作 |
| `Escape Escape` | 跳回历史记录 |
| `/clear` | 清空上下文 |
| `/help` | 显示帮助 |
| `/permissions` | 管理权限 |

### "AI 辅助工程" vs "AI 自动化工程"

> **"AI 编码助手是令人难以置信的倍增器，但人类工程师仍然是节目的导演。"** - Addy Osmani (Google Chrome Engineer)

**关键区别**：
- ❌ **AI 自动化工程**: 让 AI 自主完成一切，期望完全无人干预
- ✅ **AI 辅助工程**: 将 AI 作为强大的结对程序员，需要清晰的指导、上下文和监督

**你在循环中**：
- 必须审查和测试所有 AI 生成的代码
- 保持对软件产出的责任
- AI 放大你的专业知识，而不是替代它

---

## 实战案例：mybatis-boost

本教程使用 **mybatis-boost** 作为贯穿的实战案例。这是一个通过 Claude Code 创建的 VSCode 插件，为 MyBatis ORM 框架提供全面支持。

### 项目亮点

1. **CST vs 正则表达式**: 使用具体语法树而非正则表达式处理 MyBatis XML
2. **Provider 模式**: 同时支持 Cursor 和 VS Code Copilot 的 MCP
3. **性能优化**: LRU 缓存、文件监视器、延迟解析
4. **完整测试**: 37 个测试文件，单元测试和集成测试

### 你将学到

- 如何用 Claude Code 设计复杂功能
- 如何构建可扩展的架构
- 如何处理 AI 的局限性
- 如何优化性能

---

## 专家来源

本教程内容基于以下权威来源：

### 官方文档
- **Anthropic 官方最佳实践** - Boris Cherny 执笔
- **Plan Mode 官方指南** - Claude AI Team

### 权威课程
- **DeepLearning.AI x Anthropic 课程** - Elie Schoppik (Anthropic 技术教育主管)

### 专家文章
- **Addy Osmani** (Google Chrome Engineer) - 2026 AI 编码工作流
- **Ethan Mollick** (Wharton 教授) - Claude Code 和未来
- **Zvi Mowshowitz** - 并行工作流实践

### 研究材料
所有研究材料保存在 `docs/research/` 目录，包含：
- 完整的元信息（作者、日期、来源）
- 专家建议的原始内容
- 可离线访问的本地副本

---

## 视频脚本格式

每章内容都包含视频脚本部分，格式如下：

### 每集结构（5-15 分钟）

1. **引入（30-60 秒）**
   - 将要学习什么
   - 为什么重要

2. **概念讲解（2-3 分钟）**
   - 清晰解释
   - 配合视觉元素（图表、动画）

3. **实战演示（5-8 分钟）**
   - 现场编码/演示
   - 屏幕录制

4. **总结（1-2 分钟）**
   - 关键要点
   - 下一步

5. **练习（可选）**
   - 实践练习
   - 巩固学习

### 视觉元素

- 架构图、工作流程图、数据流图
- 前后对比、有无 Claude Code 对比
- 代码高亮（关键模式和反模式）
- 屏幕录制（真实工作流程）
- 速查表（快速参考覆盖层）

---

## 输出文档结构

```
C:\PythonProject\cc-tutorial\
├── docs/
│   ├── tutorial/              # 教程内容
│   │   ├── 00-tutorial-overview.md  # 本文件
│   │   ├── module-01-fundamentals/   # 模块 1
│   │   ├── module-02-core-workflows/ # 模块 2
│   │   ├── ...                          # 其他模块
│   │   └── module-10-reference/        # 模块 10
│   ├── video-scripts/         # 视频脚本
│   ├── examples/              # 示例代码
│   │   ├── claude-md-templates/
│   │   ├── skill-examples/
│   │   ├── mcp-server-examples/
│   │   └── hook-examples/
│   └── research/              # 研究材料
├── scripts/                   # 生成脚本
└── CLAUDE.md
```

---

## 开始学习

现在你已经了解了教程的全貌，建议你：

1. **初学者**: 从 [模块 1 - 入门基础](module-01-fundamentals/chapter-01-introduction.md) 开始
2. **有经验者**: 跳转到你感兴趣的模块
3. **快速参考**: 查看 [模块 10 - 快速参考](module-10-reference/chapter-37-command-cheatsheet.md)

---

## 关于本教程

- **创建时间**: 2026-01-10
- **版本**: 1.0.0
- **项目**: cc-tutorial
- **实战案例**: [mybatis-boost](https://github.com/young1lin/mybatis-boost)

### 贡献者

- **研究和策划**: Claude (Anthropic)
- **实战案例**: young1lin
- **专家来源**: Boris Power, Andrew Ng, Addy Osmani, Ethan Mollick, Zvi Mowshowitz

---

祝你学习愉快！让我们开始探索 Claude Code 的世界吧！ 🚀
