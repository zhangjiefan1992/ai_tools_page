# AI Tools Hub 文章写作规范

> **本文档用途**：作为 AI 统筹 Agent 生成博客文章的**唯一参考规范**。AI Agent 只需阅读本文档，即可生成完全符合项目技术标准和内容要求的文章，无需参考其他文件。

- **项目名称**：AI Tools Hub
- **技术栈**：Astro SSG + Markdown Content Collections
- **文章语言**：英文（English）
- **站点描述**：Honest reviews, tutorials, and comparisons of the best AI tools to boost your productivity.

---

## 1. 文件存放规范

| 规则 | 说明 |
|------|------|
| 文件目录 | `src/content/blog/en/` |
| 文件格式 | Markdown (`.md`) |
| 文件命名 | **kebab-case**，全小写，单词用连字符分隔 |
| 命名示例 | `best-ai-writing-tools-2026.md`、`chatgpt-vs-claude-comparison.md` |
| slug 规则 | 文件名即 URL slug。文件名 `my-article.md` → URL `/blog/my-article` |

> ⚠️ 文件名中不要包含大写字母、空格、下划线或特殊字符。

---

## 2. Frontmatter 完整规范

每篇文章开头必须包含 YAML frontmatter（用 `---` 包裹）。以下是所有支持的字段：

| 字段名 | 类型 | 必填/选填 | 验证规则 | 说明 | 示例值 |
|--------|------|-----------|----------|------|--------|
| `title` | string | **必填** | 3-100 字符 | 文章标题，用于 `<title>` 标签和卡片展示 | `"10 Best AI Writing Tools in 2026: Comprehensive Guide"` |
| `description` | string | **必填** | 10-300 字符 | Meta description，用于 SEO 和文章卡片摘要 | `"Discover the top AI writing tools of 2026. We tested and ranked the best options for content creators."` |
| `publishDate` | date | **必填** | ISO 日期格式 | 发布日期 | `2026-04-15` |
| `updatedDate` | date | 选填 | ISO 日期格式 | 最后更新日期 | `2026-04-25` |
| `category` | enum | **必填** | 仅限 4 个值之一 | 文章分类，见下方分类说明 | `review` |
| `tags` | string[] | **必填** | 1-8 个标签，全小写 | 文章标签，自动转小写和去除空格 | `["ai-writing", "content-creation", "productivity"]` |
| `author` | string | 选填 | — | 作者名称，默认值 `"AI Tools Hub Team"` | `"AI Tools Hub Team"` |
| `authorAvatar` | string | 选填 | 合法 URL | 作者头像地址 | `"https://example.com/avatar.jpg"` |
| `authorTwitter` | string | 选填 | 不含 `@` 符号 | 作者 Twitter 用户名 | `"alexchen_ai"` |
| `image` | string | 选填 | — | 文章特色图片路径 | `"/images/placeholder.svg"` |
| `imageAlt` | string | 选填 | — | 图片 alt 描述文字 | `"Best AI writing tools comparison chart"` |
| `draft` | boolean | 选填 | — | 是否为草稿，默认 `false` | `false` |
| `featured` | boolean | 选填 | — | 是否为推荐文章，默认 `false` | `false` |
| `canonicalURL` | string | 选填 | 合法 URL | 规范 URL（用于避免重复内容） | `"https://example.com/original-article"` |
| `ogImage` | string | 选填 | — | Open Graph 图片路径（社交分享） | `"/images/og-article.png"` |
| `robots` | string | 选填 | — | 自定义 robots 指令 | `"noindex, nofollow"` |
| `disableAds` | boolean | 选填 | — | 是否禁用文内广告，默认 `false` | `false` |

---

## 3. 分类说明

项目支持 4 个固定分类，`category` 字段**只能使用以下值**：

