from __future__ import annotations

from datetime import UTC, datetime
from time import perf_counter
from typing import Any

from app.schemas import TraceRecord


class StageTrace:
    def __init__(self, stage: str, details: dict[str, Any] | None = None) -> None:
        self.stage = stage
        self.details = details or {}
        self.status = "finished"
        self._started_at: datetime | None = None
        self._started_counter: float | None = None
        self.trace_record: TraceRecord | None = None

    def __enter__(self) -> "StageTrace":
        self._started_at = datetime.now(UTC)
        self._started_counter = perf_counter()
        return self

    def __exit__(self, exc_type, exc, exc_tb) -> None:
        if exc is not None:
            self.status = "failed"
        finished_at = datetime.now(UTC)
        duration_ms = round((perf_counter() - (self._started_counter or perf_counter())) * 1000, 3)
        self.trace_record = TraceRecord(
            stage=self.stage,
            started_at=self._started_at or finished_at,
            finished_at=finished_at,
            duration_ms=duration_ms,
            status=self.status,
            details=self.details,
        )


def stage_trace(stage: str, details: dict[str, Any] | None = None) -> StageTrace:
    return StageTrace(stage=stage, details=details)
