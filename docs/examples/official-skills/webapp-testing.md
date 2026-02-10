# Skill: webapp-testing

## 概述

`webapp-testing` 是用于与本地 Web 应用进行交互和测试的 Skill，基于 **Playwright** 浏览器自动化框架。它能够验证前端功能、调试 UI 行为、捕获浏览器截图，以及查看浏览器日志。

**核心能力**:
- 控制浏览器自动化测试
- 截图和可视化验证
- 浏览器控制台日志捕获
- 前端功能验证
- 交互式 UI 调试

---

## 触发方式

### 斜杠命令

```bash
/webapp-testing
```

### 自然语言触发

```
"测试这个 Web 应用"
"帮我检查登录页面是否正常工作"
"截一张首页的截图"
"验证表单提交是否成功"
"用 Playwright 测试..."
```

---

## 前置要求

```bash
# 需要本地运行的 Web 应用
npm run dev  # 或 yarn dev / pnpm dev

# 需要安装 Playwright
npm install -D playwright @playwright/test
npx playwright install chromium  # 安装浏览器
```

---

## 工作原理

```
1. 接收测试任务描述
   └─ 明确要测试的功能或页面

2. 启动浏览器
   └─ 通过 Playwright 控制 Chromium/Firefox/Safari

3. 执行操作序列
   ├─ 导航到指定 URL
   ├─ 模拟用户交互（点击、输入、滚动）
   ├─ 等待特定状态
   └─ 捕获截图/日志

4. 分析结果
   ├─ 验证期望状态
   ├─ 报告发现的问题
   └─ 提供修复建议
```

---

## 实际演示

### 示例 1: 表单功能验证

**用户请求**:
```
验证一下注册表单：
1. 所有字段都是必填的
2. 邮箱格式验证有效
3. 提交成功后跳转到 /dashboard
应用运行在 http://localhost:3000
```

**Claude 的处理过程与输出**:

```typescript
// Claude 生成并执行以下 Playwright 测试代码

import { chromium } from 'playwright';

const browser = await chromium.launch({ headless: false }); // 可见模式
const page = await browser.newPage();

// ---- 测试 1: 空表单提交 ----
await page.goto('http://localhost:3000/register');
await page.click('button[type="submit"]');

// 检查验证错误
const nameError = await page.locator('[data-testid="name-error"]').isVisible();
const emailError = await page.locator('[data-testid="email-error"]').isVisible();
const passwordError = await page.locator('[data-testid="password-error"]').isVisible();

console.log('空表单验证:', {
  nameError,    // true ✓
  emailError,   // true ✓
  passwordError // true ✓
});

// ---- 测试 2: 无效邮箱格式 ----
await page.fill('[name="email"]', 'not-an-email');
await page.click('button[type="submit"]');

const emailFormatError = await page.locator('[data-testid="email-error"]').textContent();
console.log('邮箱格式错误消息:', emailFormatError); // "请输入有效的邮箱地址"

// ---- 测试 3: 成功注册 ----
await page.fill('[name="name"]', 'Test User');
await page.fill('[name="email"]', 'test@example.com');
await page.fill('[name="password"]', 'SecurePass123!');
await page.click('button[type="submit"]');

await page.waitForURL('**/dashboard', { timeout: 5000 });
const currentUrl = page.url();
console.log('注册后跳转到:', currentUrl); // http://localhost:3000/dashboard

// 截图
await page.screenshot({ path: 'screenshots/register-success.png' });

await browser.close();
```

**测试报告**:

```
✅ 测试 1: 空表单验证 - 通过
   - 姓名字段显示必填错误 ✓
   - 邮箱字段显示必填错误 ✓
   - 密码字段显示必填错误 ✓

✅ 测试 2: 邮箱格式验证 - 通过
   - 显示"请输入有效的邮箱地址"提示 ✓

✅ 测试 3: 成功注册跳转 - 通过
   - 注册后成功跳转到 /dashboard ✓

截图已保存: screenshots/register-success.png
```

