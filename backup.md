# 项目框架总结

## 1. 项目定位

### 一句话定位
一个面向**独立开发者 / 产品探索场景**的、**skill-based research workflow system**。

它不是一个通用聊天机器人，也不是一个“缩水版 Deep Research”。  
它的核心目标，是把一个模糊想法或研究任务，稳定推进成：

- 研究结论
- 竞品与用户洞察
- MVP 规格
- 执行清单
- 可复用的项目上下文

### 核心使用场景
这个项目最适合围绕以下三类场景展开：

#### 1）Idea → Research → MVP
用户有一个模糊想法，需要：
- 澄清目标
- 找竞品
- 看用户痛点
- 形成 MVP 方案

#### 2）Tech / Product Due Diligence
用户给一个 repo、框架或产品方向，需要：
- 调研资料
- 做比较
- 输出优缺点
- 给推荐方案

#### 3）独立开发执行辅助
研究完以后，继续生成：
- PRD / spec
- issue / task 列表
- launch checklist
- 内容草案

也就是说，它不是为了“回答问题”，而是为了**推进工作流**。

---

## 2. 为什么不是“直接跟 GPT 聊天就行”

### 先说结论
对于简单问题，这个系统**不一定比直接聊天更好**。

如果只是：
- 问一个概念
- 快速比较两个框架
- 要一个灵感
- 做一轮简单 brainstorm

那么直接和 GPT 聊天通常：
- 更快
- 更便宜
- 更自然

### 这个系统真正更好的地方
它的价值只在这些场景成立：

#### A. 任务是多阶段的
不是“问一句，答一句”，而是：
- 先澄清
- 再调研
- 再比较
- 再生成交付物
- 再进入下一步动作

#### B. 任务需要多源证据
不是只靠模型记忆，而是要结合：
- web
- GitHub
- 文档
- 私有资料
- 社区内容

#### C. 任务需要稳定输出
用户要的不是聊天回复，而是：
- competitor matrix
- MVP spec
- issue list
- research brief

#### D. 任务需要可追溯、可复用
直接聊天通常有这些问题：
- 过程不可控
- 输出不稳定
- 很难复现
- 很难接下一步动作

而这个系统追求的是：
- 有状态
- 有流程
- 有结构化中间产物
- 有评估和复盘能力

### 推荐话术
可以这样解释：

> 它不是为了替代普通聊天，而是为了处理“多阶段、多来源、要结构化交付件、要可追溯”的任务。对于简单问答，直接聊天更合适；对于研究与规划型工作流，这套系统更好。

---

## 3. 核心设计原则

## 核心原则一：Workflow-first，而不是 Chat-first

### 含义
不是先做一个聊天机器人，再往里塞功能。  
而是先定义任务流程，再让聊天界面成为流程入口。

### 优势
- 任务推进更稳定
- 输出更结构化
- 更适合做评估与回归测试
- 更适合接 skills 和后续动作

### 风险
- 灵活性比纯聊天弱
- 如果流程设计太重，会显得“很聪明但很烦”

---

## 核心原则二：上下文隔离（Context Isolation）

这是整个系统最重要的工程点之一。

### 为什么需要
如果没有上下文隔离，系统会很容易变脏：

- brainstorm 的发散内容污染 research
- research 的猜测污染长期记忆
- 一个 skill 的临时推理泄漏给另一个 skill
- 上一个任务残留影响下一个任务

### 我们的做法
把上下文分成 5 层：

#### 1. Global User Profile
长期稳定偏好：
- 输出风格
- 常用平台
- 常用模板
- 风险偏好

#### 2. Project Memory
项目级上下文：
- 项目定位
- 目标用户
- 竞品池
- 术语表
- 关键事实

#### 3. Task Session State
当前任务状态：
- 当前目标
- 当前阶段
- 研究计划
- 已收集证据
- 草稿产物

#### 4. Node Scratchpad
节点局部临时推理：
- planner 的候选方案
- skill 的中间结果
- verifier 的局部判断

**默认不共享。**

#### 5. Immutable Evidence Store
原始证据：
- 网页抓取结果
- GitHub 返回结果
- 文档片段
- 截图 / 解析内容

