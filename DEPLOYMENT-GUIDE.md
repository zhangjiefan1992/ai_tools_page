# Pick My AI 部署与配置完整指南

> 本指南涵盖从环境配置到正式上线的所有步骤，请按顺序完成各部分配置。

---

## 目录

1. [Google Analytics 4 配置指南](#part-1-google-analytics-4-配置指南)
2. [Google AdSense 配置指南](#part-2-google-adsense-配置指南)
3. [环境变量配置](#part-3-环境变量配置)
4. [Vercel 部署步骤](#part-4-vercel-部署步骤)
5. [域名配置](#part-5-域名配置)
6. [GEO 优化已完成事项](#part-6-geo-优化已完成事项)
7. [内容扩展建议](#part-7-内容扩展建议)
8. [上线前检查清单](#part-8-上线前检查清单)

---

## Part 1: Google Analytics 4 配置指南

### 1.1 创建 GA4 属性

1. 访问 [Google Analytics](https://analytics.google.com/)，使用 Google 账号登录
2. 点击左下角 **管理（Admin）** 齿轮图标
3. 在「属性」列中点击 **创建属性（Create Property）**
4. 填写属性名称：`Pick My AI`
5. 选择报告时区和货币
6. 点击 **下一步**，选择行业类别为「技术」，企业规模选「小型」
7. 选择业务目标（勾选「获取流量报告」和「了解用户行为」）
8. 点击 **创建**

### 1.2 设置数据流（Data Stream）

1. 在属性创建完成后，选择 **Web** 平台
2. 输入网站 URL（例如：`https://pick-my-ai.com`）
3. 输入数据流名称：`Pick My AI - Web`
4. 点击 **创建数据流**

### 1.3 获取 Measurement ID

1. 创建数据流后，页面会显示 **衡量 ID（Measurement ID）**
2. 格式为 `G-XXXXXXXXXX`（以 G- 开头，后跟 10 位字母数字）
3. **复制此 ID**，后续配置环境变量时需要使用

### 1.4 在项目中配置

编辑项目根目录的 `.env` 文件：

```bash
PUBLIC_GA_ID=G-XXXXXXXXXX
```

将 `G-XXXXXXXXXX` 替换为你在上一步获取的真实 Measurement ID。

---

## Part 2: Google AdSense 配置指南

### 2.1 申请 Google AdSense 账号

1. 访问 [Google AdSense](https://www.google.com/adsense/)
2. 使用 Google 账号登录
3. 填写网站 URL 和付款地址信息
4. 提交申请

### 2.2 AdSense 审核要求

在提交申请前，确保网站满足以下条件：

| 要求 | 说明 |
|------|------|
| 内容数量 | 至少 **15-20 篇**高质量原创文章 |
| 隐私政策 | 必须有可访问的 `/privacy-policy` 页面 ✅ 已创建 |
| 关于页面 | 必须有 `/about` 页面说明网站用途 ✅ 已创建 |
| 导航结构 | 清晰的网站导航和分类结构 ✅ 已配置 |
| 内容质量 | 原创、有价值、非抄袭的内容 |
| 网站年龄 | 部分地区要求域名注册满 6 个月 |
| 合规内容 | 不包含成人、暴力、赌博等违禁内容 |

> ⚠️ **重要提示**：当前项目仅有 3 篇文章，需要扩充至 15-20 篇后再提交 AdSense 申请。详见 [Part 7: 内容扩展建议](#part-7-内容扩展建议)。

### 2.3 审核通过后获取配置信息

审核通过后，登录 AdSense 后台获取以下信息：

#### Publisher ID
1. 登录 AdSense → 点击 **账号（Account）** → **账号信息**
2. 找到「发布商 ID」，格式为 `ca-pub-XXXXXXXXXXXXXXXX`

#### 广告单元 Slot ID
1. 在 AdSense 后台 → **广告（Ads）** → **按广告单元（By ad unit）**
2. 创建 **文章内嵌广告（In-article ad）**：
   - 命名为 `Pick My AI - In Article`
   - 创建后获得 Slot ID（纯数字，如 `1234567890`）
3. 创建 **展示广告（Display ad）**：
   - 命名为 `Pick My AI - Display`
   - 选择「响应式」尺寸
   - 创建后获得 Slot ID（纯数字，如 `0987654321`）

### 2.4 在项目中配置

编辑 `.env` 文件，设置 3 个 AdSense 变量：

```bash
PUBLIC_ADSENSE_CLIENT=ca-pub-XXXXXXXXXXXXXXXX
PUBLIC_ADSENSE_IN_ARTICLE_SLOT=1234567890
PUBLIC_ADSENSE_DISPLAY_SLOT=0987654321
```

### 2.5 更新 ads.txt

编辑 `public/ads.txt`，将占位符替换为真实 Publisher ID：

```
google.com, pub-XXXXXXXXXXXXXXXX, DIRECT, f08c47fec0942fa0
```

将 `pub-XXXXXXXXXXXXXXXX` 替换为你的真实 Publisher ID（去掉 `ca-` 前缀，只保留 `pub-` 部分）。

---

## Part 3: 环境变量配置

### 3.1 完整 `.env` 文件模板

在项目根目录创建 `.env` 文件（基于 `.env.example`）：

```bash
# Google Analytics 4
# 获取方式：Google Analytics 后台 → 管理 → 数据流 → 衡量 ID
# 格式：G- 开头，后跟 10 位字母数字
PUBLIC_GA_ID=G-XXXXXXXXXX

# Google AdSense
# 获取方式：AdSense 后台 → 账号 → 账号信息 → 发布商 ID
# 格式：ca-pub- 开头，后跟 16 位数字
PUBLIC_ADSENSE_CLIENT=ca-pub-XXXXXXXXXXXXXXXX

# 获取方式：AdSense 后台 → 广告 → 按广告单元 → 文章内嵌广告 Slot ID
# 格式：纯数字
PUBLIC_ADSENSE_IN_ARTICLE_SLOT=1234567890

# 获取方式：AdSense 后台 → 广告 → 按广告单元 → 展示广告 Slot ID
# 格式：纯数字
PUBLIC_ADSENSE_DISPLAY_SLOT=0987654321

# 网站 URL（用于 sitemap、RSS、canonical URLs）
# 格式：完整 URL，不带末尾斜杠
SITE_URL=https://pick-my-ai.com
```

### 3.2 本地开发 vs Vercel 部署对比

| 配置方式 | 本地开发 | Vercel 部署 |
|---------|---------|------------|
| 配置文件 | 项目根目录 `.env` 文件 | Vercel 控制台 → Settings → Environment Variables |
| 是否提交 Git | ❌ 不提交（已在 .gitignore 中） | ✅ 在 Vercel 控制台配置 |
| 生效时机 | 重启 `npm run dev` 后生效 | 下次部署自动生效 |
| 环境区分 | 单一 `.env` 文件 | 可分别设置 Production / Preview / Development |

> ⚠️ **注意**：`.env` 文件不应提交到 Git 仓库。确保 `.gitignore` 中包含 `.env`。

---

## Part 4: Vercel 部署步骤

### 4.1 创建 GitHub 仓库并推送代码

```bash
# 在项目根目录执行
git init
git add .
git commit -m "Initial commit: Pick My AI"

# 在 GitHub 上创建新仓库（名称建议：pick-my-ai）
# 然后关联远程仓库
git remote add origin https://github.com/YOUR_USERNAME/pick-my-ai.git
git branch -M main
git push -u origin main
```

### 4.2 连接 Vercel 项目

1. 访问 [Vercel Dashboard](https://vercel.com/dashboard)
2. 点击 **Add New...** → **Project**
3. 选择 **Import Git Repository**，找到 `pick-my-ai` 仓库
4. 点击 **Import**

### 4.3 配置构建设置

Vercel 会自动检测 Astro 框架，确认以下设置：

| 设置项 | 值 |
|--------|-----|
| Framework Preset | Astro |
| Build Command | `npm run build` |
| Output Directory | `dist` |
| Install Command | `npm install` |

### 4.4 配置环境变量

在 Vercel 项目设置中：

1. 进入 **Settings** → **Environment Variables**
2. 逐一添加以下变量：

| Variable Name | Value | Environment |
|--------------|-------|-------------|
| `PUBLIC_GA_ID` | `G-XXXXXXXXXX` | Production, Preview |
| `PUBLIC_ADSENSE_CLIENT` | `ca-pub-XXXXXXXXXXXXXXXX` | Production |
| `PUBLIC_ADSENSE_IN_ARTICLE_SLOT` | `1234567890` | Production |
| `PUBLIC_ADSENSE_DISPLAY_SLOT` | `0987654321` | Production |
| `SITE_URL` | `https://pick-my-ai.com` | Production, Preview |

3. 点击 **Save** 保存

### 4.5 部署

1. 添加环境变量后，点击 **Deployments** 标签
2. 找到最新部署，点击 **Redeploy** 使环境变量生效
3. 等待构建完成，Vercel 会提供一个 `.vercel.app` 的预览 URL

### 4.6 自定义域名配置（可选）

1. 在 Vercel 项目中进入 **Settings** → **Domains**
2. 输入你的域名（如 `pick-my-ai.com`）并点击 **Add**
3. Vercel 会提供 DNS 配置指引

### 4.7 DNS CNAME 设置

在你的域名注册商（如 Cloudflare、Namecheap、GoDaddy）的 DNS 管理中添加：

| 记录类型 | 主机名 | 值 | TTL |
|---------|--------|-----|-----|
| CNAME | `@` 或 `www` | `cname.vercel-dns.com` | Auto |
| CNAME | `www` | `cname.vercel-dns.com` | Auto |

或者使用 A 记录（如果不支持根域名 CNAME）：

| 记录类型 | 主机名 | 值 | TTL |
|---------|--------|-----|-----|
| A | `@` | `76.76.21.21` | Auto |

> DNS 生效通常需要几分钟到 48 小时，期间可通过 Vercel 控制台查看域名验证状态。

---

## Part 5: 域名配置

当你拥有正式域名后，需要在以下位置更新域名：

### 5.1 更新 `public/robots.txt`

将文件中的 `pick-my-ai.com` 替换为真实域名：

```
Sitemap: https://pick-my-ai.com/sitemap-index.xml
```

### 5.2 更新 `astro.config.mjs`

修改 site 配置的默认值：

```javascript
site: process.env.SITE_URL || 'https://pick-my-ai.com',
```

### 5.3 更新 `src/config.ts`

修改 SITE 对象中的 url 和 email：

```typescript
export const SITE = {
  name: 'Pick My AI',
  description: 'Honest reviews, tutorials, and comparisons of the best AI tools to boost your productivity.',
  url: 'https://pick-my-ai.com',
  author: 'Pick My AI Team',
  email: 'contact@pick-my-ai.com',
  language: 'en',
} as const;
```

### 5.4 更新 `.env` 文件

```bash
SITE_URL=https://pick-my-ai.com
```

> 注意：以上示例中的 `pick-my-ai.com` 需替换为你的真实域名。

---

## Part 6: GEO 优化已完成事项

### 6.1 已创建的 GEO 文件

| 文件 | 路径 | 说明 |
|------|------|------|
| llms.txt | `public/llms.txt` | 精简版 AI 搜索引擎内容清单，遵循 [llmstxt.org](https://llmstxt.org/) 规范 |
| llms-full.txt | `public/llms-full.txt` | 扩展版，包含详细 FAQ、工具对比矩阵、参数参考表 |

### 6.2 llms.txt 包含内容

- 品牌实体描述（Brand Entity）
- 4 个核心内容分类及链接
- 3 篇支柱文章的详细摘要
- 关键事实清单
- 站点导航信息

### 6.3 llms-full.txt 额外包含

- 完整的品牌方法论和权威信号
- 10 款 AI 写作工具对比矩阵（含定价）
- ChatGPT vs Claude 8 维度对比表
- Midjourney 5 参数参考表
- 12 个自然语言 FAQ（符合 GEO Answer-First 原则）
- 完整 URL 目录
- 内容新鲜度指标

### 6.4 建议后续 GEO 增强

以下 Schema 标记建议在后续迭代中添加：

| Schema 类型 | 用途 | 建议添加位置 |
|------------|------|------------|
| FAQPage Schema | 帮助 AI 搜索提取问答对 | 每篇支柱文章底部 |
| Review Schema | 结构化工具评分数据 | Reviews 分类文章 |
| HowTo Schema | 教程步骤结构化 | Tutorials 分类文章 |
| Article Schema | 文章元数据标记 | 所有博客文章（已部分实现） |
| Breadcrumb Schema | 面包屑导航结构化 | 全站导航（已实现） |

---

## Part 7: 内容扩展建议

### 7.1 AdSense 审核前的文章需求

- **当前文章数**：3 篇
- **最低要求**：15-20 篇高质量原创文章
- **还需补充**：至少 12-17 篇

### 7.2 建议的文章主题清单

#### Reviews 分类（评测类）

1. **Jasper AI Review 2026: Is It Worth $49/Month for Marketing Teams?**
2. **Grammarly Premium Review: AI-Powered Writing Enhancement Beyond Grammar**
3. **Notion AI Review: How Good Is the Built-In AI Assistant?**
4. **Copy.ai Review 2026: Automating Sales Copy and Marketing Workflows**
5. **Writesonic Review: AI Content Generation for SEO-Focused Bloggers**

#### Comparisons 分类（对比类）

6. **Jasper vs Copy.ai: Which AI Marketing Tool Delivers Better ROI?**
7. **Grammarly vs Wordtune: Best AI Writing Enhancement Tool Compared**
8. **Midjourney vs DALL-E 3: AI Image Generation Head-to-Head**
9. **Notion AI vs ChatGPT: Which AI Assistant Fits Your Workflow?**
10. **Rytr vs Writesonic: Best Budget AI Writing Tool for Beginners**

#### Tutorials 分类（教程类）

11. **How to Use ChatGPT for Content Marketing: A Complete Guide**
12. **Getting Started with Claude: Advanced Prompting Techniques**
13. **How to Build an AI-Powered Writing Workflow in 2026**
14. **Mastering Jasper AI: Brand Voice Training Step-by-Step**
15. **How to Use AI Tools for SEO Content Optimization**

#### Best-of 分类（榜单类）

16. **5 Best AI Image Generators in 2026: Beyond Midjourney**
17. **7 Best Free AI Tools for Students and Educators**
18. **8 Best AI Tools for Small Business Owners in 2026**
19. **6 Best AI Coding Assistants: GitHub Copilot, Cursor, and More**
20. **Top 5 AI Presentation Tools to Replace PowerPoint in 2026**

### 7.3 每篇文章的 SEO 要求

| 要求 | 标准 |
|------|------|
| 字数 | 至少 800 词，建议 1,500-2,500 词 |
| 标题结构 | 1 个 H1（文章标题），3+ 个 H2 段落 |
| Frontmatter | 必须包含 title、description、pubDate、category、tags、image |
| 图片 | 每篇至少 1 张特色图片（featured image） |
| 内部链接 | 每篇包含 2-3 个指向其他文章的内链 |
| Meta Description | 120-160 字符，包含主要关键词 |
| URL Slug | 简短、包含关键词、使用连字符分隔 |

### 7.4 Frontmatter 模板

```yaml
---
title: "文章标题"
description: "120-160字符的Meta描述"
pubDate: 2026-04-26
updatedDate: 2026-04-26
category: "review"  # review / comparison / tutorial / best-of
tags: ["ai-tools", "relevant-tag"]
image: "/images/article-slug.webp"
imageAlt: "图片描述文字"
draft: false
---
```

---

## Part 8: 上线前检查清单

### 环境与配置

- [ ] `.env` 文件已创建并配置所有 5 个环境变量
- [ ] `PUBLIC_GA_ID` 已填入真实 GA4 Measurement ID
- [ ] `PUBLIC_ADSENSE_CLIENT` 已填入真实 Publisher ID
- [ ] `PUBLIC_ADSENSE_IN_ARTICLE_SLOT` 已填入真实 Slot ID
- [ ] `PUBLIC_ADSENSE_DISPLAY_SLOT` 已填入真实 Slot ID
- [ ] `SITE_URL` 已填入真实域名

### 域名相关

- [ ] `public/robots.txt` 中的域名已从 `pick-my-ai.com` 更新为真实域名
- [ ] `public/ads.txt` 中的 Publisher ID 已更新为真实 ID
- [ ] `astro.config.mjs` 中 site URL 已更新
- [ ] `src/config.ts` 中 `SITE.url` 已更新为真实域名
- [ ] `src/config.ts` 中 `SITE.email` 已更新为真实邮箱

### 构建与部署

- [ ] `npm run build` 本地构建成功，无错误
- [ ] 已创建 GitHub 仓库并推送代码
- [ ] Vercel 已连接 GitHub 仓库
- [ ] Vercel 环境变量已配置（5 个变量）
- [ ] Vercel 首次部署成功

### 域名与 DNS

- [ ] 自定义域名已在 Vercel 添加（可选）
- [ ] DNS CNAME 记录已配置指向 `cname.vercel-dns.com`
- [ ] SSL 证书已自动签发（Vercel 自动处理）
- [ ] `www` 和根域名均可访问

### GEO 优化

- [ ] `public/llms.txt` 已创建 ✅
- [ ] `public/llms-full.txt` 已创建 ✅
- [ ] SEO Head 组件已配置 ✅
- [ ] Open Graph 标签已配置 ✅
- [ ] Sitemap 已生成 ✅
- [ ] RSS Feed 已配置 ✅

### 内容（AdSense 申请前）

- [ ] 至少 15 篇高质量原创文章已发布
- [ ] 每篇文章字数不少于 800 词
- [ ] 所有文章 Frontmatter 完整
- [ ] 隐私政策页面已创建 ✅
- [ ] 关于页面已创建 ✅

---

> 📋 **操作顺序建议**：先完成域名购买和 GA4 配置 → 扩充内容至 15+ 篇 → 部署到 Vercel → 申请 AdSense → 通过后配置广告单元。
