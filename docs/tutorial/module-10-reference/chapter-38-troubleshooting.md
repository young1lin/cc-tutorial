# Chapter 38: 故障排除指南

## 概述

本章提供 Claude Code 常见问题的解决方案和调试技巧。

---

## 38.1 安装问题

### 问题：安装失败

```bash
# 错误信息
npm install -g @anthropic-ai/claude-code
# Error: EACCES: permission denied

# 解决方案 1：使用 sudo (macOS/Linux)
sudo npm install -g @anthropic-ai/claude-code

# 解决方案 2：使用 npx（无需安装）
npx @anthropic-ai/claude-code

# 解决方案 3：修复 npm 权限
mkdir ~/.npm-global
npm config set prefix '~/.npm-global'
export PATH=~/.npm-global/bin:$PATH
npm install -g @anthropic-ai/claude-code
```

### 问题：命令未找到

```bash
# 错误信息
claude-code: command not found

# 解决方案 1：检查安装
which claude-code

# 解决方案 2：添加到 PATH（macOS/Linux）
echo 'export PATH="$PATH:/path/to/npm/bin"' >> ~/.bashrc
source ~/.bashrc

# 解决方案 3：使用 npx
npx @anthropic-ai/claude-code

# Windows: 重新启动终端或重新登录
```

### 问题：版本不兼容

```bash
# 错误信息
Error: Node.js version too old. Minimum required: 18.0.0

# 解决方案：升级 Node.js
# 使用 nvm (推荐)
nvm install 20
nvm use 20

# 或从官网下载
# https://nodejs.org/
```

---

## 38.2 API 问题

### 问题：API 密钥错误

```bash
# 错误信息
Error: 401 Unauthorized
Invalid API key

# 解决方案 1：检查密钥
echo $ANTHROPIC_API_KEY

# 解决方案 2：设置正确的密钥
export ANTHROPIC_API_KEY="sk-ant-..."

# 解决方案 3：保存到配置文件
mkdir -p ~/.config/claude
echo "ANTHROPIC_API_KEY=sk-ant-..." > ~/.config/claude/.env

# 解决方案 4：检查密钥格式
# 应该以 sk-ant- 开头
```

### 问题：API 配额用尽

```bash
# 错误信息
Error: 429 Too Many Requests
Rate limit exceeded

# 解决方案 1：检查使用情况
# 登录 Anthropic 控制台查看配额

# 解决方案 2：等待配额重置
# 配额通常每小时或每天重置

# 解决方案 3：升级账户
# 访问 https://console.anthropic.com/

# 解决方案 4：使用更小的模型
claude-code --model claude-haiku
```

### 问题：网络连接问题

```bash
# 错误信息
Error: Network timeout
Could not connect to API

# 解决方案 1：检查网络连接
ping api.anthropic.com

# 解决方案 2：使用代理
export HTTP_PROXY=http://proxy.example.com:8080
export HTTPS_PROXY=http://proxy.example.com:8080

# 解决方案 3：设置超时
claude-code --timeout 120000

# 解决方案 4：使用不同的 API 端点
export ANTHROPIC_BASE_URL=https://api.anthropic.com
```

---

## 38.3 权限问题

### 问题：Edit 工具被阻止

```bash
# 现象：Claude 无法编辑文件

# 解决方案 1：检查权限
/permissions

# 解决方案 2：允许 Edit 工具
/permissions allow edit

# 解决方案 3：在配置文件中设置
cat > ~/.config/claude/config.json << EOF
{
  "permissions": {
    "edit": "always"
  }
}
EOF

# 解决方案 4：检查文件权限
ls -la file.ts
chmod u+w file.ts
```

### 问题：Bash 命令被阻止

```bash
# 现象：Claude 无法执行命令

# 解决方案 1：允许特定命令
/permissions allow git

# 解决方案 2：允许所有 bash（开发环境）
/permissions allow bash

# 解决方案 3：在配置中设置允许的命令
cat > ~/.config/claude/config.json << EOF
{
  "permissions": {
    "bash": "always",
    "allowedCommands": ["git", "npm", "node", "ls", "cat"]
  }
}
EOF
```

### 问题：文件写入被阻止

```bash
# 现象：无法创建或修改文件

# 解决方案 1：允许 Write 工具
/permissions allow write

# 解决方案 2：检查磁盘空间
df -h

# 解决方案 3：检查文件锁定
lsof | grep file.ts
```

---

## 38.4 性能问题

### 问题：响应缓慢

