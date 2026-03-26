# ScopeForge Frontend Benchmark

Date: 2026-03-25

## Goal
Benchmark current premium AI product pages and builder interfaces so ScopeForge feels commercial-grade instead of like an internal demo.

## Primary Reference Set

### Cursor
URL: https://cursor.com/

Signals worth borrowing:

- interactive hero instead of static illustration
- product demo shown immediately in the first screen
- strong productivity language tied to visible workflows
- premium trust framing with testimonials and proof points
- “agent work in progress” presentation that makes invisible AI labor legible

### v0
URL: https://v0.dev/

Signals worth borrowing:

- prompt-first entry right on the homepage
- templates as acceleration rails instead of burying the first action
- dashboards, landing pages, and components treated as visible starting points
- clear “prompt, build, publish” language that compresses complexity
- design-system messaging that makes the product feel production-oriented

### Bolt
URL: https://bolt.new/

Signals worth borrowing:

- immediate builder CTA with “What will you build today?”
- strong value framing around fewer errors and less tool switching
- integrated-platform story instead of fragmented-tool story
- commercial emphasis on scale, backend, auth, hosting, and SEO

### Dia
URL: https://www.diabrowser.com/

Signals worth borrowing:

- use-case storytelling grouped by user intent
- browser-native framing that feels ambient, not modal
- task categories like writing, learning, planning, shopping
- tight pairing of scenario copy with product snapshots

### Genspark Browser
URL: https://www.genspark.ai/browser

Signals worth borrowing:

- capability-heavy positioning with clear feature pillars
- browser, agent, and MCP concepts explained in product language
- strong sense that the product is an operating surface, not a single tool

### Manus
URL: https://manus.im/

Signals worth borrowing:

- broad “What can I do for you?” framing
- product universe expansion through multiple surfaces and integrations
- premium positioning supported by trust center, API, playbooks, and business navigation

## Patterns Repeated Across The Market

### 1. The Hero Is A Working Surface
The top of the page is no longer a passive marketing banner. The best AI products show:

- a prompt box
- a live workspace
- a staged task list
- or an interactive result frame

Implication for ScopeForge:
The hero should already look like a research cockpit, not a brochure.

### 2. The Product Is Explained Through Workflows
The strongest products make AI work visible through:

- steps
- stages
- agent state
- tasks in progress
- output cards

Implication for ScopeForge:
Show the research pipeline, artifact outputs, and evidence layers as first-class UI objects.

### 3. Use Cases Are More Convincing Than Abstract Claims
Commercial AI sites explain value through scenario clusters instead of generic feature bullets.

Implication for ScopeForge:
Show concrete flows such as:

- idea to MVP
- repo due diligence
- market scan
- execution planning

### 4. Trust Is Built Through Structure
Premium AI products signal seriousness with:

- product nav depth
- proofs and metrics
- quality claims tied to visible systems
- integration surfaces
- enterprise and security framing

Implication for ScopeForge:
Do not only say “AI research workflow.” Show traces, evidence, metrics, and artifact types.

### 5. Templates Reduce Blank-Page Anxiety
Products like v0 front-load templates and starter prompts.

Implication for ScopeForge:
Provide scenario presets and sample inputs directly in the workspace composer.

## UI Direction For ScopeForge

### Visual Direction

- editorial display typography with a sharper interface font for the app shell
- warm light background with dark workspace surfaces
- copper and mineral-teal accents instead of generic purple neon
- layered gradients, soft grids, and depth-based cards

### Information Architecture

1. Narrative hero
2. Product thesis and technical edge
3. Context-isolation explainer
4. Workflow-stage visualization
5. Interactive workspace connected to real APIs
6. Artifact, evidence, trace, and metrics rendering

### Product Framing
ScopeForge should be presented as a “research operating system” or “workflow cockpit” for product discovery, not as a chatbot skin over a REST API.

## Practical Rules For Implementation

- The first screen must contain a real prompt composer or visible run surface.
- The UI must render actual evidence, artifacts, and trace data from the backend.
- The page should explain why structured workflow beats direct chat for multi-stage work.
- The experience should feel production-oriented even without a JavaScript framework.
- Motion should support comprehension, not distract from it.

## Source Notes
The benchmark above is based on current official product pages:

- Cursor: https://cursor.com/
- v0: https://v0.dev/
- Bolt: https://bolt.new/
- Dia: https://www.diabrowser.com/
- Genspark Browser: https://www.genspark.ai/browser
- Manus: https://manus.im/