| 分类 slug | 显示名称 | 适用场景 | URL |
|-----------|----------|----------|-----|
| `review` | Reviews | 单个 AI 工具的深度评测 | `/category/review` |
| `comparison` | Comparisons | 两个或多个工具的对比分析 | `/category/comparison` |
| `tutorial` | Tutorials | 使用教程和操作指南 | `/category/tutorial` |
| `best-of` | Best Of | "最佳 X 工具" 排行榜/汇总文章 | `/category/best-of` |

---

## 4. 内容结构要求

### 4.1 基本要求

| 要求 | 标准 | 说明 |
|------|------|------|
| 最低字数 | **800 词以上**（英文） | 建议 1200-1800 词以获得更好的 SEO 表现 |
| 段落数量 | **至少 6 个 `<p>` 段落** | 低于 6 段不会触发文内广告注入 |
| 建议段落数 | **12+ 段落** | 最大化广告收入 |
| 标题层级 | 使用 `##`（h2）和 `###`（h3） | **不要在正文中使用 `#`（h1）**，h1 由布局模板自动渲染 |
| 文章开头 | 第一段为引言/概述段落 | 不要在文章开头立即使用标题，先写一段引言 |
| 每个 h2 下 | 2-3 个自然段落 | 确保每个章节有足够的内容深度 |

### 4.2 广告注入规则

项目使用 `rehype-ad-injector` 插件，会在文章渲染时自动插入广告位。规则如下：

| 参数 | 值 | 说明 |
|------|-----|------|
| 最低段落数 | 6 段 | 段落少于 6 个时**不会注入任何广告** |
| 插入间隔 | 每 3 段 | 每隔 3 个 `<p>` 段落插入一个广告位 |
| 最大广告数 | 3 个 | 单篇文章最多 3 个广告位 |

广告位数量与段落数的关系：

| 段落数 | 广告位数量 |
|--------|-----------|
| < 6 段 | 0 个（不注入） |
| 6-8 段 | 1 个 |
| 9-11 段 | 2 个 |
| 12+ 段 | **3 个（最大值）** |

> **重要**：为最大化广告收入，每篇文章应至少包含 **12 个段落**。

### 4.3 推荐文章结构模板

```markdown
引言段落（概述全文主题，吸引读者，包含主要关键词）

第二段落（补充背景信息或引出正文内容）

## 第一个主要章节标题
段落内容...
段落内容...

## 第二个主要章节标题
段落内容...
段落内容...

## 第三个主要章节标题
段落内容...
段落内容...

## 第四个主要章节标题（以此类推）
段落内容...
段落内容...

## Conclusion / Final Thoughts
总结段落...
补充建议或行动号召段落...
```

---

## 5. SEO 写作规范

### 5.1 Title 优化

- 包含主要关键词，放在标题前半部分
- 最佳长度：**50-60 字符**
- 推荐格式：`"主题: 副标题 年份"` 或 `"数字 + Best/Top + 核心关键词 + 年份"`
- 示例：`"10 Best AI Writing Tools in 2026: Comprehensive Guide"`

### 5.2 Description 优化

- 包含核心关键词，使用自然语言描述
- 最佳长度：**150-160 字符**
- 应能独立概括文章核心价值，吸引用户点击
- 不要堆砌关键词

### 5.3 Tags 规范

- 使用小写连字符格式，例如：`ai-writing`、`content-creation`
- 每篇文章 **3-5 个标签**（最少 1 个，最多 8 个）
- 标签应覆盖：工具名、内容类型、使用场景

### 5.4 正文 SEO 要点

- **文章正文第一行**使用 `# 标题` 作为 h1，应与 frontmatter `title` 匹配或接近
- **内部链接**：在文章中适当引用其他文章或分类页面（如 `/blog/chatgpt-vs-claude-comparison` 或 `/category/review`）
- **图片 alt 文本**：所有图片必须有描述性 alt 文本
- **关键词分布**：主关键词在 h1、h2、首段、末段中自然出现

---

## 6. GEO（生成式引擎优化）写作原则

