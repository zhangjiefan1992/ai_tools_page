---
title: "Oh-My-Pi 多模型路由实战：一次会话运行 5 个 AI 模型，节省 61% Token"
description: "oh-my-pi 5 角色模型路由系统实战指南。手把手教你配置 models.yml、设置 fallback 链、用真实基准数据实现最高 61% 的 Token 节省。"
publishDate: 2026-06-01
category: tutorial
tags:
  - oh-my-pi
  - ai-coding-assistant
  - multi-model
  - developer-tools
  - tutorial
  - cost-optimization
author: "Pick My AI Team"
image: "/images/omp-multi-model-routing-guide-hero.png"
imageAlt: "oh-my-pi 的 5 角色模型路由示意图，展示 fallback 链和 Token 节省"
draft: false
---

# Oh-My-Pi 多模型路由实战：一次会话运行 5 个 AI 模型，节省 61% Token

大多数 AI 编程 Agent 把你锁死在一个模型上。Claude Code 用 Claude，GitHub Copilot 用 GPT-4，Cursor 虽然允许切换模型，但本质上还是单体选择——你选一个模型，它就用这一个来处理所有事情，不管是生成一行 commit message 还是规划一次跨文件重构。

Oh-My-Pi（`omp`）的思路完全不同。它通过一个 5 角色系统，将不同类型的工作路由到不同的模型，每个角色都有独立的降级链、凭证轮换和路径作用域规则。根据项目的基准测试数据，这套架构配合 Hashline 编辑格式，将 Grok 4 Fast 的输出 token 消耗降低了 61%，GLM-5-Turbo 的端到端耗时缩短了 37%。基于项目已公开的基准数据和社区反馈，这些收益在各种模型上均可复现。

本指南将从零开始带你搭建多模型路由，包含配置示例、成本拆解和来自项目文档及社区的实战经验。如果你还没看过我们的 [oh-my-pi 完整测评](/zh/blog/oh-my-pi-review-2026)，建议先去了解全貌。

## 5 角色架构：为什么重要

Oh-My-Pi 定义了五个命名角色，各自负责不同类别的工作。Agent 发出的每一次 API 调用都会路由到匹配当前任务的角色，而非全局统一的模型设置。以下是各角色的功能和存在意义：

| Role | 用途 | 典型任务 | 理想模型画像 |
|------|------|----------|-------------|
| `default` | 通用编码——编辑、读取、工具调用 | 实现功能、修复 bug | 能力强，速度适中 |
| `smol` | 快速、廉价的操作 | 生成 commit message、文件摘要、简单重命名 | 速度快、成本低、够用就好 |
| `slow` | 需要深度思考的复杂推理 | 架构规划、排查疑难逻辑 | 能力强，可以使用思维 token |
| `plan` | 多步骤任务规划 | 把功能拆分为子任务、Review PR | 推理能力强，结构化输出好 |
| `commit` | 生成 Git commit message | 原子提交拆分、变更日志条目 | 速度快、简洁、格式感知好 |

关键洞察在于：在一次典型的编程会话中，Agent 发起的 API 调用有很大比例属于"小任务"——编辑前先总结一下文件内容、生成一行 commit message、或者决定下一步调用哪个工具。把这些任务路由到 $0.10/M-token 的模型而非 $15/M-token 的模型，能在几乎不影响该类任务质量的前提下，显著降低成本。

举个例子：考虑一次典型的 45 分钟重构会话，大约会产生 100-130 次 API 调用。如果不做角色路由（所有调用都发给 Claude Sonnet 4.5），这样一次会话的成本可能在 $4-5。而使用角色路由后（smol 任务走 Qwen-Plus，default 走 Claude Sonnet 4.5，slow 走 Claude Opus），同样的工作量可以控制在 $2 以内——潜在节省 60%，因为大部分调用都是不需要高端模型的轻量操作。

## 配置 models.yml：完整步骤

路由配置存放在 `~/.omp/agent/models.yml`。以下是一个可供参考的配置方案：

```yaml
# ~/.omp/agent/models.yml
roles:
  default:
    - provider: anthropic
      model: claude-sonnet-4-5-20250514
      
  smol:
    - provider: alibaba
      model: qwen-plus
    - provider: groq
      model: llama-3.3-70b-versatile
      
  slow:
    - provider: anthropic
      model: claude-opus-4-20250514
    - provider: openai
      model: o3
      
  plan:
    - provider: anthropic
      model: claude-sonnet-4-5-20250514
    - provider: openai
      model: gpt-4.1
      
  commit:
    - provider: groq
      model: llama-3.3-70b-versatile
    - provider: alibaba
      model: qwen-plus
```

