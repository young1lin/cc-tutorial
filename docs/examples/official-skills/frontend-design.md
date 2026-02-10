# Skill: frontend-design

## 概述

`frontend-design` 是 Claude Code 内置的前端界面设计 Skill，专门用于创建高质量、有独特风格的前端界面。它避免了 AI 生成代码常见的"平庸感"，能够生成具有专业设计品质的 Web 组件、页面和应用程序。

**核心能力**:
- 生成视觉精美的 UI 组件
- 创建完整的 Web 页面和应用
- 提供 React、HTML/CSS 等多种框架的实现
- 避免通用 AI 美学，创造独特设计

---

## 触发方式

### 斜杠命令

```bash
/frontend-design
/frontend-design:frontend-design
```

### 自然语言触发

以下描述会触发 frontend-design skill：

```
"创建一个产品卡片组件"
"设计一个登录页面"
"构建一个数据仪表盘"
"美化这个表单"
"做一个着陆页"
"build a React component for..."
"create a landing page for..."
```

---

## 工作原理

```
1. 理解设计需求
   ├─ 组件类型（卡片、表单、仪表盘等）
   ├─ 品牌风格（颜色、字体偏好）
   ├─ 交互要求（动画、响应式等）
   └─ 技术栈（React、Vue、纯 HTML 等）

2. 制定设计方案
   ├─ 色彩方案
   ├─ 排版选择
   ├─ 布局结构
   └─ 交互模式

3. 生成代码
   ├─ 编写组件代码
   ├─ 添加样式（CSS/Tailwind/Styled-components）
   └─ 实现交互逻辑

4. 优化细节
   ├─ 响应式适配
   ├─ 可访问性
   └─ 浏览器兼容性
```

---

## 实际演示

### 示例 1: 产品卡片组件

**用户请求**:
```
创建一个产品卡片组件，包含：
- 产品图片
- 标题和简短描述
- 价格（支持原价/折扣价）
- 添加到购物车按钮
- 悬停效果
```

**生成结果**（React + Tailwind CSS）:

```tsx
// ProductCard.tsx
import React, { useState } from 'react';

interface ProductCardProps {
  image: string;
  title: string;
  description: string;
  price: number;
  originalPrice?: number;
  onAddToCart: (id: string) => void;
  id: string;
}

export const ProductCard: React.FC<ProductCardProps> = ({
  image,
  title,
  description,
  price,
  originalPrice,
  onAddToCart,
  id,
}) => {
  const [isAdding, setIsAdding] = useState(false);

  const discount = originalPrice
    ? Math.round(((originalPrice - price) / originalPrice) * 100)
    : null;

  const handleAddToCart = async () => {
    setIsAdding(true);
    await onAddToCart(id);
    setTimeout(() => setIsAdding(false), 1000);
  };

  return (
    <div className="group relative bg-white rounded-2xl overflow-hidden shadow-sm hover:shadow-xl transition-all duration-300 hover:-translate-y-1">
      {/* Image Container */}
      <div className="relative overflow-hidden bg-gray-50 aspect-square">
        <img
          src={image}
          alt={title}
          className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
        />
        {discount && (
          <div className="absolute top-3 left-3 bg-rose-500 text-white text-xs font-bold px-2 py-1 rounded-full">
            -{discount}%
          </div>
        )}
      </div>

      {/* Content */}
      <div className="p-4 space-y-3">
        <div>
          <h3 className="font-semibold text-gray-900 text-sm leading-tight line-clamp-1">
            {title}
          </h3>
          <p className="text-gray-500 text-xs mt-1 line-clamp-2">
            {description}
          </p>
        </div>

        {/* Price */}
        <div className="flex items-baseline gap-2">
          <span className="text-lg font-bold text-gray-900">
            ¥{price.toFixed(2)}
          </span>
          {originalPrice && (
            <span className="text-sm text-gray-400 line-through">
              ¥{originalPrice.toFixed(2)}
            </span>
          )}
        </div>

        {/* Add to Cart Button */}
        <button
          onClick={handleAddToCart}
          disabled={isAdding}
          className={`
            w-full py-2.5 rounded-xl text-sm font-medium
            transition-all duration-200
            ${isAdding
              ? 'bg-green-500 text-white scale-95'
              : 'bg-gray-900 text-white hover:bg-gray-700 active:scale-95'
            }
          `}
        >
          {isAdding ? '✓ 已添加' : '加入购物车'}
        </button>
      </div>
    </div>
  );
};
```

```css
/* 如果不使用 Tailwind，对应的 CSS */
.product-card {
  position: relative;
  background: white;
  border-radius: 1rem;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  transition: all 0.3s ease;
}

.product-card:hover {
  box-shadow: 0 20px 40px rgba(0,0,0,0.15);
  transform: translateY(-4px);
}
```

---

