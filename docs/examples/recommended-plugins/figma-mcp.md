# 插件：Figma MCP

## 概述

Figma 官方 MCP 服务器，让 Claude 直接读取 Figma 设计文件，从组件结构生成代码，无需截图。

**类型**: MCP 服务器（官方）
**提供方**: Figma 官方
**官方文档**: `help.figma.com`
**传输协议**: HTTP（Streamable HTTP）

**解决的核心问题**：
传统工作流中，开发者需要截图 Figma 设计稿，然后把截图发给 Claude 要求生成代码。这种方式：
- 丢失精确尺寸、颜色值、间距等设计令牌
- 无法获取组件层级结构
- 无法访问变体和状态信息

Figma MCP 让 Claude 直接访问设计文件的原始数据，生成更准确的代码。

**使用场景**:
- 从设计稿直接生成 React/Vue 组件
- 提取设计令牌（颜色、字体、间距）
- 理解组件层级结构
- 设计稿与代码的自动同步

---

## 安装

### 方法一：命令行安装

```bash
claude mcp add --transport http figma https://mcp.figma.com/mcp
```

### 方法二：编辑配置文件

编辑 `~/.claude/mcp.json`：

```json
{
  "mcpServers": {
    "figma": {
      "type": "http",
      "url": "https://mcp.figma.com/mcp"
    }
  }
}
```

---

## 认证流程

安装后需要授权 Claude 访问你的 Figma 账号：

```bash
$ claude

> /mcp
```

在 MCP 列表中找到 `figma`，点击 **Authenticate** 按钮，浏览器会跳转到 Figma 授权页面，同意后返回 Claude Code 即完成认证。

---

## 工作原理

```
用户请求: "根据 Figma 中的 Button 组件生成 React 代码"
        │
        ▼
┌─────────────────────────┐
│   Figma MCP Server      │
│                         │
│ 1. 解析 Figma 文件 URL  │
│ 2. 通过 Figma API 获取  │
│    组件 JSON 结构        │
│ 3. 提取设计令牌          │
│    • 颜色（hex/rgba）    │
│    • 字体（大小/权重）   │
│    • 间距/圆角/阴影      │
│ 4. 返回结构化数据给 Claude│
└────────────┬────────────┘
             │
             ▼
      Claude 生成代码
      （包含精确的数值）
```

---

## 实际演示

### 基础用法：生成组件代码

```bash
$ claude

> 读取这个 Figma 文件中的 Button 组件：
  https://www.figma.com/design/abc123/Design-System?node-id=123:456

  生成对应的 React + Tailwind CSS 代码
```

**Claude 的处理过程**：

```
正在连接 Figma MCP...
正在读取组件 "Button/Primary"...
提取设计令牌：
  - 背景色: #2563EB (blue-600)
  - 文字色: #FFFFFF
  - 圆角: 6px (rounded-md)
  - 内边距: 10px 16px (py-2.5 px-4)
  - 字体: 14px/600 (text-sm font-semibold)
正在生成代码...
```

**生成结果示例**：

```tsx
// Button.tsx
interface ButtonProps {
  children: React.ReactNode;
  variant?: 'primary' | 'secondary' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  onClick?: () => void;
}

export function Button({
  children,
  variant = 'primary',
  size = 'md',
  disabled = false,
  onClick,
}: ButtonProps) {
  const variants = {
    primary: 'bg-blue-600 text-white hover:bg-blue-700',
    secondary: 'bg-gray-100 text-gray-900 hover:bg-gray-200',
    ghost: 'bg-transparent text-gray-600 hover:bg-gray-100',
  };

  const sizes = {
    sm: 'text-xs py-1.5 px-3',
    md: 'text-sm py-2.5 px-4',
    lg: 'text-base py-3 px-6',
  };

  return (
    <button
      className={`
        inline-flex items-center justify-center
        rounded-md font-semibold transition-colors
        disabled:opacity-50 disabled:cursor-not-allowed
        ${variants[variant]} ${sizes[size]}
      `}
      disabled={disabled}
      onClick={onClick}
    >
      {children}
    </button>
  );
}
```

### 提取整个页面的设计令牌

```bash
> 读取 Figma 文件的 Design Tokens 页面，
  生成对应的 Tailwind 主题配置文件
```

```javascript
// tailwind.config.js（由 Claude 根据 Figma 数据生成）
module.exports = {
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          500: '#3b82f6',
          600: '#2563eb',
          // ... 从 Figma 提取的精确颜色值
        }
      },
      spacing: {
        // ... 从 Figma 间距系统提取
      }
    }
  }
}
```

### 批量生成多个组件

```bash
> 读取 Figma 文件的 Components 页面，
  为所有带 "Card/" 前缀的组件生成 React 代码，
  保存到 src/components/cards/ 目录
```

---

## 与 frontend-design Skill 协作

两者的职责不同，可以配合使用：

| 工具 | 职责 | 适用场景 |
|------|------|---------|
| `frontend-design` Skill | 创意设计、美化 UI | 从零设计，需要创意 |
| Figma MCP | 还原设计稿 | 已有设计稿，需要精确还原 |

**协作工作流**：

```bash
# 步骤 1：使用 frontend-design Skill 创建初稿
> /frontend-design 创建一个现代感的用户仪表盘页面

# 步骤 2：在 Figma 中调整细节

# 步骤 3：用 Figma MCP 精确还原最终设计
> 根据调整后的 Figma 设计稿更新代码：
  https://www.figma.com/design/...
```

---

## 常见问题

### Q1: 需要 Figma 付费版吗？

**A**: 需要 Figma 账号，免费版支持读取个人文件，团队文件需要付费版权限。

### Q2: 支持实时同步吗？

**A**: 目前是按需读取，不支持自动实时同步。每次需要手动触发。

### Q3: 能处理复杂的组件变体吗？

**A**: 可以，Figma MCP 会读取所有变体（Variants）的属性，Claude 可以生成对应的 Props 接口。

### Q4: 对大型设计文件性能如何？

**A**: 大文件建议指定具体的 `node-id` 而不是读取整个文件，避免超时。

---

## 技巧与最佳实践

### 指定具体 Node ID

```bash
# 从 Figma URL 获取 node-id 参数
https://www.figma.com/design/FILE_ID/Name?node-id=123:456
#                                                     ↑ 这个

> 读取 node-id=123:456 的组件
```

### 要求生成设计系统文档

```bash
> 读取 Figma 设计文件，生成完整的组件 API 文档，
  格式参考 Storybook MDX，包含所有 Props 和使用示例
```

### 与 CLAUDE.md 集成

在项目的 `CLAUDE.md` 中记录 Figma 文件链接：

```markdown
## 设计资源
Figma 文件：https://www.figma.com/design/xxx/Design-System
主要页面：
- Components: node-id=1:2
- Tokens: node-id=3:4
- Icons: node-id=5:6
```

---

## 相关工具

- [frontend-design Skill](../official-skills/frontend-design.md) - 创意设计配合使用
- [Fetch MCP Server](./official-mcp-servers.md#fetch) - 抓取 Figma 社区资源

---

**工具版本**: 官方最新
**最后更新**: 2026-02-10