```bash
# 现象：Claude 响应时间很长

# 诊断 1：检查网络
ping api.anthropic.com

# 诊断 2：检查模型
claude-code --model claude-haiku  # 使用更快的模型

# 诊断 3：减少上下文
# 不要同时提及太多文件

# 解决方案：使用缓存
# 重复使用相同的上下文
```

### 问题：内存占用高

```bash
# 现象：Claude Code 占用大量内存

# 诊断：检查内存使用
# Windows: 任务管理器
# macOS: Activity Monitor
# Linux: top 或 htop

# 解决方案 1：限制上下文大小
# 只提供必要的文件

# 解决方案 2：定期重启
# 关闭并重新打开 Claude Code

# 解决方案 3：清理缓存
rm -rf ~/.claude/cache
```

### 问题：CPU 占用高

```bash
# 现象：CPU 使用率持续高

# 诊断 1：检查后台进程
ps aux | grep claude

# 诊断 2：检查是否有多个实例
pgrep claude-code

# 解决方案：关闭多余实例
killall claude-code
```

---

## 38.5 上下文问题

### 问题：Claude 不知道项目结构

```bash
# 现象：Claude 给出的建议不符合项目结构

# 解决方案 1：创建 CLAUDE.md
cat > CLAUDE.md << EOF
# 项目概述

## 项目结构
src/
├── components/
├── services/
└── utils/

## 技术栈
- React 18
- TypeScript 5
- Tailwind CSS
EOF

# 解决方案 2：在提示中提及文件
> 查看 src/components/Header.tsx 和 src/utils/auth.ts

# 解决方案 3：使用 Plan Mode
[Shift+Tab][Shift+Tab]
```

### 问题：上下文超出限制

```bash
# 现象：错误：上下文太长

# 解决方案 1：减少文件数量
# 只提及关键文件

# 解决方案 2：使用摘要
> 项目是一个 React 应用，主要组件是...

# 解决方案 3：分阶段处理
> 先分析 A 部分，再分析 B 部分
```

### 问题：Claude 忘记之前的内容

```bash
# 现象：Claude 不记得之前的对话

# 解决方案 1：不要使用 /clear
# /clear 会清空所有上下文

# 解决方案 2：重新提及关键信息
> 如前所述，我们使用的是 React 18...

# 解决方案 3：使用 CLAUDE.md
# 将重要信息放在 CLAUDE.md 中
```

---

## 38.6 MCP 服务器问题

### 问题：MCP 服务器未加载

```bash
# 现象：MCP 工具不可用

# 诊断 1：使用调试模式
claude-code --mcp-debug

# 诊断 2：检查配置文件
cat ~/.config/claude/mcp.json

# 解决方案 1：检查包是否安装
npx -y @modelcontextprotocol/server-github --version

# 解决方案 2：检查环境变量
echo $GITHUB_TOKEN

# 解决方案 3：验证配置格式
# 确保 JSON 格式正确
```

### 问题：MCP 服务器连接失败

```bash
# 现象：MCP 服务器连接超时

# 解决方案 1：检查网络
ping github.com

# 解决方案 2：检查 API 密钥
echo $GITHUB_TOKEN

# 解决方案 3：测试服务器
npx -y @modelcontextprotocol/server-github

# 解决方案 4：检查防火墙
# 确保 MCP 服务器可以访问外部 API
```

### 问题：MCP 工具返回错误

```bash
# 现象：MCP 工具执行失败

# 诊断：查看详细错误
claude-code --mcp-debug

# 解决方案 1：检查参数
# 确保传递给工具的参数正确

# 解决方案 2：检查权限
# 确保 MCP 服务器有足够的权限

# 解决方案 3：重启 MCP 服务器
# 退出 Claude Code 并重新启动
```

---

## 38.7 Plan Mode 问题

### 问题：Plan Mode 无法激活

```bash
# 现象：按 Shift+Tab 两次没有反应

# 解决方案 1：检查是否在正确位置
# 确保光标在输入区域

# 解决方案 2：使用命令
/plan

# 解决方案 3：检查配置
cat ~/.config/claude/config.json

# 解决方案 4：重启 Claude Code
```

### 问题：计划不满意

```bash
# 现象：Claude 生成的计划不够好

# 解决方案 1：提供更多上下文
> 这个项目使用 React 和 TypeScript，
> 需要遵循我们的编码规范...

# 解决方案 2：明确要求
> 请先分析现有代码，再制定计划

# 解决方案 3：迭代改进
> 这个计划太简单了，请提供更详细的步骤

# 解决方案 4：手动指定步骤
> 计划应该包括：
> 1. 数据模型设计
> 2. API 端点创建
> 3. 前端组件实现
```

