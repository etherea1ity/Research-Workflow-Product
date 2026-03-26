from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any, TypedDict
from uuid import uuid4

from langgraph.graph import END, START, StateGraph

from app.llm import OpenAICompatibleClient
from app.schemas import ArtifactRecord, ArtifactType, RunCreateRequest, RunMetrics
from app.skills import competitor_scan, fetch_page, github_repo_search, local_docs_lookup, web_search
from app.tracing import stage_trace


class WorkflowState(TypedDict, total=False):
    run_id: str
    request: RunCreateRequest
    status: str
    current_stage: str
    stage_history: list[str]
    project_profile: dict[str, Any]
    task_state: dict[str, Any]
    scratchpad: dict[str, Any]
    evidence_store: list[dict[str, Any]]
    artifacts: list[dict[str, Any]]
    trace: list[dict[str, Any]]
    metrics: dict[str, Any]
    evaluation_plan: dict[str, Any]
    started_at: str
    error: str | None


def _append_trace(state: WorkflowState, trace_record: dict[str, Any]) -> list[dict[str, Any]]:
    return [*state.get("trace", []), trace_record]


def _base_metrics(evidence_count: int, artifact_count: int, started_at: str) -> dict[str, Any]:
    started = datetime.fromisoformat(started_at)
    latency_ms = round((datetime.now(UTC) - started).total_seconds() * 1000, 3)
    return RunMetrics(
        coverage_score=min(1.0, 0.45 + artifact_count * 0.1 + evidence_count * 0.03),
        evidence_support_rate=min(1.0, evidence_count / max(artifact_count * 2, 1)),
        actionability_score=min(1.0, 0.4 + artifact_count * 0.12),
        total_token_usage=250 + evidence_count * 65 + artifact_count * 120,
        latency_ms=latency_ms,
        user_edit_distance=max(0.1, round(0.8 - artifact_count * 0.1, 3)),
    ).model_dump()


def _is_verifiable_source(source: str) -> bool:
    if source.startswith(("http://", "https://")):
        return True
    if source.startswith("synthetic://"):
        return False
    return Path(source).exists()


def intake_node(state: WorkflowState) -> WorkflowState:
    with stage_trace("Intake", {"rule": "normalize user request"}) as trace:
        request = state["request"]
        project_profile = {
            "product_mode": "product_research_to_mvp",
            "audience": "indie_developer",
            "workflow_mode": "mvp",
            "default_artifacts": [artifact.value for artifact in request.desired_artifacts],
        }
        task_state = {
            "task_brief": request.idea.strip(),
            "success_criteria": request.goals or ["Produce structured MVP planning artifacts."],
            "scope_limit": request.constraints or ["Stay within lightweight workflow MVP boundaries."],
        }
        trace.details["goal_count"] = len(request.goals)
    return {
        **state,
        "current_stage": "Intake",
        "stage_history": [*state.get("stage_history", []), "Intake"],
        "project_profile": project_profile,
        "task_state": task_state,
        "trace": _append_trace(state, trace.trace_record.model_dump()),
    }


def clarification_node(state: WorkflowState) -> WorkflowState:
    with stage_trace("Clarification", {"rule": "detect ambiguity and stabilize scope"}) as trace:
        request = state["request"]
        ambiguity_signals = []
        if len(request.idea) < 40:
            ambiguity_signals.append("idea_too_short")
        if not request.goals:
            ambiguity_signals.append("missing_goals")
        if not request.constraints:
            ambiguity_signals.append("missing_constraints")
        needs_brainstorm = len(ambiguity_signals) >= 2
        clarified_task = {
            "task_spec": {
                "problem_statement": request.idea,
                "must_cover_dimensions": [
                    "target_user",
                    "competitors",
                    "mvp_scope",
                    "execution_next_steps",
                ],
                "missing_info": ambiguity_signals,
            },
            "needs_brainstorm": needs_brainstorm,
            "clarification_notes": (
                "Brainstorm is recommended because the request is still broad."
                if needs_brainstorm
                else "The request is specific enough to continue directly into research."
            ),
        }
        trace.details["needs_brainstorm"] = needs_brainstorm
    return {
        **state,
        "current_stage": "Clarification",
        "stage_history": [*state.get("stage_history", []), "Clarification"],
        "task_state": {**state.get("task_state", {}), **clarified_task},
        "trace": _append_trace(state, trace.trace_record.model_dump()),
    }


def brainstorm_node(state: WorkflowState) -> WorkflowState:
    with stage_trace("OptionalBrainstorm", {"rule": "only for ambiguous requests"}) as trace:
        request = state["request"]
        scratchpad = {
            "candidate_directions": [
                f"Evidence-first positioning for {request.idea[:60]}",
                f"Lean MVP scope for {request.idea[:60]}",
                f"Execution-focused workflow for {request.idea[:60]}",
            ],
            "risk_hypotheses": [
                "Scope may be too broad for the first release.",
                "The user may need stronger differentiation from direct chat tools.",
            ],
        }
        trace.details["candidate_count"] = len(scratchpad["candidate_directions"])
    return {
        **state,
        "current_stage": "OptionalBrainstorm",
        "stage_history": [*state.get("stage_history", []), "OptionalBrainstorm"],
        "scratchpad": scratchpad,
        "trace": _append_trace(state, trace.trace_record.model_dump()),
    }


