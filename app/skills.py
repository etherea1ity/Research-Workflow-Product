from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
from typing import Any
from urllib.parse import quote_plus
from uuid import uuid4

from app.schemas import EvidenceItem, RunCreateRequest, SourceInput


def _new_evidence(
    skill: str,
    title: str,
    summary: str,
    source: str,
    tags: Iterable[str],
    metadata: dict[str, Any] | None = None,
) -> EvidenceItem:
    return EvidenceItem(
        evidence_id=f"ev_{uuid4().hex[:10]}",
        skill=skill,
        title=title,
        summary=summary,
        source=source,
        tags=list(tags),
        metadata=metadata or {},
    )


def web_search(request: RunCreateRequest) -> list[EvidenceItem]:
    keywords = [request.idea, *request.goals[:2]]
    return [
        _new_evidence(
            skill="web_search",
            title=f"Market signal {index + 1}",
            summary=f"Derived research angle for: {keyword[:120]}",
            source=f"https://duckduckgo.com/?q={quote_plus(keyword)}",
            tags=["market", "web"],
            metadata={"query": keyword, "source_kind": "search_results_page"},
        )
        for index, keyword in enumerate(keywords)
    ]


def fetch_page(sources: list[SourceInput]) -> list[EvidenceItem]:
    return [
        _new_evidence(
            skill="fetch_page",
            title=f"Fetched page: {source.value}",
            summary="Captured page as supporting external reference.",
            source=source.value,
            tags=["external", "url"],
        )
        for source in sources
        if source.kind == "url"
    ]


def github_repo_search(sources: list[SourceInput]) -> list[EvidenceItem]:
    evidence: list[EvidenceItem] = []
    for source in sources:
        if source.kind != "github_repo":
            continue
        repo_name = source.value.rstrip("/").split("/")[-1]
        evidence.append(
            _new_evidence(
                skill="github_repo_search",
                title=f"Repository signal: {repo_name}",
                summary=f"Repository {repo_name} was included as a reference implementation or competitor.",
                source=source.value,
                tags=["github", "repo"],
            )
        )
    return evidence


def local_docs_lookup(sources: list[SourceInput]) -> list[EvidenceItem]:
    evidence: list[EvidenceItem] = []
    for source in sources:
        if source.kind != "local_doc":
            continue
        path = Path(source.value)
        if path.exists():
            preview = path.read_text(encoding="utf-8", errors="ignore")[:240]
            summary = f"Local document preview: {preview}" if preview else "Local document was available but empty."
        else:
            summary = "Local document path was provided but the file does not exist."
        evidence.append(
            _new_evidence(
                skill="local_docs_lookup",
                title=f"Local doc: {path.name}",
                summary=summary,
                source=str(path),
                tags=["local", "docs"],
                metadata={"exists": path.exists()},
            )
        )
    return evidence


def competitor_scan(request: RunCreateRequest) -> list[EvidenceItem]:
    baseline_names = [
        "Direct Chat",
        "Single Agent + Tools",
        "Linear Pipeline",
        "Workflow MVP",
    ]
    return [
        _new_evidence(
            skill="competitor_scan",
            title=f"Reference baseline: {name}",
            summary=f"Baseline candidate included for comparison against the workflow MVP in the context of {request.idea[:90]}",
            source=f"synthetic://baseline/{index}",
            tags=["baseline", "comparison"],
            metadata={"baseline": name},
        )
        for index, name in enumerate(baseline_names, start=1)
    ]