GEO 旨在让文章内容更容易被 AI 搜索引擎（如 ChatGPT、Perplexity、Google AI Overview）检索和引用。

### 6.1 事实密度
- 每 **150-200 词**包含一个具体数据点或统计信息
- 示例：价格、用户数量、性能指标、发布日期等

### 6.2 答案优先
- 在文章开头和每个章节开头**先给出核心结论**，再展开详细分析
- 避免"铺垫式"写作，直接回答读者可能提出的问题

### 6.3 实体清晰度
- 明确提及工具名称、公司名称、版本号、价格等实体信息
- 避免模糊代词，如"该工具"——应直接使用工具全名

### 6.4 列表和表格
- 大量使用**项目符号列表**和**比较表格**
- 提高 AI 检索的"可提取性"（extractability）
- 比较类文章务必包含对比表格

### 6.5 权威信号
- 引用具体测试方法、评测标准
- 说明数据来源和对比依据
- 使用"我们测试了..."、"经过 X 个月的评估..."等表述增强可信度

---

## 7. Frontmatter 模板

以下 4 个模板可直接复制使用，按需修改具体内容即可。

### 7.1 Review（评测类）模板

```yaml
---
title: "[工具名] Review 2026: Is It Worth It?"
description: "An honest, in-depth review of [工具名] covering features, pricing, pros and cons. Find out if it's the right AI tool for your needs."
publishDate: 2026-MM-DD
category: review
tags:
  - [tool-name]
  - ai-tools
  - review
author: "AI Tools Hub Team"
image: "/images/placeholder.svg"
imageAlt: "[工具名] review featured image"
draft: false
featured: false
---
```

### 7.2 Comparison（对比类）模板

```yaml
---
title: "[工具A] vs [工具B]: Which Is Better in 2026?"
description: "A detailed comparison of [工具A] and [工具B] across features, pricing, and performance. Discover which AI tool fits your workflow."
publishDate: 2026-MM-DD
category: comparison
tags:
  - [tool-a-name]
  - [tool-b-name]
  - comparison
  - ai-tools
author: "AI Tools Hub Team"
image: "/images/placeholder.svg"
imageAlt: "Side by side comparison of [工具A] and [工具B]"
draft: false
featured: false
---
```

### 7.3 Tutorial（教程类）模板

```yaml
---
title: "How to Use [工具名]: Complete Guide 2026"
description: "Learn how to get started with [工具名] in this step-by-step tutorial. Covers setup, key features, and advanced tips for beginners and pros."
publishDate: 2026-MM-DD
category: tutorial
tags:
  - [tool-name]
  - tutorial
  - how-to
author: "AI Tools Hub Team"
image: "/images/placeholder.svg"
imageAlt: "Step-by-step guide to using [工具名]"
draft: false
featured: false
---
```

### 7.4 Best-of（榜单类）模板

```yaml
---
title: "N Best [类别] Tools in 2026: Comprehensive Guide"
description: "Discover the top N [类别] tools of 2026. We tested and ranked the best options for [目标用户] looking to [目标]."
publishDate: 2026-MM-DD
category: best-of
tags:
  - [category-keyword]
  - ai-tools
  - tools-roundup
  - best-of
author: "AI Tools Hub Team"
image: "/images/placeholder.svg"
imageAlt: "Best [类别] tools comparison chart"
draft: false
featured: false
---
```

---

## 8. 建议文章主题清单

以下为按分类组织的文章主题建议，共 20 个。文件名请根据标题自行转换为 kebab-case。

### Reviews 分类（评测类）

