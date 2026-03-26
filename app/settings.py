from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _load_local_env() -> None:
    for filename in (".env.local", ".env"):
        path = Path(filename)
        if not path.exists():
            continue
        for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or "=" not in stripped:
                continue
            key, value = stripped.split("=", 1)
            normalized_key = key.strip().lstrip("\ufeff")
            os.environ.setdefault(normalized_key, value.strip())


@dataclass(frozen=True)
class Settings:
    app_name: str = "ScopeForge"
    database_path: str = str(Path("data") / "research_workflow.db")
    server_host: str = "127.0.0.1"
    server_port: int = 8010
    server_reload: bool = True
    use_llm: bool = False
    api_key: str = ""
    base_url: str = "https://coding.dashscope.aliyuncs.com/v1"
    model: str = "qwen3.5-plus"
    timeout_seconds: int = 60


def load_settings() -> Settings:
    _load_local_env()
    return Settings(
        database_path=os.getenv("DATABASE_PATH", str(Path("data") / "research_workflow.db")),
        server_host=os.getenv("RESEARCH_WORKFLOW_SERVER_HOST", "127.0.0.1"),
        server_port=int(os.getenv("RESEARCH_WORKFLOW_SERVER_PORT", "8010")),
        server_reload=os.getenv("RESEARCH_WORKFLOW_SERVER_RELOAD", "true").lower() == "true",
        use_llm=os.getenv("RESEARCH_WORKFLOW_USE_LLM", "false").lower() == "true",
        api_key=os.getenv("RESEARCH_WORKFLOW_API_KEY", ""),
        base_url=os.getenv("RESEARCH_WORKFLOW_BASE_URL", "https://coding.dashscope.aliyuncs.com/v1"),
        model=os.getenv("RESEARCH_WORKFLOW_MODEL", "qwen3.5-plus"),
        timeout_seconds=int(os.getenv("RESEARCH_WORKFLOW_TIMEOUT_SECONDS", "60")),
    )