---

## 38.8 Git 集成问题

### 问题：Git 命令失败

```bash
# 现象：Claude 无法执行 git 命令

# 诊断 1：测试 Git
git status

# 诊断 2：检查权限
/permissions

# 解决方案 1：允许 Git
/permissions allow git

# 解决方案 2：检查 Git 配置
git config --list

# 解决方案 3：初始化仓库（如果需要）
git init
```

### 问题：提交消息生成失败

```bash
# 现象：/commit 命令无法生成提交消息

# 解决方案 1：检查是否有更改
git status

# 解决方案 2：暂存更改
git add .

# 解决方案 3：手动提供上下文
> 创建一个提交，包含以下更改：
> - 添加用户认证
> - 修复登录 bug
> - 更新文档

# 解决方案 4：手动创建提交
git commit -m "描述更改"
```

---

## 38.9 输出质量问题

### 问题：代码有语法错误

```bash
# 现象：Claude 生成的代码有语法错误

# 解决方案 1：指定语言版本
> 使用 TypeScript 5.3 语法

# 解决方案 2：提供代码示例
> 按照这种风格编写：
> [提供示例]

# 解决方案 3：要求验证
> 请确保代码可以编译通过

# 解决方案 4：使用 linter
> 在生成后运行 eslint 检查
```

### 问题：代码不符合项目风格

```bash
# 现象：生成的代码风格不一致

# 解决方案 1：在 CLAUDE.md 中定义风格
cat >> CLAUDE.md << EOF

## 代码风格
- 使用 2 空格缩进
- 单引号优先
- 箭头函数
- TypeScript 严格模式
EOF

# 解决方案 2：提供示例
> 按照现有代码的风格：
> [粘贴示例代码]

# 解决方案 3：使用 Prettier
> 生成后运行 prettier 格式化
```

### 问题：代码遗漏了边界情况

```bash
# 现象：生成的代码没有处理边界情况

# 解决方案 1：明确要求
> 请包括所有边界情况的错误处理

# 解决方案 2：列出边界情况
> 需要处理：
> - null 值
> - 空数组
> - 超出范围的值
> - 网络错误

# 解决方案 3：先写测试
> 请先编写测试，确保覆盖所有情况
```

---

## 38.10 调试技巧

### 启用调试模式

```bash
# 启用调试日志
claude-code --debug

# 启用 MCP 调试
claude-code --mcp-debug

# 查看日志文件
tail -f ~/.claude/logs/debug.log
```

### 检查配置

```bash
# 查看当前配置
/config

# 查看权限
/permissions

# 查看状态
/status

# 查看日志
/log
```

### 重置到默认状态

```bash
# 重置权限
/permissions reset

# 清空上下文
/clear

# 删除配置
rm ~/.config/claude/config.json

# 删除缓存
rm -rf ~/.claude/cache
```

### 收集诊断信息

```bash
# 创建诊断报告
claude-code --diagnose > diagnosis.txt

# 查看系统信息
uname -a
node --version
npm --version

# 查看环境变量
env | grep CLAUDE
env | grep ANTHROPIC
```

---

## 38.11 获取帮助

### 内置帮助

```bash
# 查看帮助
/help

# 查看版本
/version

# 查看配置
/config
```

### 在线资源

```bash
# 官方文档
https://docs.anthropic.com/claude-code/

# GitHub Issues
https://github.com/anthropics/claude-code/issues

# Discord 社区
https://discord.gg/anthropic
```

### 报告问题

报告问题时包含：

1. Claude Code 版本：`/version`
2. 操作系统和版本
3. Node.js 版本：`node --version`
4. 错误消息完整内容
5. 复现步骤
6. 预期行为 vs 实际行为

---

## 38.12 预防性措施

### 定期维护

```bash
# 定期清理缓存
rm -rf ~/.claude/cache

# 定期更新
npm update -g @anthropic-ai/claude-code

# 定期检查配置
cat ~/.config/claude/config.json
```

### 备份配置

```bash
# 备份配置文件
cp ~/.config/claude/config.json ~/.config/claude/config.json.backup

# 备份 CLAUDE.md
find . -name "CLAUDE.md" -exec cp {} {}.backup \;
```

### 监控使用

```bash
# 查看使用统计
/stats

# 检查 API 配额
# 登录 Anthropic 控制台
```