每个角色接受一个按优先级排列的模型列表。当链中第一个模型出错（触发速率限制、网络异常、上下文长度超限），`omp` 会自动降级到下一个条目。这个切换对 Agent 是透明的——不会丢失上下文，也不需要重新开始任务。

创建好文件后，运行 `omp` 并输入 `/models` 来验证配置是否正确加载。你应该能看到每个角色映射到的主模型以及降级指示。

## 降级链：实际行为

### 预期行为

降级链在理论上很简单。但实际使用中，有几个不太直观的行为会显著影响可靠性和成本。

**速率限制级联是最大的收益点。** 根据项目文档，当使用 `omp commit` 批量生成提交时，如果 Groq 的 Llama 3.3 70B 触发了速率限制，系统会静默降级到阿里云的 Qwen-Plus。会话继续运行不受影响——社区用户反馈唯一可感知的变化是 commit message 风格略有偏移，因为 Qwen-Plus 的表达偏向更详细。

**上下文长度不匹配需要注意。** 如果你的 `slow` 角色主模型有 200K 上下文窗口，而降级模型只有 32K，那么长对话在降级后就会失败。比如 `slow` 链从 Claude Opus（200K）降级到本地 Ollama 模型（8K 上下文），会话中途就会断掉。解决方案是确保同一链中的所有模型具有大致相当的上下文限制，或者给短上下文模型设置 `maxContext` 保护。

**跨供应商的凭证轮换是自动的。** 你可以为单个角色配置多个 API key：

```yaml
roles:
  default:
    - provider: anthropic
      model: claude-sonnet-4-5-20250514
      credentials:
        - key: sk-ant-api03-xxxxx1
        - key: sk-ant-api03-xxxxx2
```

Oh-My-Pi 会在这些 key 之间轮询使用，配置的 key 数量大致可以等比例提升该角色的有效速率上限。对于共享少量 API key 的团队来说，这是避免在密集会话中触发单 key 限流的实用方式。

## 场景示例：一次全栈重构

### 路由如何映射到工作流各阶段

要理解角色路由的价值，来看一个典型的多阶段任务如何映射到 5 个角色。以在 Next.js 应用（Python API 后端）中把 15 个 API 端点从 REST 迁移到 tRPC 为例。

**阶段 1 — 规划：** `plan` 角色调用 Claude Sonnet 4.5 来分析代码库结构，识别所有端点及其消费者，并生成按依赖排序的迁移计划。这个阶段 API 调用次数少，但需要强推理能力。

**阶段 2 — 执行：** `default` 角色处理实际的代码变更——重写路由处理器、更新客户端调用、修改类型定义。当 Agent 执行轻量操作（如"总结一下这个中间件的作用"）时，`smol` 角色接管并路由到 Qwen-Plus，成本只是前者的零头。

**阶段 3 — 调试：** 如果迁移后测试失败，`slow` 角色调用 Claude Opus 做深度分析——比如在多层泛型包装器中追踪类型不匹配。

**阶段 4 — 提交：** `omp commit` 使用 `commit` 角色，将变更文件拆分为原子提交。每条 commit message 由 Groq 上的 Llama 3.3 70B 生成——速度快（每条不到一秒）且成本极低。

### 为什么成本差异巨大

各阶段的成本差异非常大。规划和调试需要昂贵的高能力模型，但调用次数相对较少。执行阶段调用量大，但大部分轻量操作可以路由到廉价模型。提交阶段调用量高但每次调用都很简单。如果没有路由，每一次调用——不论难度——都会打到同一个高端模型上。从已公开的基准数据来看（Grok 4 Fast -61% token，Claude Sonnet 4.5 -24% token），路由机制加上 Hashline 格式，能够大幅降低每次会话的成本。

## /bench 命令：自动发现最快的模型

Oh-My-Pi 内置了基准测试工具 `/bench`，会探测所有已配置供应商的每个可用模型，测量延迟、成本和输出质量。这不是理论估算——它会发送真实的流式 API 调用和代表性 prompt，然后对结果排名。

