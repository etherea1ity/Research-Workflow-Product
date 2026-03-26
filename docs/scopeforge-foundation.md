# ScopeForge Product Foundation

## Product Definition

### Working Name
`ScopeForge`

The name reflects what the product actually does: it clarifies scope, forges evidence into decisions, and turns research into execution-ready artifacts.

### One-Sentence Positioning
ScopeForge is a workflow-first research system for indie builders and product explorers who need to turn a fuzzy idea into evidence-backed MVP decisions.

### Formal Definition
ScopeForge accepts an open-ended product idea, diligence request, or exploratory research task and converts it into a structured, traceable workflow with evidence, synthesis, and execution-ready deliverables.

It is not designed to be a general chatbot. It is designed to move work forward.

## Why This Exists

### The Problem With Direct Chat
Direct chat is excellent for quick questions, rough brainstorming, and one-off comparisons. It gets weaker when the task becomes:

- multi-stage
- multi-source
- evidence-sensitive
- artifact-oriented
- hard to reproduce

In those situations, chat alone often creates four failure modes:

- unclear scope
- unstable outputs
- weak evidence traceability
- poor handoff into the next action

### ScopeForge Thesis
The product wins when the user needs:

- clarified task scope before execution
- research grounded in multiple sources
- stable deliverables instead of conversational replies
- a reusable project memory instead of disposable chat context

## Core Use Cases

### Idea to Research to MVP
For a founder with an early product idea who needs:

- target-user framing
- competitor discovery
- demand signals
- MVP scoping
- next-step issues

### Technical or Product Due Diligence
For evaluating a repo, framework, category, or product direction:

- research collection
- comparisons
- tradeoff analysis
- recommendation artifacts

### Execution Support After Research
For continuing from analysis into action:

- research brief
- competitor matrix
- MVP spec
- issue bundle
- launch or validation checklist

## Product Principles

### Workflow-First, Not Chat-First
The product is organized around stages, state transitions, and artifacts. Chat can be an entry surface, but it is not the system architecture.

Benefits:

- more stable task progression
- more predictable deliverables
- clearer evaluation and regression testing
- easier orchestration of tools and skills

Risk:

- if the flow is too heavy, the experience feels over-managed

### Context Isolation
This is the deepest technical differentiator in the product.

Without isolation, exploratory reasoning bleeds into evidence, temporary guesses leak into memory, and one task contaminates the next. ScopeForge separates context into distinct layers:

1. `Global User Profile`
2. `Project Memory`
3. `Task Session State`
4. `Node Scratchpad`
5. `Immutable Evidence Store`

Why it matters:

- keeps reasoning cleaner
- improves debuggability
- reduces cross-stage contamination
- makes regression evaluation more trustworthy

### Memory Compression
The product should not drag full raw history forever. It should keep:

- stable facts
- user preferences
- chosen directions
- rejected options
- stage summaries

This reduces token cost and improves later-stage signal quality.

### Evidence Before Synthesis
RAG and retrieval are not the product. They are capability layers inside the product.

The system should:

- collect evidence first
- normalize and judge it
- synthesize with explicit evidence links
- generate artifacts from the synthesis layer

This is the difference between a research workflow and a toy QA wrapper.

### Skills as Composable Units
Skills should be small, testable units with clear boundaries, not giant black boxes.

Suggested taxonomy:

- Primitive skills: `web_search`, `fetch_page`, `github_repo_search`, `docs_lookup`
- Composite skills: `competitor_scan`, `repo_due_diligence`, `community_painpoint_mining`
- Action skills: `create_issue_bundle`, `save_report`, `enqueue_monitoring_job`

## System Architecture

### Current MVP Shape In This Repository

- `FastAPI` for API and web entrypoints
- `LangGraph` for workflow orchestration
- `SQLite` for local run persistence
- provider-agnostic LLM client wrapper
- structured artifacts, traces, evidence, and metrics

### Target Architecture Direction
The original concept goes beyond the current MVP and points toward:

- `PostgreSQL + pgvector` for state, memory, and evidence retrieval
- `Redis Streams` for async events and long-running workflows
- `Playwright` for browser-based collection when no stable API exists
- `MCP` connectors for external tools and internal knowledge systems
- `OpenTelemetry` plus custom traces for observability

### Workflow Stages

1. `Intake`
2. `Clarification`
3. `OptionalBrainstorm`
4. `Planner`
5. `Parallel Collectors / Research Workers`
6. `Normalize / Evidence Judge`
7. `Synthesis`
8. `Artifact Generator`
9. `Action Gate`
10. `Memory Commit`

The current codebase implements a leaner MVP slice of that architecture:

1. `Intake`
2. `Clarification`
3. `OptionalBrainstorm`
4. `ResearchCollectors`
5. `Synthesis`
6. `ArtifactGenerator`

## Technical Advantages

### Advantage 1: Context Isolation
Temporary reasoning does not automatically become long-term memory. Evidence does not collapse into summaries. This gives ScopeForge a stronger reliability story than free-form agent demos.

### Advantage 2: Traceable Outputs
Every run carries stage history, evidence summaries, artifacts, and trace records. That makes the system explainable to the user and debuggable for the builder.

### Advantage 3: Artifact-Centric Design
The system is optimized to output documents that are easy to hand off:

- `research_brief`
- `competitor_matrix`
- `mvp_spec`
- `issue_bundle`

### Advantage 4: Measurable Workflow Quality
The architecture is designed to support baseline comparisons, ablation studies, and regression testing instead of relying on vibes.

Suggested tracked metrics:

- coverage score
- evidence support rate
- actionability score
- total token usage
- latency
- user edit distance
- over-questioning rate

## What ScopeForge Is Not

- not a general chatbot
- not a single giant autonomous agent
- not a pure RAG question-answering app
- not an automation-heavy posting bot
- not a browser agent that tries to do everything

## MVP Boundary

### Must-Have Capabilities

- workflow entry from a product idea or research task
- structured clarification
- evidence collection from multiple sources
- synthesis with explicit risks and next actions
- artifact generation for planning and execution
- trace and evaluation data for every run

### Must-Not-Have In V1

- automatic posting
- automatic growth loops
- complex multi-account automation
- over-engineered multi-agent choreography
- broad browser autonomy without tight constraints

## Why The Product Can Feel Commercial
The UI should not present ScopeForge as a lab experiment. The product story is strong enough for a premium commercial interface because it has:

- a clear user
- a clear job to be done
- a differentiated technical thesis
- a visible workflow
- concrete deliverables

The frontend should therefore communicate:

- confidence, not gimmicks
- evidence, not fluff
- premium craft, not generic SaaS boilerplate

## Current Repository Deliverables

- API endpoints for creating and reading workflow runs
- local persistence for runs
- workflow stage trace output
- evidence and artifact summaries
- a commercial-style web frontend layered on top of the existing APIs

## Summary
ScopeForge is best understood as a research-to-execution operating layer for product work. It sits between raw AI capability and real product decision-making, and its strongest defensibility comes from workflow structure, evidence handling, and context discipline.
