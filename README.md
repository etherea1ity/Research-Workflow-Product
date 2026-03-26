# ScopeForge

一个面向独立开发者的、从产品研究走向 MVP 规划的 workflow-first 系统。

## Quick Start (前后端一起启动)

> 当前项目是前后端一体：前端由 FastAPI 挂载并提供 `GET /` 页面。

1. 安装依赖

```bash
python -m pip install -e .
```

2. 启动服务（同时包含后端 API + 前端页面）

```bash
python -m app.run_server
```

3. 打开地址

- 前端主页: `http://127.0.0.1:8010/`
- API 文档: `http://127.0.0.1:8010/docs`
- 健康检查: `http://127.0.0.1:8010/health`

## 配置位置（包括端口）

- 运行时配置优先从 `.env.local` 读取
- 配置解析逻辑在 `app/settings.py`
- 服务启动入口在 `app/run_server.py`

常用配置项：

- `RESEARCH_WORKFLOW_SERVER_HOST=127.0.0.1`
- `RESEARCH_WORKFLOW_SERVER_PORT=8010`
- `RESEARCH_WORKFLOW_SERVER_RELOAD=true`

当前版本包含：

- `FastAPI` API：`POST /runs`、`GET /runs/{run_id}`
- 商业化风格的 Web 前端：`GET /`
- `LangGraph` 6-stage workflow
- 轻量状态分层：`project_profile`、`task_state`、`scratchpad`、`evidence_store`
- 内置 trace、基础评估指标、artifact 输出
- 默认使用本地 SQLite 持久化

项目文档：

- [Product Foundation](docs/scopeforge-foundation.md)
- [Frontend Benchmark](docs/design-benchmark.md)

## Workflow Stages

1. `Intake`
2. `Clarification`
3. `OptionalBrainstorm`
4. `ResearchCollectors`
5. `Synthesis`
6. `ArtifactGenerator`

## Artifact Types

- `research_brief`
- `competitor_matrix`
- `mvp_spec`
- `issue_bundle`

## Run Locally

```bash
python -m app.run_server
```

可用接口：

- `GET /`
- `GET /health`
- `POST /runs`
- `GET /runs/{run_id}`

## CLI

```bash
python -m app.cli "Build a workflow-based product research assistant" --goal "Find competitors" --goal "Shape MVP"
```

## Example Request

```json
{
  "idea": "Build a workflow-based product research assistant for indie makers validating product ideas.",
  "goals": ["Find competitors", "Shape MVP"],
  "constraints": ["Keep it API first", "Avoid heavy multi-agent complexity"],
  "desired_artifacts": ["research_brief", "competitor_matrix", "mvp_spec", "issue_bundle"],
  "optional_sources": [
    {"kind": "url", "value": "https://example.com/market"},
    {"kind": "github_repo", "value": "https://github.com/example/project"},
    {"kind": "local_doc", "value": "C:/path/to/notes.md"}
  ]
}
```

## Tests

```bash
pytest
```