---

### 示例 2: 截图和视觉检查

**用户请求**:
```
截取我们 App 的以下页面截图：
1. 首页（桌面端和移动端）
2. 登录页面
3. 用户资料页面（登录后）

运行在 http://localhost:3000
```

**Claude 生成的截图脚本**:

```typescript
import { chromium } from 'playwright';

const browser = await chromium.launch();
const SCREENSHOTS_DIR = './screenshots';

// 桌面端截图
const desktopPage = await browser.newPage();
await desktopPage.setViewportSize({ width: 1440, height: 900 });

// 1. 首页 - 桌面端
await desktopPage.goto('http://localhost:3000');
await desktopPage.waitForLoadState('networkidle');
await desktopPage.screenshot({
  path: `${SCREENSHOTS_DIR}/home-desktop.png`,
  fullPage: true  // 截取完整页面
});
console.log('✓ 首页桌面端截图完成');

// 2. 移动端视图
const mobilePage = await browser.newPage();
await mobilePage.setViewportSize({ width: 390, height: 844 }); // iPhone 14
await mobilePage.goto('http://localhost:3000');
await mobilePage.screenshot({
  path: `${SCREENSHOTS_DIR}/home-mobile.png`,
  fullPage: true
});
console.log('✓ 首页移动端截图完成');

// 3. 登录页面
await desktopPage.goto('http://localhost:3000/login');
await desktopPage.screenshot({ path: `${SCREENSHOTS_DIR}/login.png` });
console.log('✓ 登录页面截图完成');

// 4. 登录后截取用户资料页
await desktopPage.fill('[name="email"]', 'demo@example.com');
await desktopPage.fill('[name="password"]', 'demo123');
await desktopPage.click('button[type="submit"]');
await desktopPage.waitForURL('**/dashboard');
await desktopPage.goto('http://localhost:3000/profile');
await desktopPage.screenshot({ path: `${SCREENSHOTS_DIR}/profile.png` });
console.log('✓ 用户资料页截图完成');

await browser.close();
console.log('\n所有截图已保存到 ./screenshots/ 目录');
```

**输出结果**:

```
✓ 首页桌面端截图完成 → screenshots/home-desktop.png
✓ 首页移动端截图完成 → screenshots/home-mobile.png
✓ 登录页面截图完成  → screenshots/login.png
✓ 用户资料页截图完成 → screenshots/profile.png

所有截图已保存到 ./screenshots/ 目录
```

---

### 示例 3: 控制台日志捕获

**用户请求**:
```
检查一下商品列表页面的控制台，
看看有没有 JavaScript 错误或者 API 请求失败
```

**Claude 的分析**:

```typescript
import { chromium } from 'playwright';

const browser = await chromium.launch();
const page = await browser.newPage();

// 捕获所有控制台消息
const consoleLogs: { type: string; message: string }[] = [];
page.on('console', (msg) => {
  consoleLogs.push({ type: msg.type(), message: msg.text() });
});

// 捕获网络请求错误
const networkErrors: { url: string; status: number }[] = [];
page.on('response', (response) => {
  if (response.status() >= 400) {
    networkErrors.push({
      url: response.url(),
      status: response.status()
    });
  }
});

// 捕获 JS 错误
const jsErrors: string[] = [];
page.on('pageerror', (error) => {
  jsErrors.push(error.message);
});

await page.goto('http://localhost:3000/products');
await page.waitForLoadState('networkidle');

// 滚动到底部触发懒加载
await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
await page.waitForTimeout(1000);

await browser.close();

// 分析结果
console.log('\n=== 控制台日志分析 ===');

const errors = consoleLogs.filter(l => l.type === 'error');
const warnings = consoleLogs.filter(l => l.type === 'warning');

if (errors.length > 0) {
  console.log(`\n🔴 JavaScript 错误 (${errors.length} 个):`);
  errors.forEach(e => console.log(`  - ${e.message}`));
} else {
  console.log('\n✅ 没有 JavaScript 错误');
}

if (warnings.length > 0) {
  console.log(`\n🟡 警告 (${warnings.length} 个):`);
  warnings.forEach(w => console.log(`  - ${w.message}`));
}

if (networkErrors.length > 0) {
  console.log(`\n🔴 网络请求错误 (${networkErrors.length} 个):`);
  networkErrors.forEach(e => console.log(`  - [${e.status}] ${e.url}`));
} else {
  console.log('✅ 没有网络请求错误');
}

if (jsErrors.length > 0) {
  console.log(`\n🔴 未捕获的 JS 异常 (${jsErrors.length} 个):`);
  jsErrors.forEach(e => console.log(`  - ${e}`));
}
```

