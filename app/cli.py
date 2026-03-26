from __future__ import annotations

import argparse
import json

from app.llm import LLMSettings, OpenAICompatibleClient
from app.repository import RunRepository
from app.schemas import ArtifactType, RunCreateRequest
from app.service import WorkflowService
from app.settings import load_settings


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the ScopeForge workflow from the command line.")
    parser.add_argument("idea", help="The product idea or research task.")
    parser.add_argument("--goal", action="append", default=[], help="Goal for the run. Repeatable.")
    parser.add_argument("--constraint", action="append", default=[], help="Constraint for the run. Repeatable.")
    parser.add_argument(
        "--artifact",
        action="append",
        choices=[artifact.value for artifact in ArtifactType],
        help="Requested artifact type. Repeatable.",
    )
    args = parser.parse_args()

    request = RunCreateRequest(
        idea=args.idea,
        goals=args.goal,
        constraints=args.constraint,
        desired_artifacts=[ArtifactType(value) for value in args.artifact] if args.artifact else list(ArtifactType),
    )
    settings = load_settings()
    service = WorkflowService(
        RunRepository(settings.database_path),
        llm_client=OpenAICompatibleClient(
            LLMSettings(
                use_llm=settings.use_llm,
                api_key=settings.api_key,
                base_url=settings.base_url,
                model=settings.model,
                timeout_seconds=settings.timeout_seconds,
            )
        ),
    )
    created = service.create_run(request)
    detail = service.get_run(created.run_id)
    print(json.dumps(detail.model_dump(mode="json"), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