基准测试参数可调：

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `PER_CALL_TIMEOUT_MS` | 4,000 | 单次探测最大耗时 |
| `TOTAL_RUN_TIMEOUT_MS` | 30,000 | 整个测试的硬性时间上限 |
| `CONCURRENCY_PER_PROVIDER` | 8 | 每个供应商的并行探测数 |
| `BATCH_GAP_MS` | 200 | 探测批次之间的间隔 |

根据项目文档，表现最稳定的是阿里云通义千问系列，延迟低于 700ms 且成本趋近于零——非常适合作为 `smol` 和 `commit` 角色的候选模型。基准测试会输出 `bench-candidates.txt` 文件，列出所有通过质量筛选的模型以及被淘汰模型的原因。

真正强大的地方在于 `pi-bench` 会自动与 `pi-recap`（omp 的摘要扩展）联动。当你运行一次新的基准测试后，策划好的模型链会自动更新，下游工具（如摘要器）也会自动采用新的优胜模型，无需手动修改配置。

## 成本对比：各模型的 Token 节省

除了路由本身，`omp` 使用的 Hashline 编辑格式也是 token 节省的重要来源。以下是 oh-my-pi 基准测试套件的实测数据，对比 Hashline 与传统 `str_replace` 风格编辑的表现：

| 模型 | 编辑通过率变化 | 输出 Token 变化 | 发生了什么 |
|------|---------------|----------------|-----------|
| Grok Code Fast 1 | 6.7% → 68.3% | -49% | 十倍提升——编辑格式不再拖垮模型 |
| Gemini 3 Flash | 比 str_replace 高 5 个百分点 | — | 比 Google 自己对该格式的最佳实现还好 |
| Grok 4 Fast | — | -61% token | 消除了 diff 错误导致的重试循环后，输出量骤降 |
| MiniMax | 通过率 2.1 倍 | — | 同样的权重、同样的 prompt，通过率翻倍 |
| Claude Sonnet 4.5 | 80.0% Hashline v2 | -24% token | 本就很强的基线进一步提升 |

这些数据对路由决策至关重要，因为它们与角色路由的节省是叠加关系。一个 `smol` 调用使用廉价模型搭配 Hashline 格式，成本只是传统 Agent 用昂贵模型加 str_replace 重试的零头。

## 进阶：按路径作用域路由

Oh-My-Pi 支持基于路径的模型覆盖规则，允许你对代码库的不同部分使用不同的模型。这对多语言项目特别有用：

```yaml
roles:
  default:
    - provider: anthropic
      model: claude-sonnet-4-5-20250514
      paths:
        - "src/**/*.ts"
        - "src/**/*.tsx"
    - provider: google
      model: gemini-2.5-pro
      paths:
        - "backend/**/*.py"
        - "ml/**/*.py"
```

一个典型用法是将 Python ML 代码路由到 Gemini 2.5 Pro（在 Python 密集型任务上表现出色），同时将 TypeScript 工作保持在 Claude Sonnet 4.5 上。路由过程是透明的——你不需要告诉 Agent 用哪个模型，它会根据当前操作涉及的文件路径自动推断。

## Web 搜索供应商链：14 个后端，一个工具

除了模型路由，`omp` 对 Web 搜索也采用了同样的链式降级模式，支持 14 个排名后端：

| 供应商 | 认证方式 | 最佳用途 |
|--------|---------|---------|
| auto | chain | 默认——按顺序遍历所有供应商 |
| exa | EXA_API_KEY | 语义搜索，查找相似内容 |
| brave | BRAVE_API_KEY | 通用网页搜索，隐私保护好 |
| jina | JINA_API_KEY | 文档提取和阅读模式 |
| kimi | MOONSHOT_API_KEY | 中文内容 |
| perplexity | PERPLEXITY_API_KEY | 研究级回答，带引用来源 |
| tavily | TAVILY_API_KEY | AI 优化的搜索结果 |
| kagi | KAGI_API_KEY | 无广告、高质量结果 |
| searxng | 自托管 | 完全隐私，无需 API key |

将搜索供应商设为 `auto` 意味着 `omp` 会按顺序尝试每个后端，直到有一个返回结果。常见配置是 Brave 作为主力、Jina 作为降级——两者结合覆盖了通用网页搜索和文档提取，降级链透明地处理速率限制。

## Gentle Coding：社区发现的优化技巧