**示例输出**:

```
=== 控制台日志分析 ===

🔴 JavaScript 错误 (2 个):
  - Cannot read properties of undefined (reading 'price')
    位置: ProductCard.jsx:45
  - Warning: Each child in a list should have a unique "key" prop.

✅ 没有网络请求错误

发现 2 个问题，建议修复：

1. ProductCard.jsx:45 - 访问 undefined 对象的 price 属性
   可能原因：API 返回的商品数据中 price 字段为空
   建议修复：添加可选链 `product?.price ?? 0`

2. React key 警告
   需要为列表中的每个元素添加唯一的 key 属性
```

---

### 示例 4: 端到端测试场景

**用户请求**:
```
测试完整的购物流程：
1. 浏览商品
2. 添加到购物车
3. 结账
4. 验证订单确认页面
```

**Claude 生成的 E2E 测试**:

```typescript
import { test, expect } from '@playwright/test';

test.describe('购物流程 E2E 测试', () => {
  test('完整购物流程', async ({ page }) => {
    // 1. 浏览商品
    await page.goto('/products');
    await expect(page).toHaveTitle(/商品列表/);

    const firstProduct = page.locator('.product-card').first();
    const productName = await firstProduct.locator('h3').textContent();
    console.log(`选择商品: ${productName}`);

    // 2. 添加到购物车
    await firstProduct.locator('button[aria-label="加入购物车"]').click();

    // 等待购物车图标数量更新
    await expect(page.locator('[data-testid="cart-count"]'))
      .toHaveText('1');

    // 3. 前往购物车
    await page.click('[data-testid="cart-icon"]');
    await expect(page).toHaveURL('/cart');
    await expect(page.locator('.cart-item')).toHaveCount(1);

    // 4. 结账
    await page.click('button:has-text("去结账")');
    await expect(page).toHaveURL('/checkout');

    // 填写收货信息
    await page.fill('[name="name"]', '张三');
    await page.fill('[name="phone"]', '13800138000');
    await page.fill('[name="address"]', '北京市朝阳区测试街道1号');

    // 选择支付方式
    await page.click('[data-value="alipay"]');

    // 提交订单
    await page.click('button:has-text("提交订单")');

    // 5. 验证订单确认
    await page.waitForURL('/order-confirm/**');
    await expect(page.locator('h1')).toContainText('订单提交成功');
    await expect(page.locator('[data-testid="order-number"]')).toBeVisible();

    // 截图存档
    await page.screenshot({
      path: 'screenshots/order-confirm.png',
      fullPage: true
    });
  });
});
```

---

## 常用操作参考

### 页面导航

```typescript
// 导航到 URL
await page.goto('http://localhost:3000/path');

// 等待页面加载完成
await page.waitForLoadState('networkidle');

// 等待跳转
await page.waitForURL('**/success');
```

### 元素交互