### 示例 2: 数据仪表盘

**用户请求**:
```
创建一个 SaaS 数据仪表盘，显示：
- 核心指标卡（用户数、收入、转化率、活跃率）
- 折线图（7 天趋势）
- 最近交易列表
- 侧边导航栏
```

**生成结果概览**:

```tsx
// Dashboard.tsx - 主结构
export const Dashboard = () => {
  return (
    <div className="flex h-screen bg-gray-950 text-gray-100">
      {/* 侧边栏 */}
      <Sidebar />

      {/* 主内容区 */}
      <main className="flex-1 overflow-y-auto">
        {/* 顶栏 */}
        <Header />

        {/* 内容网格 */}
        <div className="p-6 space-y-6">
          {/* 指标卡 */}
          <div className="grid grid-cols-4 gap-4">
            <MetricCard
              title="总用户数"
              value="24,521"
              change="+12.5%"
              trend="up"
              icon={<UsersIcon />}
            />
            <MetricCard
              title="月收入"
              value="¥128,430"
              change="+8.2%"
              trend="up"
              icon={<RevenueIcon />}
            />
            <MetricCard
              title="转化率"
              value="3.24%"
              change="-0.4%"
              trend="down"
              icon={<ConversionIcon />}
            />
            <MetricCard
              title="活跃用户"
              value="8,820"
              change="+5.7%"
              trend="up"
              icon={<ActivityIcon />}
            />
          </div>

          {/* 图表 + 列表 */}
          <div className="grid grid-cols-3 gap-4">
            <div className="col-span-2">
              <TrendChart />
            </div>
            <RecentTransactions />
          </div>
        </div>
      </main>
    </div>
  );
};

// MetricCard 组件
const MetricCard = ({ title, value, change, trend, icon }) => (
  <div className="bg-gray-900 rounded-2xl p-5 border border-gray-800">
    <div className="flex justify-between items-start mb-4">
      <div className="p-2 bg-gray-800 rounded-xl text-blue-400">
        {icon}
      </div>
      <span className={`text-sm font-medium ${
        trend === 'up' ? 'text-emerald-400' : 'text-rose-400'
      }`}>
        {change}
      </span>
    </div>
    <p className="text-3xl font-bold text-white">{value}</p>
    <p className="text-sm text-gray-400 mt-1">{title}</p>
  </div>
);
```

---

### 示例 3: 着陆页

**用户请求**:
```
为一个 AI 写作工具创建着陆页，需要：
- 英雄区（Hero Section）
- 功能特点展示
- 定价表格
- CTA 按钮
- 现代、专业的设计风格
```

**生成的 Hero Section**:

```tsx
// HeroSection.tsx
export const HeroSection = () => {
  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden bg-[#0a0a0f]">
      {/* 渐变背景 */}
      <div className="absolute inset-0">
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-violet-600/20 rounded-full blur-[120px]" />
        <div className="absolute bottom-1/4 right-1/4 w-[400px] h-[400px] bg-blue-600/15 rounded-full blur-[100px]" />
      </div>

      {/* 网格背景 */}
      <div
        className="absolute inset-0 opacity-[0.02]"
        style={{
          backgroundImage: `linear-gradient(rgba(255,255,255,.1) 1px, transparent 1px),
                            linear-gradient(90deg, rgba(255,255,255,.1) 1px, transparent 1px)`,
          backgroundSize: '40px 40px',
        }}
      />

      {/* 内容 */}
      <div className="relative z-10 text-center max-w-5xl mx-auto px-4">
        {/* 标签 */}
        <div className="inline-flex items-center gap-2 bg-white/5 border border-white/10 rounded-full px-4 py-1.5 mb-8 text-sm text-gray-400">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          现已开放公测
        </div>

        {/* 标题 */}
        <h1 className="text-6xl sm:text-7xl font-black text-white mb-6 leading-tight tracking-tight">
          让 AI 为你
          <br />
          <span className="bg-gradient-to-r from-violet-400 via-pink-400 to-blue-400 bg-clip-text text-transparent">
            书写一切
          </span>
        </h1>

        {/* 副标题 */}
        <p className="text-xl text-gray-400 max-w-2xl mx-auto mb-10 leading-relaxed">
          融合最新 AI 技术，一键生成高质量文章、营销文案、技术文档。
          告别写作困境，专注创意本身。
        </p>

        {/* CTA 按钮组 */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <button className="group relative px-8 py-4 bg-violet-600 hover:bg-violet-500 rounded-2xl text-white font-semibold transition-all duration-200 hover:scale-105">
            免费开始使用
            <span className="ml-2 group-hover:translate-x-1 inline-block transition-transform">→</span>
          </button>
          <button className="px-8 py-4 bg-white/5 hover:bg-white/10 border border-white/10 rounded-2xl text-white font-semibold transition-all duration-200">
            观看演示
          </button>
        </div>

        {/* 社会证明 */}
        <div className="mt-16 flex items-center justify-center gap-8 text-gray-500 text-sm">
          <span>已有 10,000+ 用户信赖</span>
          <span>·</span>
          <span>4.9/5 用户评分</span>
          <span>·</span>
          <span>无需信用卡</span>
        </div>
      </div>
    </section>
  );
};
```

