from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.llm import LLMSettings, OpenAICompatibleClient
from app.repository import RunRepository
from app.schemas import RunCreateRequest, RunCreatedResponse, RunDetailResponse
from app.service import WorkflowService
from app.settings import load_settings

settings = load_settings()
repository = RunRepository(settings.database_path)
llm_client = OpenAICompatibleClient(
    LLMSettings(
        use_llm=settings.use_llm,
        api_key=settings.api_key,
        base_url=settings.base_url,
        model=settings.model,
        timeout_seconds=settings.timeout_seconds,
    )
)
service = WorkflowService(repository, llm_client=llm_client)
static_dir = Path(__file__).resolve().parent / "static"

app = FastAPI(title=settings.app_name, version="0.2.0")
app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/", include_in_schema=False)
def home() -> FileResponse:
    return FileResponse(static_dir / "index.html")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/runs", response_model=RunCreatedResponse)
def create_run(request: RunCreateRequest) -> RunCreatedResponse:
    return service.create_run(request)


@app.get("/runs/{run_id}", response_model=RunDetailResponse)
def get_run(run_id: str) -> RunDetailResponse:
    record = service.get_run(run_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Run not found")
    return record