```typescript
// 点击元素
await page.click('button[type="submit"]');
await page.click('text=登录');

// 输入文本
await page.fill('[name="email"]', 'user@example.com');
await page.type('[name="search"]', 'keyword'); // 模拟键盘逐个输入

// 选择下拉菜单
await page.selectOption('select[name="category"]', 'electronics');

// 勾选复选框
await page.check('[name="agree"]');

// 上传文件
await page.setInputFiles('[name="avatar"]', './test-image.jpg');
```

### 断言验证

```typescript
// URL 断言
await expect(page).toHaveURL('/dashboard');

// 文本断言
await expect(page.locator('h1')).toHaveText('欢迎回来');
await expect(page.locator('.message')).toContainText('成功');

// 可见性断言
await expect(page.locator('.error-msg')).toBeVisible();
await expect(page.locator('.loading')).toBeHidden();

// 属性断言
await expect(page.locator('button')).toBeDisabled();
await expect(page.locator('input')).toHaveValue('test@example.com');
```

### 等待策略

```typescript
// 等待元素出现
await page.waitForSelector('.product-list');

// 等待特定文本
await page.waitForSelector('text=加载完成');

// 等待网络请求
await page.waitForResponse('**/api/products');

// 自定义等待
await page.waitForFunction(() => {
  return document.querySelectorAll('.product-card').length > 0;
});
```

---

## 与 CI/CD 集成

### GitHub Actions 配置

```yaml
# .github/workflows/e2e.yml
name: E2E Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Install dependencies
        run: npm ci

      - name: Install Playwright
        run: npx playwright install --with-deps chromium

      - name: Start dev server
        run: npm run dev &
        env:
          PORT: 3000

      - name: Wait for server
        run: npx wait-on http://localhost:3000 --timeout 30000

      - name: Run E2E Tests with Claude
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          claude --print "测试 http://localhost:3000 的登录和注册功能"

      - name: Upload screenshots
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: screenshots
          path: screenshots/
```

---

## 常见问题

### Q1: 需要安装什么依赖？

**A**: 需要 Playwright：

```bash
npm install -D playwright
npx playwright install chromium
```

### Q2: 如何测试需要登录的页面？

**A**: 可以使用 Playwright 的 `storageState` 保存登录状态：

```typescript
// 先登录并保存状态
await page.goto('/login');
await page.fill('[name="email"]', 'test@example.com');
await page.fill('[name="password"]', 'password');
await page.click('button[type="submit"]');
await page.context().storageState({ path: 'auth.json' });
```

或者直接告诉 Claude：

```bash
> 测试用户资料页面，先用 test@example.com/password123 登录
```

### Q3: 支持测试 API 接口吗？

**A**: webapp-testing 主要针对 UI 测试，API 测试建议使用 HTTP 示例或专门的 API 测试工具。但可以验证 API 调用的结果是否正确反映在 UI 上。

### Q4: 如何处理异步加载的内容？

**A**: 使用等待策略：

```bash
> 商品列表是异步加载的，等待列表出现后再进行测试
```

Claude 会自动使用合适的等待策略。

---

## 最佳实践

### 1. 明确描述测试场景

```bash
# 好的描述
> 测试用户登录流程：
  1. 访问 /login
  2. 输入正确的邮箱和密码
  3. 验证跳转到 /dashboard
  4. 验证导航栏显示用户名

# 模糊的描述（效果较差）
> 测试登录
```

### 2. 使用 data-testid 属性

在组件中添加测试 ID，让测试更稳定：

```tsx
// 组件代码
<button data-testid="submit-btn" type="submit">登录</button>
<div data-testid="error-message">{error}</div>
```

```bash
> 点击 data-testid 为 "submit-btn" 的按钮，
  然后检查 data-testid 为 "error-message" 的元素内容
```

### 3. 截图存档

```bash
> 在每个关键步骤后截图，保存到 screenshots/ 目录
```

---

## 相关 Skills

- [code-review](./code-review.md) - 审查测试代码
- [frontend-design](./frontend-design.md) - 创建被测试的组件

---

**Skill 版本**: 内置
**最后更新**: 2026-02-10