### 优势
- 更稳定
- 更容易 debug
- 更容易定位错误
- 更适合回归测试

### 缺点
- 实现复杂度更高
- 需要明确读写规则

---

## 核心原则三：记忆压缩（Memory Compression）

### 为什么需要
不是所有历史都值得一直带着。  
长上下文不是越长越好，很多时候只是更脏。

### 我们的做法
不是保留完整聊天历史，而是做两种压缩：

#### A. 事实压缩
把稳定事实压成结构化记忆：
- confirmed facts
- user preference
- chosen direction
- rejected options

#### B. 阶段摘要
每个阶段结束后，只保留：
- 关键结论
- 未解决问题
- 下一步输入

### 优势
- 降低 token 消耗
- 提高后续节点输入质量
- 更容易做状态恢复

### 缺点
- 压缩策略不好会丢信息
- 需要区分“事实”和“推测”

---

## 核心原则四：RAG 不是主角，而是能力层

### 为什么这样说
如果把 RAG 当系统中心，就又回到了玩具 QA。

### RAG 在这里的角色
RAG 只负责：
- 查询本地知识库
- 提供文档证据
- 给 research 提供私有上下文

它不负责：
- 决定流程
- 决定最终输出结构
- 决定阶段切换

### 优势
- 保留原项目资产价值
- 让系统具备私有知识能力
- 便于扩展到文件 / 项目级研究

### 缺点
- 如果过度依赖向量检索，容易误召回
- 需要配合 metadata 和 reranking

---

## 核心原则五：Skills 是能力单元，不是大黑箱

### 正确的 skill 设计
skill 分三类：

#### 1. Primitive Skills
最小能力：
- `web_search`
- `fetch_page`
- `github_repo_search`
- `read_readme`
- `docs_lookup`
- `xhs_browser_search`
- `extract_pricing`

#### 2. Composite Skills
组合能力：
- `competitor_scan`
- `repo_due_diligence`
- `product_research_pack`
- `community_painpoint_mining`

#### 3. Action Skills
有副作用动作：
- `create_issue_bundle`
- `save_report`
- `enqueue_monitoring_job`

### 优势
- 可组合
- 可测试
- 易替换
- 易接 workflow

### 缺点
- skill 设计不好会导致边界混乱
- 非官方平台 skill 稳定性差

---

## 4. 整体架构

## 总体形态
这是一个**状态驱动（state-driven）的 research workflow system**。

它不是：
- 多个 agent 自由群聊
- 纯 RAG QA
- 一个巨大的全能 agent

它是：
- 一个主编排器
- 少量关键 LLM 节点
- 一组 skills / collectors
- 一个共享状态层
- 一个证据层
- 一个交付层

---

## 顶层流程

### Stage 0：Intake / Scope Guard
**输入**
- 用户 idea
- 目标
- 约束
- 期望产出

**输出**
- `task_brief`
- `success_criteria`
- `scope_limit`

### Stage 1：Clarification
主动多轮问询，把模糊问题压成明确任务。

**输出**
- `task_spec`
- `must_cover_dimensions`
- `missing_info`

### Stage 2：Optional Brainstorm
只在需要发散时触发。  
**不是默认开启。**

**输出**
- candidate directions
- research dimensions
- risk hypotheses

### Stage 3：Planner
决定：
- 用哪个 workflow
- 走哪些 skills
- 哪些可并行
- 输出什么 artifact

### Stage 4：Parallel Collectors / Research Workers
例如：
- `web_research`
- `github_search`
- `docs_lookup`
- `xhs_search`
- `local_rag_lookup`

### Stage 5：Normalize / Evidence Judge
统一数据结构，去重、打分、识别缺口。

### Stage 6：Synthesizer
统一输出：
- 结论
- 证据
- 风险
- 建议

### Stage 7：Artifact Generator
生成：
- competitor matrix
- MVP spec
- issue list
- launch checklist

### Stage 8：Action Gate
外部动作统一在这里执行，默认人工确认。

### Stage 9：Memory Commit
只把确认后的稳定事实写进长期记忆。

---

## 这个架构的本质
一句话：

> 它本质上是一个 DAG / workflow 系统，里面只在必要的地方使用 agent，而不是把所有步骤都 agent 化。