oh-my-pi 社区（来自项目 Discord 和 GitHub 讨论中贡献者的分享）最出人意料的发现之一是"Gentle Coding"提示词优化技术。标准 Agent 提示词使用命令式、有时甚至是强制性的语言（"你必须完成此任务"、"绝对不要留下未完成的代码"）。Gentle Coding 方式将其替换为协作式表达，基准测试结果非常亮眼：

| 模型 | 指标 | Gentle Coding 效果 |
|------|------|-------------------|
| GLM-5.1 (Medium) | 通过率 | +22%，修复了 100% 的冻结问题 |
| GLM-5.1 (Medium) | 延迟 | 中位数降低 23.3% |
| GLM-5-Turbo | 端到端耗时 | -37%（关闭思维模式） |
| GLM-5-Turbo (Thinking High) | 端到端耗时 | 中位数降低 18.4% |
| Kimi K2.6 (Turbo/High) | 输入 token | -36%，输出 -23%，耗时 -11% |
| Claude 4.6 Sonnet/Opus 及 GPT-5 | 稳定性 | 消除了"Agent 失控"——恐慌驱动的 30 分钟以上无限工具调用循环 |

GLM-5.1 的结果尤其惊人：根据项目的基准报告，标准基线在 6 次试验中全部超时崩溃，而 Gentle Coding 则 6 题全部秒解。这不是边际改进——这是模型可用与不可用之间的差别。

要在你的配置中启用 Gentle Coding，请修改 `~/.omp/agent/agent.md` 中的系统提示词，使用协作式语言。Oh-My-Pi 的默认提示词已经内置了这些模式，但如果你自定义过系统提示词，值得排查一下是否存在强制性措辞。

## 社区实战心得

基于社区反馈和项目文档，以下是一些容易忽略的经验：

**先从两个角色开始，别一上来就配五个。** 先配置 `default` 和 `smol`，等你搞清楚路由的手感后，再加 `slow`、`plan` 和 `commit`。在还没弄明白各角色边界的情况下就全部启用，只会让你搞不清哪个模型处理了什么。

**用 `/stats` 监控。** Oh-My-Pi 会跟踪每个角色的 API 调用次数、token 用量和延迟。会话结束后运行 `/stats` 看看 token 花在了哪里。如果你发现大量 token 消耗在了本应用廉价模型处理的 `smol` 任务上，那就说明 smol 路由的触发频率不够高——需要调整角色边界。

**降级链保持简短。** 每个角色两个模型通常足够，三个是实际上限。更长的链只会在故障场景中增加延迟，而不会带来有意义的可靠性提升，因为如果两个独立供应商同时宕机，问题大概率出在你这边。

**先用本地模型测试再花钱。** 用 Ollama 跑一个 7B 模型，把每个角色都设成它。跑一遍你的典型工作流。这能告诉你工作流会产生多少 API 调用、哪些角色流量最大——在决定付费模型配额之前，你需要这些信息。

## 什么时候多模型路由不划算

客观地说，有些场景下单模型的简单粗暴更占优。如果你用的是 Claude Max 或 ChatGPT Plus 这类无限量套餐，路由的经济性论据就不成立了——不管怎么用都是固定费用。如果你的工作都是短会话（15 分钟以内），配置路由的开销比节省的成本还大。如果你只用本地模型，在它们之间路由只是徒增复杂度，并不能节省成本。

多模型路由的优势场景是：按 token 计费的 API 方案、长会话（30 分钟以上）、跨多种语言或领域的工作，以及需要跨供应商降级来保证可靠性。关于 `omp` 在路由之外的更多能力，参见我们的 [oh-my-pi 完整测评](/zh/blog/oh-my-pi-review-2026)。

## 结论

Oh-My-Pi 的多模型路由不只是一个功能——它是一种关于 AI 编程 Agent 应该如何工作的理念。认为每次 API 调用都值得用 $15/M-token 模型来处理，就像认为数据库查询优化器应该永远做全表扫描一样浪费。通过将工作分配到 5 个功能匹配的角色、配合自动降级和凭证轮换，`omp` 带来了实实在在的收益：最高 61% 的 token 节省（Grok 4 Fast 基准）、跨供应商零停机降级，以及为每个具体任务使用最佳模型而非为所有任务使用最佳平均模型的能力。

配置投入是真实存在的——预计 30 分钟可以跑通基础路由，完整调优需要几天时间。但回报同样真实，而且配置通过一个 YAML 文件就能跨机器迁移。对于使用按 token 计费 API 方案的开发者来说，路由系统能很快收回学习成本——尤其是那些每天都要跑长会话的人。