def research_collectors_node(state: WorkflowState) -> WorkflowState:
    with stage_trace("ResearchCollectors", {"skills": []}) as trace:
        request = state["request"]
        evidence = []
        skill_names = []
        for skill_name, produced in [
            ("web_search", web_search(request)),
            ("fetch_page", fetch_page(request.optional_sources)),
            ("github_repo_search", github_repo_search(request.optional_sources)),
            ("local_docs_lookup", local_docs_lookup(request.optional_sources)),
            ("competitor_scan", competitor_scan(request)),
        ]:
            if produced:
                evidence.extend([item.model_dump() for item in produced])
                skill_names.append(skill_name)
        trace.details["skills"] = skill_names
        trace.details["evidence_count"] = len(evidence)
    return {
        **state,
        "current_stage": "ResearchCollectors",
        "stage_history": [*state.get("stage_history", []), "ResearchCollectors"],
        "evidence_store": evidence,
        "trace": _append_trace(state, trace.trace_record.model_dump()),
    }


def synthesis_node(state: WorkflowState) -> WorkflowState:
    with stage_trace("Synthesis", {"rule": "merge evidence into decision-ready summary"}) as trace:
        evidence = state.get("evidence_store", [])
        evidence_ids = [
            item["evidence_id"] for item in evidence if _is_verifiable_source(str(item.get("source", "")))
        ]
        summary = {
            "conclusion": "A workflow-first MVP is justified because the task requires repeatable structured outputs.",
            "key_evidence": evidence_ids[:6],
            "risks": [
                "Too much clarification can hurt UX.",
                "Multi-agent complexity should stay optional for v1.",
            ],
            "next_actions": [
                "Lock the MVP artifact types.",
                "Keep brainstorm conditional and trace every stage.",
            ],
        }
        task_state = {**state.get("task_state", {}), "synthesis": summary}
        trace.details["linked_evidence"] = len(summary["key_evidence"])
    return {
        **state,
        "current_stage": "Synthesis",
        "stage_history": [*state.get("stage_history", []), "Synthesis"],
        "task_state": task_state,
        "trace": _append_trace(state, trace.trace_record.model_dump()),
    }


def artifact_generator_node(state: WorkflowState) -> WorkflowState:
    with stage_trace("ArtifactGenerator", {"rule": "all final outputs are generated here"}) as trace:
        request = state["request"]
        synthesis = state.get("task_state", {}).get("synthesis", {})
        evidence_ids = synthesis.get("key_evidence", [])
        artifacts = []
        for artifact_type in request.desired_artifacts:
            artifacts.append(
                ArtifactRecord(
                    artifact_type=artifact_type,
                    title=artifact_type.value.replace("_", " ").title(),
                    content=_artifact_content(artifact_type, state),
                    evidence_ids=evidence_ids,
                ).model_dump()
            )
        metrics = _base_metrics(
            evidence_count=len(state.get("evidence_store", [])),
            artifact_count=len(artifacts),
            started_at=state["started_at"],
        )
        trace.details["artifact_count"] = len(artifacts)
    return {
        **state,
        "status": "completed",
        "current_stage": "ArtifactGenerator",
        "stage_history": [*state.get("stage_history", []), "ArtifactGenerator"],
        "artifacts": artifacts,
        "metrics": metrics,
        "evaluation_plan": {
            "baselines": [
                "Direct Chat",
                "Single Agent + Tools",
                "Linear Pipeline",
                "Our Workflow MVP",
            ],
            "tracked_metrics": [
                "coverage_score",
                "evidence_support_rate",
                "actionability_score",
                "total_token_usage",
                "latency_ms",
                "user_edit_distance",
            ],
        },
        "trace": _append_trace(state, trace.trace_record.model_dump()),
    }


def _artifact_content(artifact_type: ArtifactType, state: WorkflowState) -> dict[str, Any]:
    request = state["request"]
    synthesis = state.get("task_state", {}).get("synthesis", {})
    competitor_titles = [
        item["title"] for item in state.get("evidence_store", []) if item["skill"] == "competitor_scan"
    ]
    if artifact_type is ArtifactType.RESEARCH_BRIEF:
        return {
            "problem": request.idea,
            "goals": request.goals,
            "conclusion": synthesis.get("conclusion"),
            "risks": synthesis.get("risks", []),
        }
    if artifact_type is ArtifactType.COMPETITOR_MATRIX:
        return {
            "dimensions": ["approach", "cost", "structure", "traceability"],
            "rows": competitor_titles,
        }
    if artifact_type is ArtifactType.MVP_SPEC:
        return {
            "workflow_stages": [
                "Intake",
                "Clarification",
                "OptionalBrainstorm",
                "ResearchCollectors",
                "Synthesis",
                "ArtifactGenerator",
            ],
            "must_have": [
                "trace every stage",
                "keep brainstorm conditional",
                "store evidence separately from synthesis",
            ],
        }
    return {
        "epics": [
            "Set up API and persistence",
            "Implement workflow graph",
            "Add evaluation fixtures",
        ],
        "next_actions": synthesis.get("next_actions", []),
    }