这是它和“agent 炫技 demo”的关键区别。

---

## 5. 技术选型

## 后端
### FastAPI
负责：
- API 服务
- artifact 输出
- workflow 触发入口
- skill 服务暴露

### 适合原因
- async 友好
- 文档清晰
- 工程实现快

---

## 编排层
### LangGraph（MVP）
适合做：
- DAG
- checkpoint
- stateful workflow
- 人工确认点
- 长任务恢复

### 为什么先不用更重的
第一版更需要的是：
- 快速迭代
- 结构清晰
- 容易调试

而不是超复杂的生产调度。

### 第二阶段再考虑
- Temporal
- 更复杂的队列和长任务系统

---

## 数据层
### PostgreSQL + pgvector
Postgres 存：
- task state
- artifacts
- logs
- memory
- evidence metadata

pgvector 存：
- embeddings
- 相似片段检索

### 优势
- 一个库搞定大部分需求
- 状态与证据容易 join
- 工程上稳定

---

## 事件层
### Redis Streams
用来做：
- 状态广播
- 任务队列
- 节点异步通知

---

## 浏览器层
### Playwright
只用于：
- 没有稳定 API 的站点
- 需要半自动浏览器采集的 skill

### 注意
第一版只做**只读**。  
不做自动发帖 / 自动运营闭环。

---

## LLM 接入
### provider-agnostic
不要把系统绑定到某一个模型上。  
应该支持：

- 强推理模型做 planner / critic
- 普通模型做摘要 / 模板化生成
- 成熟 deep research 能力作为底层能力接入

### 战略定位
不是跟成熟 Deep Research 正面对打，  
而是把成熟 research 能力当底层，自己做：
- 状态管理
- skill 编排
- 上层 workflow
- artifact 化交付

---

## 工具协议层
### MCP
适合接：
- GitHub
- docs
- internal knowledge
- 自定义工具

但不要把整个系统都理解成 MCP 项目。  
MCP 是连接层，不是 workflow 大脑。

---

## 观测层
### OpenTelemetry + 自定义 run trace
记录：
- 每个节点耗时
- token 用量
- skill 调用
- 失败原因
- 哪条边触发

这对面试和回归测试都很重要。

---

## 6. 可量化指标、Baseline、回归测试

这是你项目从“好看”变成“像技术项目”的关键。

---

## 6.1 Baseline 怎么设

至少对比这 4 个基线：

### Baseline A：直接和 GPT 聊天
用户手动聊天。  
没有 workflow，没有 state，没有 skill 编排。

### Baseline B：单 Agent + Tools
一个 agent 自己决定：
- 检索
- 搜索
- 总结
- 输出

### Baseline C：线性 Pipeline
固定步骤：
- clarify
- search
- summarize
- output

### Baseline D：完整系统
完整流程：
- clarification
- optional brainstorm
- planner
- research workers
- synthesis
- artifact generation

---

## 6.2 Ablation Study 怎么做

要证明你的设计不是花哨，必须拆模块看效果。

### Ablation 1：去掉 Clarification
观察：
- 任务跑偏率
- 用户补充轮数
- 最终满意度

### Ablation 2：去掉 Brainstorm
观察：
- 模糊任务是否更容易漏维度
- 输出是否更保守

### Ablation 3：去掉 Context Isolation
观察：
- 节点污染率
- 结论重复 / 矛盾率
- 无关信息带入率

### Ablation 4：去掉 Evidence Judge
观察：
- 引用质量
- 错误结论比例
- source quality 是否明显下降

### Ablation 5：去掉 Artifact Layer
观察：
- 用户是否更难把结果转成下一步动作

---

## 6.3 核心量化指标

### 一）结果质量（Quality）
- **Coverage Score**：是否覆盖用户要求的维度
- **Factual Correctness**：事实正确率
- **Evidence Support Rate**：关键结论有证据支撑的比例
- **Actionability Score**：输出能否直接转成任务 / 执行项
- **Usefulness Rating**：人工打分