---

## 38.13 常见错误代码

| 错误代码 | 含义 | 解决方案 |
|----------|------|----------|
| 401 | 未授权 | 检查 API 密钥 |
| 429 | 请求过多 | 等待或升级配额 |
| 500 | 服务器错误 | 稍后重试 |
| 503 | 服务不可用 | 检查状态页面 |
| 400 | 错误请求 | 检查请求格式 |

---

## 38.14 快速修复清单

```
问题：Claude 不工作
□ 检查网络连接
□ 检查 API 密钥
□ 重启 Claude Code
□ 清空缓存
□ 更新到最新版本

问题：权限被拒绝
□ 检查 /permissions
□ 允许所需工具
□ 检查文件权限
□ 使用 sudo (如适用)

问题：输出质量差
□ 更新 CLAUDE.md
□ 提供更多上下文
□ 使用 Plan Mode
□ 明确指定要求

问题：性能慢
□ 使用更小的模型
□ 减少上下文
□ 检查网络速度
□ 清理缓存
```

---

## 38.15 进一步阅读

- [Chapter 37: 命令速查表](chapter-37-command-cheatsheet.md) - 上一章
- [Chapter 39: 社区资源](chapter-39-community-resources.md) - 下一章
- [Claude Code GitHub](https://github.com/anthropics/claude-code) - 源代码和问题

---

## 视频脚本

### Episode 38: 故障排除指南 (16 分钟)

#### [0:00-1:00] 引入

**视觉元素**：
- 标题："Claude Code 故障排除"
- 问题分类

**内容**：
> 即使是最佳工具也会遇到问题。
>
> 本章我们将学习如何诊断和解决 Claude Code 的常见问题。
>
> 从安装问题到性能问题，我们都有解决方案。

#### [1:00-4:00] 安装和 API 问题

**视觉元素**：
- 常见错误消息
- 解决方案步骤

**内容**：
> **安装问题**：
>
> ```
> Error: command not found
> ```
>
> 解决方案：
> 1. 检查 PATH
> 2. 使用 npx
> 3. 重新安装
>
> **API 问题**：
>
> ```
> Error: 401 Unauthorized
> ```
>
> 解决方案：
> 1. 检查 API 密钥
> 2. 设置环境变量
> 3. 验证密钥格式

#### [4:00-7:00] 权限和上下文问题

**视觉元素**：
- 权限检查命令
- CLAUDE.md 示例

**内容**：
> **权限问题**：
>
> ```
> Edit tool blocked
> ```
>
> 解决方案：
> ```
> /permissions allow edit
> ```
>
> **上下文问题**：
>
> Claude 不知道项目结构？
>
> 解决方案：创建 CLAUDE.md
> - 项目概述
> - 目录结构
> - 技术栈
> - 编码规范

#### [7:00-10:00] 性能和质量问题

**视觉元素**：
- 性能优化技巧
- 输出质量改进

**内容**：
> **性能问题**：
>
> - 使用更小的模型（Haiku）
> - 减少上下文
> - 清理缓存
>
> **质量问题**：
>
> - 代码有语法错误？
>   → 指定语言版本
>
> - 风格不一致？
>   → 在 CLAUDE.md 中定义风格
>
> - 缺少边界处理？
>   → 明确要求错误处理

#### [10:00-13:00] MCP 和 Plan Mode 问题

**视觉元素**：
- MCP 调试命令
- Plan Mode 故障排除

**内容**：
> **MCP 问题**：
>
> ```
> claude-code --mcp-debug
> ```
>
> 检查：
> - 配置文件格式
> - 环境变量
> - 网络连接
>
> **Plan Mode 问题**：
>
> 无法激活？
> - 检查光标位置
> - 使用 `/plan` 命令
> - 重启 Claude Code

#### [13:00-16:00] 调试技巧和总结

**视觉元素**：
- 调试命令清单
- 快速修复清单

**内容**：
> **调试技巧**：
>
> ```
> --debug        # 调试模式
> --mcp-debug    # MCP 调试
> /config        # 查看配置
> /permissions   # 查看权限
> /log           # 查看日志
> ```
>
> **快速修复清单**：
>
> - ✓ 检查网络
> - ✓ 检查 API 密钥
> - ✓ 重启 Claude Code
> - ✓ 清空缓存
> - ✓ 更新版本
>
> **获取帮助**：
> - `/help` 内置帮助
> - 官方文档
> - GitHub Issues
> - Discord 社区
>
> 下一章，最后一章：社区资源。