| # | 文章标题 | 建议文件名 |
|---|---------|-----------|
| 1 | Jasper AI Review 2026: Is It Worth $49/Month for Marketing Teams? | `jasper-ai-review-2026.md` |
| 2 | Grammarly Premium Review: AI-Powered Writing Enhancement Beyond Grammar | `grammarly-premium-review.md` |
| 3 | Notion AI Review: How Good Is the Built-In AI Assistant? | `notion-ai-review.md` |
| 4 | Copy.ai Review 2026: Automating Sales Copy and Marketing Workflows | `copy-ai-review-2026.md` |
| 5 | Writesonic Review: AI Content Generation for SEO-Focused Bloggers | `writesonic-review.md` |

### Comparisons 分类（对比类）

| # | 文章标题 | 建议文件名 |
|---|---------|-----------|
| 6 | Jasper vs Copy.ai: Which AI Marketing Tool Delivers Better ROI? | `jasper-vs-copy-ai-comparison.md` |
| 7 | Grammarly vs Wordtune: Best AI Writing Enhancement Tool Compared | `grammarly-vs-wordtune-comparison.md` |
| 8 | Midjourney vs DALL-E 3: AI Image Generation Head-to-Head | `midjourney-vs-dall-e-3-comparison.md` |
| 9 | Notion AI vs ChatGPT: Which AI Assistant Fits Your Workflow? | `notion-ai-vs-chatgpt-comparison.md` |
| 10 | Rytr vs Writesonic: Best Budget AI Writing Tool for Beginners | `rytr-vs-writesonic-comparison.md` |

### Tutorials 分类（教程类）

| # | 文章标题 | 建议文件名 |
|---|---------|-----------|
| 11 | How to Use ChatGPT for Content Marketing: A Complete Guide | `how-to-use-chatgpt-content-marketing.md` |
| 12 | Getting Started with Claude: Advanced Prompting Techniques | `getting-started-with-claude-prompting.md` |
| 13 | How to Build an AI-Powered Writing Workflow in 2026 | `ai-powered-writing-workflow-2026.md` |
| 14 | Mastering Jasper AI: Brand Voice Training Step-by-Step | `mastering-jasper-ai-brand-voice.md` |
| 15 | How to Use AI Tools for SEO Content Optimization | `how-to-use-ai-tools-seo-optimization.md` |

### Best-of 分类（榜单类）

| # | 文章标题 | 建议文件名 |
|---|---------|-----------|
| 16 | 5 Best AI Image Generators in 2026: Beyond Midjourney | `best-ai-image-generators-2026.md` |
| 17 | 7 Best Free AI Tools for Students and Educators | `best-free-ai-tools-students.md` |
| 18 | 8 Best AI Tools for Small Business Owners in 2026 | `best-ai-tools-small-business-2026.md` |
| 19 | 6 Best AI Coding Assistants: GitHub Copilot, Cursor, and More | `best-ai-coding-assistants.md` |
| 20 | Top 5 AI Presentation Tools to Replace PowerPoint in 2026 | `best-ai-presentation-tools-2026.md` |

---

## 9. 质量检查清单

文章完成后，必须逐项确认以下内容：

### Frontmatter 检查
- [ ] `title` 已填写，3-100 字符
- [ ] `description` 已填写，10-300 字符
- [ ] `publishDate` 已填写，格式为 `YYYY-MM-DD`
- [ ] `category` 值为 `review` / `comparison` / `tutorial` / `best-of` 之一
- [ ] `tags` 至少 1 个，最多 8 个，全小写连字符格式
- [ ] `author` 已填写（可使用默认值 `"AI Tools Hub Team"`）
- [ ] `image` 和 `imageAlt` 已填写

### 内容检查
- [ ] 文章字数 ≥ 800 词（英文）
- [ ] 段落数 ≥ 6（建议 12+ 以最大化广告位）
- [ ] 正文第一行为 `# 标题`（h1），后续使用 `##`（h2）和 `###`（h3）
- [ ] 正文不使用 h1（`#`）作为章节标题
- [ ] 文章以引言段落开头，不是直接以 h2 开头
- [ ] 每个 h2 章节下有 2-3 个自然段落

