from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_homepage_serves_frontend() -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert "ScopeForge" in response.text
    assert "Run the actual workflow." in response.text


def test_create_run_generates_artifacts_and_trace(tmp_path: Path) -> None:
    local_doc = tmp_path / "notes.md"
    local_doc.write_text("# Notes\nUseful competitor hints.", encoding="utf-8")

    response = client.post(
        "/runs",
        json={
            "idea": "Build a workflow-based research assistant for indie makers validating product ideas.",
            "goals": ["Find competitors", "Shape MVP"],
            "constraints": ["Keep it API first", "Avoid heavy multi-agent complexity"],
            "optional_sources": [
                {"kind": "url", "value": "https://example.com/market"},
                {"kind": "github_repo", "value": "https://github.com/example/project"},
                {"kind": "local_doc", "value": str(local_doc)},
            ],
        },
    )
    assert response.status_code == 200
    created = response.json()
    detail = client.get(f"/runs/{created['run_id']}")
    assert detail.status_code == 200
    payload = detail.json()
    assert payload["status"] == "completed"
    assert payload["current_stage"] == "ArtifactGenerator"
    assert len(payload["artifact_summary"]) == 4
    assert len(payload["trace"]) >= 5
    assert any(item["skill"] == "local_docs_lookup" for item in payload["evidence_summary"])


def test_ambiguous_request_triggers_brainstorm() -> None:
    response = client.post(
        "/runs",
        json={"idea": "做一个AI产品", "goals": [], "constraints": []},
    )
    assert response.status_code == 200
    run_id = response.json()["run_id"]
    detail = client.get(f"/runs/{run_id}")
    payload = detail.json()
    assert "OptionalBrainstorm" in payload["stage_history"]


def test_unknown_run_returns_404() -> None:
    response = client.get("/runs/run_missing")
    assert response.status_code == 404