### 二）过程质量（Process）
- **Clarification Efficiency**：平均需要几轮问询
- **Duplicate Work Rate**：重复检索 / 重复分析比例
- **Context Pollution Rate**：无关上下文进入后续节点的比例
- **Branch Efficiency**：并行节点中真正有价值的比例

### 三）系统成本（Cost）
- **Total Token Usage**
- **Latency**
- **Tool Call Count**
- **External API Cost**
- **Average Cost per Deliverable**

### 四）稳定性（Stability）
- **Success Rate**
- **Retry Rate**
- **Recovery Success Rate**
- **Deterministic Output Similarity**：同输入多次运行结果相似度

### 五）产品体验（UX）
- **User Edit Distance**：用户需要手动改动多少
- **Time-to-First-Useful-Artifact**
- **Abandonment Rate**
- **Over-questioning Rate**：用户认为“问太多”的比例

---

## 6.4 如何直观说明“为什么比直接聊天更好”

### A. 语言说明
可以直接这样说：

> 直接聊天适合快速问题；我们的系统适合多阶段、多来源、要结构化交付件的任务。它的优势不是更会聊天，而是更会把研究过程拆成稳定的可执行工作流。

### B. 直观例子
任务：
> 我想做一个留学生求职产品，帮我分析竞品、需求和 MVP

直接聊天通常得到的是：
- 一段不错的分析
- 但证据不稳定
- 输出结构不固定
- 不容易接下一步

你的系统应该输出：
- 明确 task spec
- 竞品表
- 用户痛点证据
- MVP spec
- issue list
- 待验证假设

### C. 量化对比
例如：

| 指标 | Direct Chat | Single Agent | Our System |
|---|---:|---:|---:|
| 覆盖维度数 | 低/中 | 中 | 高 |
| 证据支撑率 | 低 | 中 | 高 |
| 可直接执行的产物数量 | 低 | 中 | 高 |
| 平均成本 | 低 | 中 | 高 |
| 用户后续修改量 | 高 | 中 | 低 |

重点不是所有指标都赢，  
而是诚实地说明：

> 我们用更高成本，换来了更高的结构化交付能力和更低的后续人工整理成本。

---

## 6.5 回归测试怎么做

### 测试集要固定
做一个固定任务集，例如 20～50 个任务，覆盖：

- idea → research
- repo due diligence
- framework comparison
- community pain-point mining
- MVP planning

### 每次改动后跑三类测试

#### 1. Functional Regression
看 workflow 是否跑通：
- 节点是否触发正确
- artifact 是否生成
- memory 是否更新正确

#### 2. Quality Regression
看质量分数是否下降：
- coverage
- evidence support
- actionability

#### 3. Cost Regression
看成本是否失控：
- token
- latency
- tool calls

### 再加 1 个 golden set
选 5～10 个最重要任务做人审基准，  
每次版本迭代抽样对比。

---

## 7. MVP 边界

第一版必须收敛，不然一定会烂。

## 第一版定位
**独立开发者产品研究与落地助手**

## 第一版 skills
- web research
- GitHub search
- docs / file RAG
- competitor matrix
- MVP spec generator
- issue bundle generator

## 第一版不要做
- 自动发帖
- 自动评论
- 自动运营闭环
- 复杂多账号自动登录
- 万能 browser agent

## 第一版最强交付物
- research brief
- competitor matrix
- MVP spec
- task / issue list

---

## 8. 最终项目定义

### 正式定义
一个面向独立开发与产品探索的、**skill-based 的 research workflow system**。  
它接收模糊想法或研究任务，通过 clarification、可选 brainstorming、stateful research orchestration、evidence judging 和 artifact generation，把开放式研究过程转化为结构化、可追溯、可执行的交付件。

### 核心技术点
- workflow-first 架构
- context isolation
- memory compression
- RAG as capability layer
- skill composition
- state-driven DAG orchestration
- evidence-based synthesis
- measurable evaluation and regression testing

### 核心价值
它不是“比 GPT 更会聊天”，而是：

- 更适合多阶段任务
- 更适合多源整合
- 更适合产出结构化交付件
- 更可追溯
- 更可复现
- 更能接后续动作

### 核心代价
- 更重
- 更贵
- 更复杂
- 对简单任务不划算

这个代价必须承认，承认了反而更像工程师。