### SEO / GEO 检查
- [ ] title 包含主要关键词
- [ ] description 自然描述文章内容，包含关键词
- [ ] 每 150-200 词包含一个具体数据点
- [ ] 使用了列表或表格来提升可提取性
- [ ] 包含内部链接（指向其他文章或分类页）

### 文件规范检查
- [ ] 文件名使用 kebab-case 全小写格式
- [ ] 文件保存在 `src/content/blog/en/` 目录下
- [ ] 文件扩展名为 `.md`

---

## 10. 示例文章参考

以下为一篇实际文章的开头部分（comparison 分类），展示完整的 frontmatter 和正文格式：

```markdown
---
title: "ChatGPT vs Claude 3.5: Which AI Assistant Is Better in 2026?"
description: "An in-depth comparison of ChatGPT (GPT-4o) and Claude 3.5 Sonnet across writing, coding, analysis, and creative tasks. Find out which AI tool suits your needs."
publishDate: 2026-04-20
updatedDate: 2026-04-25
category: comparison
tags:
  - chatgpt
  - claude
  - ai-assistants
  - comparison
author: "Alex Chen"
authorTwitter: "alexchen_ai"
image: "/images/placeholder.svg"
imageAlt: "Side by side comparison of ChatGPT and Claude interfaces"
draft: false
featured: true
---

# ChatGPT vs Claude 3.5: The Ultimate Comparison

In this comprehensive comparison, we put two of the most powerful AI assistants head to head — OpenAI's ChatGPT powered by GPT-4o and Anthropic's Claude 3.5 Sonnet. Both tools have matured significantly throughout 2025 and into 2026, each carving out distinct strengths and loyal user bases. If you are trying to decide which AI assistant deserves your subscription dollars, this detailed breakdown will help you make an informed choice.

We tested both tools across hundreds of prompts spanning five major categories: writing quality, coding ability, analytical reasoning, creative tasks, and general knowledge. Here is what we found.

## Writing Quality

When it comes to writing, both ChatGPT and Claude deliver impressive results, but they have noticeably different styles. ChatGPT tends to produce content with a confident, energetic tone. Its output is polished and reads well out of the box, with strong paragraph structure and natural transitions. It excels at marketing copy, social media content, and persuasive writing where a punchy, engaging style is desirable.

Claude, on the other hand, produces writing that is more measured, nuanced, and detailed. Its output tends to be longer and more thorough, with careful attention to caveats and balanced perspectives. Academic writers, researchers, and professionals who need precision over flair often prefer Claude's writing style.

## Coding Ability

...（后续章节继续）
```

### 示例要点说明

1. **Frontmatter** 使用 `---` 包裹，所有必填字段齐全
2. **正文第一行**是 `# 标题`（h1），与 frontmatter title 含义一致但可以不完全相同
3. **引言**为两个自然段落，概述全文并说明测试方法
4. **h2 章节**下各有 2+ 个自然段落
5. **tags** 全小写，使用连字符分隔多词标签
6. **category** 使用精确的枚举值 `comparison`

---

## 附录：常见错误

| 错误 | 正确做法 |
|------|---------|
| `category: "reviews"` | `category: review`（使用精确枚举值，无引号亦可） |
| `tags: ["AI-Writing", "SEO"]` | `tags: ["ai-writing", "seo"]`（全小写） |
| 正文章节使用 `# 章节标题` | 使用 `## 章节标题`（h2），h1 仅用于文章最开头的标题 |
| 文章只有 4 个段落 | 至少 6 段（建议 12+），否则不会注入广告 |
| description 超过 300 字符 | 控制在 10-300 字符内，建议 150-160 字符 |
| 文件名 `My_Article.md` | 使用 `my-article.md`（kebab-case 全小写） |
| 文章直接以 `## 章节` 开头 | 先写 1-2 段引言，再使用 h2 |
| `publishDate: "April 15, 2026"` | `publishDate: 2026-04-15`（ISO 格式） |
