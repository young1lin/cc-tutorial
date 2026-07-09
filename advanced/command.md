# Command

## Command 放哪里

项目级自定义 command 放在：

```text
.claude/commands/
```

例如：

```text
.claude/commands/commit-push.md
```

## Command 的本质

**[Tutorial perspective]** Command 的本质通常就是一段强提示词，加上一组固定的执行步骤。它不是神秘机制。它只是把“每次都要重复说一遍的话”压成一个可调用入口。

所以 command 很适合做这些事：

- 固定 Git 工作流
- 固定同步流程
- 固定代码审查流程
- 固定发布前检查

不适合做这些事：

- 持久化领域知识
- 维护复杂目录路由
- 承载大量参考资料
- 沉淀长期业务记忆

## 为什么说它像 Skill 的前身

**[Tutorial perspective]** 很多团队一开始只有 command。因为它便宜，写得快，立刻能用。等命令背后的知识开始膨胀，固定提示词已经装不下，就会自然长成 skill。

演化路径通常是这样：

1. 先有一段反复复制的提示词
2. 然后把它塞进 `.claude/commands/*.md`
3. 再往后，发现还需要脚本、参考资料、模板、路由
4. 这时 command 已经不够，skill 才是正解

## Command 与 Skill 的区别

Command 解决“怎么触发一段固定流程”。

Skill 解决“怎么把一类长期能力和知识沉淀下来，并按需加载”。

一个简单判断：

- 只是想把常说的话压缩成入口，用 command
- 想把知识、脚本、模板、路由和同步机制都放进去，用 skill

## 在这个仓库里的例子

- [commit-push command](../.claude/commands/commit-push.md)
- [business-logic skill](../.claude/skills/business-logic/SKILL.md)

`business-logic` 不再放在 `.claude/commands/`。这个例子现在完全收回 skill。

## 安全

Command 本身主要是提示词风险。Skill 往往叠加了提示词风险、脚本风险、第三方代码风险和供应链风险。

**[Author's analysis]** 所以公共市场里的第三方 skill 比普通 command 危险得多。command 说错话，通常是流程跑偏。skill 带恶意脚本，可能直接把机器卖了。
