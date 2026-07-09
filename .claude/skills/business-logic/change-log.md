# Business Logic Change Log

## 记录格式

```md
## YYYY-MM-DD HH:mm
- mode: init | sync | last
- scope: 涉及的业务域
- files: 受影响文件或提交范围
- commits: 最近提交数量或具体范围，例如 HEAD~2..HEAD
- summary: 更新了什么
- evidence: 依据哪些代码位置得出结论
- unknowns: 仍然无法确认的点
```

## Entries

---

## 2026-03-07 15:30
- mode: init
- scope: video-scripts, research, examples, shared
- files: 新建知识库索引
- commits: N/A (初始化)
- summary: |
    完成仓库知识库初始化，创建 3 个业务单元 + 1 个共享目录：

    **video-scripts 单元**
    - `video-scripts/overview.md` - 9 层教程体系概览
    - `video-scripts/layer-06-advanced.md` - 高级功能主题

    **research 单元**
    - `research/overview.md` - 研究材料索引 (12 篇 + summary)
    - `research/prompt-caching.md` - Prompt Caching 主题

    **examples 单元**
    - `examples/overview.md` - 代码示例概览
    - `examples/agent-patterns.md` - Agent 模式实现主题

    **shared**
    - `shared/cross-cutting.md` - 证据引用、写作风格、中国开发者适配
- evidence: |
    - 仓库目录结构扫描
    - video-scripts/README.md (目录定义)
    - research/00-research-summary.md (研究索引)
    - examples/ 各子目录文件
    - CLAUDE.md (项目说明)
- unknowns: 部分研究材料的原始 URL 可能已失效
