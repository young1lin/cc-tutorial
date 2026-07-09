# 权限与沙箱

## 先说结论

**[Tutorial perspective]** 权限体系是 Claude Code 的刹车。基础篇讲过怎么开车，这篇只讲刹车怎么配：六档 permission mode、五层 settings 优先级、一套 allow/ask/deny 规则。

## permission modes

`T1` 官方口径（[Permission modes](https://code.claude.com/docs/en/permission-modes)、[Configure permissions](https://code.claude.com/docs/en/permissions)）。官方页实际列出 6 种模式，比常见的“五档”说法多一个 `auto`：

| 模式 | 行为 |
|------|------|
| `default` | 标准行为：每个工具首次使用时提示确认。CLI 与 VS Code/JetBrains 插件里标为 Manual，`manual` 是官方别名 |
| `acceptEdits` | 对工作目录（或 `additionalDirectories`）内的路径，自动接受文件编辑和 `mkdir`/`touch`/`mv`/`cp` 等常见文件系统命令 |
| `plan` | Plan Mode：只读文件、跑只读 shell 命令做调研，不编辑源码 |
| `auto` | 后台安全检查（独立分类器）通过后自动批准工具调用；官方标注为 research preview |
| `dontAsk` | 除非经 `/permissions` 或 `permissions.allow` 预先批准，否则自动拒绝所有会提示的调用 |
| `bypassPermissions` | 跳过几乎所有权限提示；显式 `ask` 规则、`rm -rf /`、`rm -rf ~` 等根目录/home 删除仍会强制提示 |

`default → acceptEdits → plan` 用 `Shift+Tab` 循环切换；`auto`、`bypassPermissions` 需先满足解锁条件（账号/模型/启动参数）才会加入循环；`dontAsk` 不进循环，只能靠 `--permission-mode dontAsk` 或 `defaultMode` 设置。

## permissions 规则

`T1` settings.json 里的规则语法：`allow` 放行、`ask` 强制确认、`deny` 阻断。三者按 **deny → ask → allow** 顺序求值，第一个命中的规则生效——规则粒度不改变这个顺序，粗粒度 `deny` 能挡住细粒度 `allow`。

```json
{
  "permissions": {
    "allow": ["Bash(npm run *)", "Bash(git commit *)"],
    "ask": ["Bash(git push *)"],
    "deny": ["Read(./.env)", "Read(./secrets/**)"]
  }
}
```

作用域优先级（[Settings precedence](https://code.claude.com/docs/en/permissions#settings-precedence)），从高到低：managed settings → 命令行参数 → local project（`.claude/settings.local.json`，不入库）→ shared project（`.claude/settings.json`，入库共享）→ user（`~/.claude/settings.json`）。这与“user → project → local 依次覆盖”的直觉正好相反：任意层的 `deny`，其他层都盖不掉。

## 沙箱

`T1`（[Configure permissions](https://code.claude.com/docs/en/permissions#how-permissions-interact-with-sandboxing)、[Security](https://code.claude.com/docs/en/security)）：permissions 和 sandbox 是互补的两层，不是二选一。permissions 控制 Claude 能调用哪些工具、能碰哪些文件和域名，覆盖全部工具；sandbox 是操作系统级隔离，只管 Bash 工具及其子进程的文件系统和网络访问。`/sandbox` 开启后，默认的 `autoAllowBashIfSandboxed: true` 会让沙箱内的 Bash 命令免提示执行——沙箱边界替代了那次全工具提示，但内容级 `ask` 规则、显式 `deny`、对根目录/home 目录的删除仍然生效。

## 怎么选

**[Tutorial perspective]** 日常开发 acceptEdits；动基建、跑不熟悉的仓库用 default；bypassPermissions 只配隔离环境（容器、一次性 VM）——它不是效率档，是拆刹车。