def should_brainstorm(state: WorkflowState) -> str:
    return "brainstorm" if state.get("task_state", {}).get("needs_brainstorm") else "research"


def build_workflow(llm_client: OpenAICompatibleClient | None = None):
    class _DisabledLLM:
        enabled = False

        def chat(self, system_prompt: str, user_prompt: str, temperature: float = 0.2) -> str:
            raise RuntimeError("LLM disabled")

    llm_client = llm_client or _DisabledLLM()

    def clarification_with_llm(state: WorkflowState) -> WorkflowState:
        updated = clarification_node(state)
        if not getattr(llm_client, "enabled", False):
            return updated
        task_spec = updated["task_state"]["task_spec"]
        prompt = (
            "You are clarifying a product research request for an indie developer.\n"
            f"Idea: {state['request'].idea}\n"
            f"Goals: {state['request'].goals}\n"
            f"Constraints: {state['request'].constraints}\n"
            f"Missing info: {task_spec['missing_info']}\n"
            "Write 3 concise sentences explaining the stabilized scope and whether brainstorm is necessary."
        )
        try:
            text = llm_client.chat(
                system_prompt="You turn broad product research requests into execution-ready scopes.",
                user_prompt=prompt,
            )
            updated["task_state"]["clarification_notes"] = text
        except Exception as exc:
            updated["task_state"]["llm_error"] = f"clarification: {exc}"
        return updated

    def brainstorm_with_llm(state: WorkflowState) -> WorkflowState:
        updated = brainstorm_node(state)
        if not getattr(llm_client, "enabled", False):
            return updated
        prompt = (
            "Given this product research task, propose 3 candidate directions and 2 key risks.\n"
            f"Idea: {state['request'].idea}\n"
            "Return plain text with short bullet lines."
        )
        try:
            text = llm_client.chat(
                system_prompt="You are helping shape lean product research directions.",
                user_prompt=prompt,
                temperature=0.4,
            )
            updated["scratchpad"]["llm_brainstorm"] = text
        except Exception as exc:
            updated["scratchpad"]["llm_error"] = f"brainstorm: {exc}"
        return updated

    def synthesis_with_llm(state: WorkflowState) -> WorkflowState:
        updated = synthesis_node(state)
        if not getattr(llm_client, "enabled", False):
            return updated
        evidence_lines = [
            f"- {item['title']}: {item['summary']}" for item in state.get("evidence_store", [])[:8]
        ]
        prompt = (
            "Synthesize the following evidence into a concise research summary for an indie developer.\n"
            f"Idea: {state['request'].idea}\n"
            "Evidence:\n"
            + "\n".join(evidence_lines)
            + "\nWrite a compact markdown summary with conclusion, risks, and next actions."
        )
        try:
            text = llm_client.chat(
                system_prompt="You produce evidence-based product research summaries.",
                user_prompt=prompt,
            )
            updated["task_state"]["synthesis"]["llm_summary"] = text
        except Exception as exc:
            updated["task_state"]["llm_error"] = f"synthesis: {exc}"
        return updated

    def artifact_generator_with_llm(state: WorkflowState) -> WorkflowState:
        updated = artifact_generator_node(state)
        if not getattr(llm_client, "enabled", False):
            return updated
        updated["task_state"]["synthesis"]["llm_summary_reference"] = updated["task_state"]["synthesis"].get(
            "llm_summary", ""
        )
        return updated

    graph = StateGraph(WorkflowState)
    graph.add_node("intake", intake_node)
    graph.add_node("clarification", clarification_with_llm)
    graph.add_node("brainstorm", brainstorm_with_llm)
    graph.add_node("research", research_collectors_node)
    graph.add_node("synthesis", synthesis_with_llm)
    graph.add_node("artifact_generator", artifact_generator_with_llm)
    graph.add_edge(START, "intake")
    graph.add_edge("intake", "clarification")
    graph.add_conditional_edges(
        "clarification",
        should_brainstorm,
        {"brainstorm": "brainstorm", "research": "research"},
    )
    graph.add_edge("brainstorm", "research")
    graph.add_edge("research", "synthesis")
    graph.add_edge("synthesis", "artifact_generator")
    graph.add_edge("artifact_generator", END)
    return graph.compile()


def initial_state(request: RunCreateRequest) -> WorkflowState:
    return {
        "run_id": f"run_{uuid4().hex[:12]}",
        "request": request,
        "status": "running",
        "current_stage": "queued",
        "stage_history": [],
        "project_profile": {},
        "task_state": {},
        "scratchpad": {},
        "evidence_store": [],
        "artifacts": [],
        "trace": [],
        "metrics": RunMetrics().model_dump(),
        "evaluation_plan": {},
        "started_at": datetime.now(UTC).isoformat(),
        "error": None,
    }
