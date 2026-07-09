# Plugins 打包与分发

## 先说结论

Plugin 不是第九个扩展点，是打包格式：把 skills、agents、hooks、MCP、LSP 装进一个目录，命名空间化，版本化，经市场分发。[扩展机制全景](EXTENSIONS_OVERVIEW.md)渐进构建表的最后一行承诺过「第二个仓库要同样配置 → 打包成 plugin」——本文兑现它。全文对照官方 [Create plugins](https://code.claude.com/docs/en/plugins)、[Plugin marketplaces](https://code.claude.com/docs/en/plugin-marketplaces)、[Plugins reference](https://code.claude.com/docs/en/plugins-reference)（`T1`，2026-07-07 校对 @ Claude Code v2.1.202），活体解剖两个：官方市场里的 superpowers / gopls-lsp（本机缓存），和本教程作者的 [claude-token-monitor](https://github.com/young1lin/claude-token-monitor)。

先决策再动手（`T1` 官方对照）：

| | standalone `.claude/` | Plugin |
|---|---|---|
| skill 名字 | `/hello` | `/my-plugin:hello`（命名空间防撞名） |
| 适合 | 单项目、个人、快速实验 | 团队共享、跨项目复用、版本化更新、市场分发 |

官方路线也是这个顺序：先在 `.claude/` 里迭代，要分发了再打包。

## 插件解剖

一条铁律，官方标注为 Common mistake（`T1`）：**只有 `plugin.json` 进 `.claude-plugin/`，其余全在插件根目录**。

| 位置 | 装什么 | 备注 |
|------|--------|------|
| `.claude-plugin/plugin.json` | manifest | 整个文件可省——组件放默认位置即可，名字取目录名 |
| `skills/` | `<name>/SKILL.md` | 主力形态；单 skill 插件可直接根放 `SKILL.md` |
| `commands/` | 扁平 `.md` | 遗留形态，官方建议新插件用 `skills/` |
| `agents/` | agent 定义 | 同名时项目/用户级 `.claude/agents/` 覆盖插件版 |
| `hooks/hooks.json` | hook 配置 | 格式与 settings.json 的 `hooks` 对象相同，见 [Hooks 完全参考](HOOKS_GUIDE.md) |
| `.mcp.json` | MCP server 配置 | 随插件启用连接 |
| `.lsp.json` | LSP 配置 | 冷门，见下文 gopls-lsp 活体 |
| `monitors/monitors.json` | 后台监视器 | 冷门：stdout 逐行变成会话通知 |
| `bin/` | 可执行文件 | 冷门：插件启用期间进 Bash 工具的 PATH |
| `settings.json` | 默认设置 | 冷门：仅 `agent` / `subagentStatusLine` 两键，前者能把主线程换成插件自带 agent |

`plugin.json` 里 **`name` 是唯一必填字段**（`T1`）。常用可选：`description`、`version`、`author`、`homepage`、`repository`、`license`、`keywords`、`displayName`（≥ v2.1.143）、`defaultEnabled: false`（≥ v2.1.154，装完默认关闭，适合连外部服务的插件）。组件路径字段（`skills`、`hooks`、`mcpServers`、`lspServers` 等）能改默认位置，`hooks`/`mcpServers`/`lspServers` 还接受内联对象。没认出来的顶层字段直接忽略（`validate` 只报 warning）——所以一份 manifest 可以同时兼任 npm 或 VS Code 扩展的 manifest（`T1`）。

**版本机制是最大的坑**（`T1`）。版本解析顺位：plugin.json 的 `version` → 市场条目的 `version` → git commit SHA → `unknown`。两种玩法：

- **显式版本**：设了 `version`，用户只在你 bump 它时收到更新——只推 commit 不 bump，`/plugin update` 报「already at the latest version」，改动永远到不了用户手里。
- **SHA 版本**：两边都不设 `version`，每个 commit 都是新版本。官方建议：快速迭代期就别设。

`T1`（官方 plugins-reference）：缓存目录名是解析后的版本——设了显式 `version` 就是版本号（本机 superpowers 缓存目录是 `6.1.1`，因 manifest 设了 `version`）；两边都不设 `version` 时目录名是 commit SHA，每个 commit 一个新目录。快速迭代期官方建议别设 `version`，正是这个原因。

路径引用用三个变量（`T1`）：`${CLAUDE_PLUGIN_ROOT}`（安装目录，**每次更新都换路径**，旧目录约七天后清理，别往里写状态）、`${CLAUDE_PLUGIN_DATA}`（跨版本持久，放依赖、缓存）、`${CLAUDE_PROJECT_DIR}`（项目根）。

## 本地开发闭环

```bash
claude plugin init my-tool        # scaffold into ~/.claude/skills/my-tool/, loads next session as my-tool@skills-dir
claude --plugin-dir ./my-plugin   # load without installing; repeat the flag for multiple plugins
/reload-plugins                   # pick up changes without restart
claude plugin validate ./my-plugin --strict   # warnings become errors; run before publishing
```

`--plugin-dir` 也接受 `.zip` 和远程 `--plugin-url`（见官方 plugins 文档）。同名时本地插件覆盖已安装的市场插件——改装了的插件不用先卸载就能测（managed 强制启停项除外）。

`@skills-dir` 是「打包但不分发」的中间态（`T1`）：skills 目录下任何带 `.claude-plugin/plugin.json` 的文件夹，下个会话直接以 `<name>@skills-dir` 加载，不进缓存、不需要市场。项目级（`<cwd>/.claude/skills/`）随仓库到达每个协作者，但过信任门禁：MCP server 逐个审批、LSP 信任工作区后才启动、monitors 干脆不加载；个人级（`~/.claude/skills/`）无这些限制。

CLI 全家桶（`实测` `claude plugin --help`）：`init`、`validate`、`install`、`list`、`enable`/`disable`、`update`、`uninstall`、`prune`，以及三个文档少提的：`details`（组件清单 + **预估 token 成本**）、`eval`（对插件跑评测用例，自带无插件基线对照）、`tag`（发版打 `{name}--v{version}` git tag，顺带校验 plugin.json 与市场条目一致）。

## marketplace.json 解剖

市场 = 仓库根放一个 `.claude-plugin/marketplace.json`：必填 `name`、`owner`、`plugins[]`；每个条目必填 `name` + `source`（`T1`）。五种 source：

| source | 写法 | 钉版本 |
|--------|------|--------|
| 相对路径 | `"./plugins/formatter"` | 随市场仓库 commit |
| `github` | `{"source": "github", "repo": "owner/repo"}` | `ref` / `sha` |
| git URL | `{"source": "url", "url": "https://...git"}` | `ref` / `sha` |
| `git-subdir` | 大仓库取子目录 | `ref` / `sha` |
| `npm` | npm 包 | 包版本 |

规则（`T1`）：插件的 `source` 里 `ref`（分支/标签）和 `sha`（精确 commit）都设时 `sha` 生效。**市场本身的 source 和插件的 source 是两回事**——市场用 `github`/`url` 形式注册（如本机 known_marketplaces 的 `{"source":"github","repo":...}`），钉默认分支、不接受单独 `ref`；只有插件条目才支持 `ref`/`sha` 钉版。相对路径条目在「用户用 URL 直链添加市场」时失效——只下载了 marketplace.json 一个文件，没有仓库。

`strict` 字段（默认 `true`）决定谁说了算：true 时 plugin.json 是权威；false 时市场条目全权定义、插件可以连 plugin.json 都没有。这不是边角料——官方市场（255 个插件）自己就在用（`实测`，本机缓存的官方 marketplace.json）：

```json
{ "name": "gopls-lsp", "version": "1.0.0", "source": "./plugins/gopls-lsp",
  "strict": false,
  "lspServers": { "gopls": { "command": "gopls", "extensionToLanguage": { ".go": "go" } } } }
```

源目录里只有 README 和 LICENSE，功能全在条目里。而对第三方仓库 obra/superpowers，官方条目是 `{"source": "url", "url": "https://github.com/obra/superpowers.git", "sha": "d884ae04..."}`——**引别人的仓库，钉死精确 commit**。这里的 `sha` 钉的是源 commit（供应链纪律），不是缓存目录名；superpowers 自己设了 `version: 6.1.1`，所以缓存目录仍是 `6.1.1`。

作者侧活体（`实测`，[claude-token-monitor](https://github.com/young1lin/claude-token-monitor)）：一个 marketplace.json 同时示范两种形态——`claude-token-monitor` 自己用 `"source": "./"`（插件仓库兼任自己的市场），第二个插件 cc-otel 用 `{"source": "url", "url": ".../cc-otel.git", "ref": "v0.1.0-preview.2"}`（远程仓库钉 tag）。

## 分发与安装链路

用户侧三步（`实测`，本机走通）：

```bash
/plugin marketplace add young1lin/claude-token-monitor      # register the marketplace
/plugin install claude-token-monitor@claude-token-monitor   # plugin@marketplace
# lands in <config-dir>/plugins/cache/<marketplace>/<plugin>/<version>/
```

更新是两段式：作者推送后，用户 `/plugin marketplace update` 刷新目录、`/plugin update <plugin>` 升级插件（要重启会话生效）。**不跑 update，用户永远停在装机那天的版本**——`/plugin update` 报「already at the latest version」只反映你本地目录里的版本，不反映远端仓库。

团队分发不用公开：私有 git 仓库做市场，配合 settings 的 `extraKnownMarketplaces` 预注册即可（`T1`）。

## 两个官方市场

| | claude-plugins-official | claude-community |
|---|---|---|
| 机制 | 官方策展，**无申请通道** | 表单投稿 → 审核 → 上架 |
| 注册 | 首次交互启动自动注册 | `/plugin marketplace add anthropics/claude-plugins-community` |
| 审核 | Anthropic 自行决定 | 跑同款 `claude plugin validate` + 自动安全扫描 |
| 钉版 | 策展条目（如 superpowers 钉 SHA） | 过审钉 commit SHA，作者再推 commit 由 CI 自动 bump，目录夜间同步 |

投稿入口：个人走 [platform.claude.com/plugins/submit](https://platform.claude.com/plugins/submit)（claude.ai 表单需要 Team/Enterprise 组织）。投稿前本地先跑 `claude plugin validate`——审核管线跑的就是它（`T1`）。上了官方市场的插件还能让自家 CLI 提示 Claude Code 用户安装（plugin-hints，`T1`）。

## 活例子

- **superpowers**（`实测`，本机缓存 v6.1.1）：`.claude-plugin/` + `hooks/`（SessionStart 注入 bootstrap，见 [SUPERPOWERS_GUIDE](SUPERPOWERS_GUIDE.md)）+ `skills/` 主体，根目录还躺着 `.codex-plugin`、`.cursor-plugin`、`.kimi-plugin`、`.opencode`、`.pi`、`gemini-extension.json`——同一个仓库同时发行到六家 agent 平台。manifest 的「未识别字段忽略」规则就是为这种一仓多平台准备的。
- **gopls-lsp**（`实测`）：整个插件 = 市场条目里一段内联 `lspServers`，源目录只有文档。最小可行插件可以小到没有代码。
- **claude-token-monitor 的「command 当安装器」**（`实测`）：插件本体是 Go 二进制 statusline，但二进制没法靠插件机制自动进 `settings.json`——它的 `commands/setup.md` 把安装流程写成 slash command：解析 `$CLAUDE_CONFIG_DIR`（多账号环境 env var 优先于 `~/.claude`）、查已装版本走更新流、指挥 Claude 下载二进制并改配置（`command` 字段必须绝对路径，Claude Code 不展开 `~` 和环境变量）。插件机制当分发渠道、Claude 当安装员——官方文档不展示的真实模式。

## 安全边界

装插件 = 接受四件事以你的权限发生：它的 hooks 直接跑（[安全四纪律](HOOKS_GUIDE.md)照单全收）、`bin/` 进 PATH、`settings.json` 能把主线程换成它的 agent、MCP server 随启用连接。市场安全告警见 [README](README.md)。本篇追加一条：**市场条目只有 `ref` 没有 `sha`，就是追着别人的 HEAD 跑**——你装的是「现在的它」，不是「你审过的它」。官方对 obra/superpowers 都钉 SHA，你引第三方插件没理由不钉。

## 何时不用

**[Tutorial perspective]** 打包的触发条件只有一个：第二个仓库或第二个人要用。单项目自用别打包——`.claude/` 直接放，skill 名字还短（`/hello` vs `/my-plugin:hello`），官方自己也把 standalone 排在前面。中间还有一档：只想给自己所有项目复用、不想开市场，`claude plugin init` 的 `@skills-dir` 形态就够了。市场是分发工具，不是收纳癖的奖章。
