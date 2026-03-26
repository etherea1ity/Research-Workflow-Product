from __future__ import annotations

from datetime import UTC, datetime

from app.llm import OpenAICompatibleClient
from app.repository import RunRepository
from app.schemas import RunCreateRequest, RunCreatedResponse, RunDetailResponse, RunRecord
from app.workflow import build_workflow, initial_state


class WorkflowService:
    def __init__(self, repository: RunRepository, llm_client: OpenAICompatibleClient | None = None) -> None:
        self.repository = repository
        self.workflow = build_workflow(llm_client=llm_client)

    def create_run(self, request: RunCreateRequest) -> RunCreatedResponse:
        state = initial_state(request)
        try:
            result = self.workflow.invoke(state)
            status = result.get("status", "completed")
            error = None
        except Exception as exc:  # pragma: no cover
            result = state
            result["status"] = "failed"
            result["current_stage"] = result.get("current_stage", "unknown")
            result["error"] = str(exc)
            status = "failed"
            error = str(exc)

        record = RunRecord(
            run_id=result["run_id"],
            status=status,
            current_stage=result["current_stage"],
            created_at=datetime.fromisoformat(result["started_at"]),
            updated_at=datetime.now(UTC),
            request=request,
            stage_history=result.get("stage_history", []),
            project_profile=result.get("project_profile", {}),
            task_state=result.get("task_state", {}),
            scratchpad=result.get("scratchpad", {}),
            evidence_store=result.get("evidence_store", []),
            artifacts=result.get("artifacts", []),
            trace=result.get("trace", []),
            metrics=result.get("metrics", {}),
            evaluation_plan=result.get("evaluation_plan", {}),
            error=error or result.get("error"),
        )
        self.repository.upsert(record)
        return RunCreatedResponse(
            run_id=record.run_id,
            current_stage=record.current_stage,
            artifact_refs=[artifact.artifact_type for artifact in record.artifacts],
        )

    def get_run(self, run_id: str) -> RunDetailResponse | None:
        record = self.repository.get(run_id)
        if record is None:
            return None
        return RunDetailResponse(
            run_id=record.run_id,
            status=record.status,
            current_stage=record.current_stage,
            stage_history=record.stage_history,
            evidence_summary=record.evidence_store,
            artifact_summary=record.artifacts,
            trace=record.trace,
            metrics=record.metrics,
            task_state=record.task_state,
            evaluation_plan=record.evaluation_plan,
            error=record.error,
        )