---

## 支持的输出格式

### React + Tailwind CSS（推荐）

最常用的现代 Web 开发栈：

```bash
> 用 React 和 Tailwind CSS 创建一个 [组件名]
```

### 原生 HTML/CSS

不依赖框架：

```bash
> 用纯 HTML 和 CSS 创建一个 [组件名]
```

### Next.js 组件

适用于 Next.js 项目：

```bash
> 为 Next.js 项目创建一个 [页面名] 页面
```

### CSS 模块

```bash
> 使用 CSS Modules 创建一个 [组件名]
```

---

## 设计风格指南

### 如何获得最佳结果

在请求中描述设计风格会显著提升输出质量：

```bash
# 描述配色
> 创建一个深色主题（dark mode）的数据仪表盘

# 描述风格
> 创建一个极简风格的登录页面，类似 Linear 或 Vercel 的设计

# 描述受众
> 为儿童教育平台创建一个活泼、色彩丰富的课程卡片组件

# 描述品牌
> 为银行 App 创建一个专业、可信赖感强的首页，主色调为深蓝色
```

### 常见风格关键词

| 风格 | 关键词 |
|------|--------|
| 现代极简 | minimal, clean, modern, Linear-style |
| 玻璃拟态 | glassmorphism, frosted glass, blur |
| 新拟态 | neumorphism, soft shadows |
| 暗色主题 | dark mode, dark theme, night mode |
| 活泼多彩 | colorful, vibrant, playful |
| 专业商务 | professional, corporate, trustworthy |
| 渐变风格 | gradient, aurora, colorful |

---

## 高级功能

### 1. 动画效果

```bash
> 创建一个带流畅动画的 [组件名]
> 添加悬停动画效果
> 使用 Framer Motion 添加页面过渡动画
```

### 2. 响应式设计

```bash
> 确保在手机端也能完美显示
> 创建移动优先（Mobile First）的设计
```

### 3. 暗色/亮色模式切换

```bash
> 同时支持暗色和亮色模式，用 CSS 变量实现
```

### 4. 可访问性

```bash
> 确保符合 WCAG 2.1 AA 标准
> 添加适当的 ARIA 属性
```

### 5. 交互状态

```bash
> 包含所有交互状态：默认、悬停、点击、禁用、加载中
```

---

## 实战工作流

### 1. 快速原型

```bash
> 快速创建一个 [功能] 的原型，不需要完美，先看看整体布局
```

### 2. 迭代优化

```bash
# 第一轮：基础结构
> 创建一个用户资料页面

# 第二轮：优化设计
> 这个设计太普通了，让它更有高级感

# 第三轮：添加功能
> 添加头像上传功能
```

### 3. 从设计图到代码

```bash
# 提供截图描述
> 参考这个截图的设计风格，创建一个类似的 [组件名]
```

---

## 常见问题

### Q1: 可以为现有组件添加样式吗？

**A**: 可以！

```bash
> 这是我现有的 Button 组件代码，帮我美化它：
[粘贴代码]
```

### Q2: 支持 Vue/Svelte/Angular 吗？

**A**: 支持！明确指定框架即可：

```bash
> 用 Vue 3 创建一个 [组件名]
> 用 Svelte 创建一个 [组件名]
```

### Q3: 如何确保生成的代码能直接在项目中使用？

**A**: 在 `CLAUDE.md` 中描述你的技术栈：

```markdown
# CLAUDE.md

## 技术栈
- 框架: React 18
- 样式: Tailwind CSS v3
- 状态管理: Zustand
- 动画: Framer Motion

## 设计规范
- 颜色主题: 见 tailwind.config.js
- 字体: Inter
- 圆角: rounded-xl (12px)
- 间距: 4px 基础单位
```

### Q4: 生成的组件包含哪些内容？

**A**: 通常包括：
- 完整的 TypeScript/JSX 代码
- 样式代码（CSS/Tailwind）
- Props 类型定义
- 基础的交互逻辑
- 可选的 Storybook story

---

## 与其他 Skills 协作

### frontend-design + webapp-testing

```bash
# 创建组件后立即测试
> 创建一个登录表单组件，然后用 Playwright 编写测试
```

### frontend-design + code-review

```bash
# 创建组件后进行代码审查
> 创建一个用户列表组件，生成后帮我 review 一下代码质量
```

---

**Skill 版本**: 内置
**最后更新**: 2026-02-10
