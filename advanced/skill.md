# Skill

## Skill 的本质

`T1` 在 OpenClaw 的技能模型里，`SKILL.md` 至少需要 `name` 和 `description` 这两个元信息字段。技能本体可以继续挂载脚本、参考资料和资源文件。[Skills docs](https://docs.openclaw.ai/skills)

**[Tutorial perspective]** Skill 的本质不是“更长的提示词”。它是一个可路由、可分目录、可增量维护的能力包。提示词只是入口。真正值钱的是后面的目录、脚本、参考资料、知识沉淀和固定工作流。

## 为什么需要 Skill

不用 Skill，会反复掉进同一个坑：

- 每次新会话都要重新 Explore 整个项目
- 每次都要重新告诉 Agent 某个业务在哪里
- 每次都要重新解释某个 PDF 怎么生成、脚本放哪里、样例代码是什么
- 每次都把关键知识塞进聊天记录，下一次又丢光

这不是智能。是失忆。

Skill 解决的是这类重复成本：

- 把领域知识固定到目录里
- 把路由规则固定到 `SKILL.md`
- 把脚本固定到 `scripts/`
- 把参考资料固定到 `references/`
- 把输出模板固定到 `assets/`

## 为什么不是每次都在线搜索

**[Tutorial perspective]** 在线搜索擅长找“外部最新信息”。Skill 擅长沉淀“项目内部稳定结构”。两者不是替代关系。把稳定知识每次都交给搜索和探索，像每次进办公室先把工位拆了再重新摆。

适合放进 Skill 的内容：

- 项目自己的业务分层
- 接口与 service 的映射
- 常见改动的调用链
- PDF 生成方式
- 报表模板
- 常用脚本和样例代码
- 团队内部约定

适合在线搜索的内容：

- 官方文档最新变更
- 价格和配额
- 新发布的 API
- 安全公告

## Skill 与 business-logic

`business-logic` 这个 skill 的目标很直接：把代码、需求、业务规则、关键行号、时序图和改动影响，沉淀到按业务划分的目录里。

它不是为了替代 RAG 的所有能力。它是为了让会话一上来就拿到“这个业务为什么存在、代码在哪里、应该怎么改”。

在这个仓库里，`business-logic` 的入口协议也直接放在 `SKILL.md`，没有再在 `.claude/commands/` 下复制一份。

## 推荐结构

```text
.claude/skills/business-logic/
├── SKILL.md
├── change-log.md
├── shared/
│   └── cross-cutting.md
├── team/
│   ├── overview.md
│   ├── join-team.md
│   └── leave-team.md
└── order/
    ├── overview.md
    └── cancel-order.md
```

## 安全

`T1` OpenClaw 官方文档明确写了：第三方 skills 应被视为不受信任代码；涉及高风险工具或不受信任输入时，应优先采用沙箱。[Skills docs](https://docs.openclaw.ai/skills)

`T1` ClawHub 官方文档说明市场默认开放上传，治理主要依赖账号门槛、举报和隐藏机制。[ClawHub docs](https://docs.openclaw.ai/tools/clawhub)

`T3` 公开研究和报道已经把恶意 skills、凭据窃取和恶意载荷投递与 OpenClaw 生态直接关联起来。[Snyk report summary](https://snyk.io/articles/clawdhub-malicious-campaign-ai-agent-skills/) [TechRadar report](https://www.techradar.com/pro/security/openclaw-ai-agents-targeted-by-infostealer-malware-for-the-first-time)

**[Author's analysis]** 所以结论不该温和。公共 Skill Marketplace 不是玩具。恶意 skill 可以把你的 agent 变成数据外带器、下载器，甚至跳板机。别把能跑终端和读文件的 agent 当成浏览器插件。
