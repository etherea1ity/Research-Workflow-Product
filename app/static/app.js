const presets = [
  {
    label: "Idea to MVP",
    idea: "Build a workflow-based research assistant for indie makers validating product ideas.",
    goals: ["Find competitors", "Shape MVP", "Keep evidence traceable"],
    constraints: ["Keep it API first", "Avoid heavy multi-agent complexity"],
    sources: [],
  },
  {
    label: "Repo diligence",
    idea: "Evaluate an open-source AI browser automation repo for whether it is viable as a base for a commercial research product.",
    goals: ["Assess architecture", "Compare alternatives", "Recommend adoption path"],
    constraints: ["Prefer maintainability", "Call out integration risk"],
    sources: [{ kind: "github_repo", value: "https://github.com/example/project" }],
  },
  {
    label: "Market scan",
    idea: "Research AI workflow tools for solo founders moving from idea validation to MVP planning.",
    goals: ["Map the market", "Find product gaps", "Propose a differentiated wedge"],
    constraints: ["Favor evidence over generic trend claims"],
    sources: [{ kind: "url", value: "https://example.com/market" }],
  },
];

const state = {
  goals: [],
  constraints: [],
  sources: [],
  artifacts: [],
  activeArtifactIndex: 0,
  logIntervalId: null,
  evidenceMap: {},
};

const $ = {
  main: document.querySelector("main"),
  presetRail: document.querySelector("#preset-rail"),
  ideaInput: document.querySelector("#idea-input"),
  goalInput: document.querySelector("#goal-input"),
  constraintInput: document.querySelector("#constraint-input"),
  goalTags: document.querySelector("#goal-tags"),
  constraintTags: document.querySelector("#constraint-tags"),
  sourceList: document.querySelector("#source-list"),
  addSource: document.querySelector("#add-source"),
  runForm: document.querySelector("#run-form"),
  submitRun: document.querySelector("#submit-run"),
  loadSample: document.querySelector("#load-sample"),
  runIdInput: document.querySelector("#run-id-input"),
  loadRun: document.querySelector("#load-run"),
  notice: document.querySelector("#notice"),
  resultsBody: document.querySelector("#results-body"),
  runStatus: document.querySelector("#run-status"),
  runIdDisplay: document.querySelector("#run-id-display"),
  currentStageDisplay: document.querySelector("#current-stage-display"),
  statusDisplay: document.querySelector("#status-display"),
  metricGrid: document.querySelector("#metric-grid"),
  timelineStrip: document.querySelector("#timeline-strip"),
  artifactCount: document.querySelector("#artifact-count"),
  artifactTabs: document.querySelector("#artifact-tabs"),
  artifactContent: document.querySelector("#artifact-content"),
  evidenceCount: document.querySelector("#evidence-count"),
  evidenceList: document.querySelector("#evidence-list"),
  taskState: document.querySelector("#task-state"),
  traceCount: document.querySelector("#trace-count"),
  traceList: document.querySelector("#trace-list"),
  liveLog: document.querySelector("#live-log"),
  liveLogStatus: document.querySelector("#live-log-status"),
};

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function setNotice(message, isError = false) {
  $.notice.textContent = message;
  $.notice.style.background = isError ? "rgba(188, 106, 44, 0.16)" : "rgba(255, 255, 255, 0.55)";
}

function setLoading(isLoading) {
  $.runForm.classList.toggle("loading", isLoading);
  $.submitRun.disabled = isLoading;
  $.loadRun.disabled = isLoading;
  $.runStatus.textContent = isLoading ? "Running" : "Ready";
}

function pushLog(level, message) {
  const row = document.createElement("div");
  row.className = "log-entry";
  row.innerHTML = `<small>${escapeHtml(level)}</small>${escapeHtml(message)}`;
  $.liveLog.prepend(row);
}

function clearLog() {
  $.liveLog.innerHTML = "";
}

function startLiveLog(payload) {
  stopLiveLog();
  clearLog();
  $.liveLogStatus.textContent = "Running";
  const steps = [
    `Scoping your request: ${payload.idea.slice(0, 70)}...`,
    "Clarifying goals and constraints into a stable task spec.",
    "Planning which collectors should run for this request.",
    "Collecting evidence from web/repo/page sources.",
    "Judging evidence quality and deduplicating findings.",
    "Synthesizing conclusions, risks, and next actions.",
    "Generating deliverables with evidence references.",
  ];
  let cursor = 0;
  pushLog("Start", "Workflow started. Building execution plan.");
  state.logIntervalId = window.setInterval(() => {
    pushLog("Step", steps[cursor % steps.length]);
    cursor += 1;
  }, 900);
}

function stopLiveLog() {
  if (state.logIntervalId !== null) {
    window.clearInterval(state.logIntervalId);
    state.logIntervalId = null;
  }
}

function renderLogFromTrace(trace) {
  stopLiveLog();
  clearLog();
  if (!trace || trace.length === 0) {
    $.liveLogStatus.textContent = "No trace";
    pushLog("Info", "No stage trace found for this run.");
    return;
  }
  $.liveLogStatus.textContent = "Completed";
  [...trace].reverse().forEach((entry) => {
    const detailBits = Object.entries(entry.details || {})
      .map(([key, value]) => `${key}=${Array.isArray(value) ? value.join(",") : value}`)
      .join(" | ");
    const line = `${entry.stage} (${Math.round(entry.duration_ms)} ms)${detailBits ? ` | ${detailBits}` : ""}`;
    pushLog(entry.status === "failed" ? "Error" : "Done", line);
  });
}

function renderPresetRail() {
  $.presetRail.innerHTML = "";
  presets.forEach((preset) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "preset-button";
    button.textContent = preset.label;
    button.addEventListener("click", () => applyPreset(preset));
    $.presetRail.appendChild(button);
  });
}

function renderTags(type) {
  const container = type === "goals" ? $.goalTags : $.constraintTags;
  container.innerHTML = "";
  state[type].forEach((item, index) => {
    const chip = document.createElement("div");
    chip.className = "tag-chip";
    chip.innerHTML = `<span>${escapeHtml(item)}</span>`;
    const remove = document.createElement("button");
    remove.type = "button";
    remove.textContent = "x";
    remove.addEventListener("click", () => {
      state[type].splice(index, 1);
      renderTags(type);
    });
    chip.appendChild(remove);
    container.appendChild(chip);
  });
}

function addTag(type, value) {
  const normalized = value.trim();
  if (!normalized) return;
  state[type].push(normalized);
  renderTags(type);
}

function renderSources() {
  $.sourceList.innerHTML = "";
  if (state.sources.length === 0) {
    const hint = document.createElement("div");
    hint.className = "notice";
    hint.textContent = "Add URLs, repos, or local docs as optional research sources.";
    $.sourceList.appendChild(hint);
    return;
  }

  state.sources.forEach((source, index) => {
    const row = document.createElement("div");
    row.className = "source-row";
    const kind = document.createElement("select");
    ["url", "github_repo", "local_doc", "note"].forEach((k) => {
      const option = document.createElement("option");
      option.value = k;
      option.textContent = k;
      option.selected = source.kind === k;
      kind.appendChild(option);
    });
    kind.addEventListener("change", (event) => {
      state.sources[index].kind = event.target.value;
    });

    const value = document.createElement("input");
    value.type = "text";
    value.placeholder = "Source value";
    value.value = source.value;
    value.addEventListener("input", (event) => {
      state.sources[index].value = event.target.value;
    });

    const remove = document.createElement("button");
    remove.type = "button";
    remove.className = "button button-tiny";
    remove.textContent = "Remove";
    remove.addEventListener("click", () => {
      state.sources.splice(index, 1);
      renderSources();
    });

    row.append(kind, value, remove);
    $.sourceList.appendChild(row);
  });
}

function applyPreset(preset) {
  $.ideaInput.value = preset.idea;
  state.goals = [...preset.goals];
  state.constraints = [...preset.constraints];
  state.sources = preset.sources.map((item) => ({ ...item }));
  renderTags("goals");
  renderTags("constraints");
  renderSources();
}

function selectedArtifacts() {
  return [...document.querySelectorAll(".artifact-checks input:checked")].map((item) => item.value);
}

function toContentHtml(value) {
  if (Array.isArray(value)) {
    return `<ul>${value.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>`;
  }
  if (value && typeof value === "object") {
    return Object.entries(value)
      .map(
        ([key, nested]) =>
          `<div class="content-node"><strong>${escapeHtml(key.replaceAll("_", " "))}</strong>${toContentHtml(nested)}</div>`
      )
      .join("");
  }
  const text = String(value ?? "-");
  if (/^#{1,6}\s|\n[-*]\s|\n\d+\.\s/m.test(text)) {
    return markdownToHtml(text);
  }
  return `<div>${escapeHtml(text)}</div>`;
}

function markdownToHtml(markdown) {
  const lines = markdown.split("\n");
  const html = [];
  let inUl = false;
  let inOl = false;

  function closeLists() {
    if (inUl) {
      html.push("</ul>");
      inUl = false;
    }
    if (inOl) {
      html.push("</ol>");
      inOl = false;
    }
  }

  lines.forEach((raw) => {
    const line = raw.trim();
    if (!line) {
      closeLists();
      return;
    }
    if (/^###\s+/.test(line)) {
      closeLists();
      html.push(`<h5>${escapeHtml(line.replace(/^###\s+/, ""))}</h5>`);
      return;
    }
    if (/^##\s+/.test(line)) {
      closeLists();
      html.push(`<h4>${escapeHtml(line.replace(/^##\s+/, ""))}</h4>`);
      return;
    }
    if (/^#\s+/.test(line)) {
      closeLists();
      html.push(`<h3>${escapeHtml(line.replace(/^#\s+/, ""))}</h3>`);
      return;
    }
    if (/^[-*]\s+/.test(line)) {
      if (!inUl) {
        closeLists();
        html.push("<ul>");
        inUl = true;
      }
      html.push(`<li>${escapeHtml(line.replace(/^[-*]\s+/, ""))}</li>`);
      return;
    }
    if (/^\d+\.\s+/.test(line)) {
      if (!inOl) {
        closeLists();
        html.push("<ol>");
        inOl = true;
      }
      html.push(`<li>${escapeHtml(line.replace(/^\d+\.\s+/, ""))}</li>`);
      return;
    }
    closeLists();
    html.push(`<p>${escapeHtml(line)}</p>`);
  });

  closeLists();
  return html.join("");
}

function formatArtifactContent(artifact) {
  const content = artifact.content || {};
  if (artifact.artifact_type === "mvp_spec") {
    const stages = content.workflow_stages || [];
    const mustHave = content.must_have || [];
    return `
      <div class="content-node">
        <strong>MVP Workflow</strong>
        <ol>${stages.map((stage) => `<li>${escapeHtml(stage)}</li>`).join("")}</ol>
      </div>
      <div class="content-node">
        <strong>Must-Have Rules</strong>
        <ul>${mustHave.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>
      </div>
    `;
  }
  if (artifact.artifact_type === "research_brief") {
    return `
      <div class="content-node"><strong>Problem</strong>${toContentHtml(content.problem)}</div>
      <div class="content-node"><strong>Goals</strong>${toContentHtml(content.goals || [])}</div>
      <div class="content-node"><strong>Conclusion</strong>${toContentHtml(content.conclusion)}</div>
      <div class="content-node"><strong>Risks</strong>${toContentHtml(content.risks || [])}</div>
    `;
  }
  return toContentHtml(content);
}

function renderMetrics(metrics) {
  const labels = {
    coverage_score: "Coverage",
    evidence_support_rate: "Evidence support",
    actionability_score: "Actionability",
    total_token_usage: "Token usage",
    latency_ms: "Latency",
    user_edit_distance: "Edit distance",
  };

  $.metricGrid.innerHTML = "";
  Object.entries(labels).forEach(([key, label]) => {
    const raw = metrics[key] ?? 0;
    const formatted =
      key === "latency_ms" ? `${Math.round(raw)} ms` : key === "total_token_usage" ? String(raw) : Number(raw).toFixed(2);
    const card = document.createElement("div");
    card.className = "metric-card";
    card.innerHTML = `<small>${escapeHtml(label)}</small><strong>${escapeHtml(formatted)}</strong>`;
    $.metricGrid.appendChild(card);
  });
}

function renderTimeline(history) {
  $.timelineStrip.innerHTML = "";
  history.forEach((stage) => {
    const pill = document.createElement("div");
    pill.className = "timeline-pill";
    pill.textContent = stage;
    $.timelineStrip.appendChild(pill);
  });
}

function renderArtifactContent() {
  const artifact = state.artifacts[state.activeArtifactIndex];
  if (!artifact) {
    $.artifactContent.innerHTML = "<div>No artifact output.</div>";
    return;
  }
  const linkedEvidence = (artifact.evidence_ids || [])
    .map((id) => state.evidenceMap[id])
    .filter(Boolean);

  $.artifactContent.innerHTML = `
    <div class="content-node"><strong>${escapeHtml(artifact.title)}</strong>${formatArtifactContent(artifact)}</div>
    <div class="content-node">
      <strong>Evidence sources</strong>
      ${linkedEvidence.length ? linkedEvidence.map((item) => evidenceReferenceHtml(item)).join("") : "<p>No verifiable source linked.</p>"}
    </div>
  `;
}

function renderArtifacts(artifacts) {
  state.artifacts = artifacts;
  state.activeArtifactIndex = 0;
  $.artifactCount.textContent = `${artifacts.length} outputs`;
  $.artifactTabs.innerHTML = "";
  artifacts.forEach((artifact, index) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = `artifact-tab ${index === 0 ? "active" : ""}`;
    button.textContent = artifact.title;
    button.addEventListener("click", () => {
      state.activeArtifactIndex = index;
      [...$.artifactTabs.children].forEach((node, nodeIndex) => node.classList.toggle("active", nodeIndex === index));
      renderArtifactContent();
    });
    $.artifactTabs.appendChild(button);
  });
  renderArtifactContent();
}

function inferSourceKind(item) {
  if (item.skill === "local_docs_lookup") return "Local knowledge";
  if (item.skill === "github_repo_search") return "Repository";
  if (item.skill === "fetch_page") return "Web page";
  if (item.skill === "web_search") return "Web result";
  if (item.skill === "competitor_scan") return "Benchmark model";
  if (String(item.source).startsWith("http")) return "Web page";
  if (String(item.source).startsWith("synthetic://")) return "System generated";
  return "Evidence source";
}

function evidenceLink(item) {
  const source = String(item.source || "");
  if (source.startsWith("http")) {
    return `<a class="evidence-link" href="${escapeHtml(source)}" target="_blank" rel="noreferrer">Open source</a>`;
  }
  return `<span>${escapeHtml(source.replace("synthetic://", ""))}</span>`;
}

function evidenceReferenceHtml(item) {
  return `
    <div class="evidence-ref">
      <div class="evidence-ref-title">${escapeHtml(item.title)}</div>
      <div class="evidence-meta">
        <span class="meta-pill">${escapeHtml(inferSourceKind(item))}</span>
        <span class="meta-pill">${escapeHtml(item.skill.replaceAll("_", " "))}</span>
      </div>
      ${evidenceLink(item)}
    </div>
  `;
}

function renderEvidence(items) {
  $.evidenceCount.textContent = `${items.length} items`;
  $.evidenceList.innerHTML = "";
  items.forEach((item) => {
    const card = document.createElement("article");
    card.className = "evidence-card";
    card.innerHTML = `
      <h4>${escapeHtml(item.title)}</h4>
      <p>${escapeHtml(item.summary)}</p>
      <div class="evidence-meta">
        <span class="meta-pill">${escapeHtml(inferSourceKind(item))}</span>
        <span class="meta-pill">${escapeHtml(item.skill.replaceAll("_", " "))}</span>
      </div>
      ${evidenceLink(item)}
    `;
    $.evidenceList.appendChild(card);
  });
}

function renderTaskState(taskState) {
  $.taskState.innerHTML = "";
  const cleanedTaskState = { ...taskState };
  if (cleanedTaskState.synthesis && typeof cleanedTaskState.synthesis === "object") {
    const synthesis = { ...cleanedTaskState.synthesis };
    delete synthesis.llm_summary;
    delete synthesis.llm_summary_reference;
    cleanedTaskState.synthesis = synthesis;
  }

  Object.entries(cleanedTaskState).forEach(([key, value]) => {
    const row = document.createElement("article");
    row.className = "state-row";
    row.innerHTML = `<h4>${escapeHtml(key.replaceAll("_", " "))}</h4><p>${toContentHtml(value)}</p>`;
    $.taskState.appendChild(row);
  });
}

function humanTraceLabel(stage) {
  const map = {
    Intake: "Understanding your request",
    Clarification: "Clarifying scope and gaps",
    OptionalBrainstorm: "Exploring candidate directions",
    ResearchCollectors: "Collecting external evidence",
    Synthesis: "Summarizing findings and risks",
    ArtifactGenerator: "Formatting final deliverables",
  };
  return map[stage] || stage;
}

function renderTrace(trace) {
  $.traceCount.textContent = `${trace.length} stages`;
  $.traceList.innerHTML = "";
  trace.forEach((entry) => {
    const details = Object.entries(entry.details || {})
      .map(([key, value]) => `${key}: ${Array.isArray(value) ? value.join(", ") : value}`)
      .join(" | ");
    const card = document.createElement("article");
    card.className = "trace-entry";
    card.innerHTML = `
      <h4>${escapeHtml(entry.stage)} - ${escapeHtml(humanTraceLabel(entry.stage))}</h4>
      <div class="trace-meta">
        <span>${escapeHtml(entry.status)}</span>
        <span>${escapeHtml(Math.round(entry.duration_ms))} ms</span>
      </div>
      <p>${escapeHtml(details || "No details.")}</p>
    `;
    $.traceList.appendChild(card);
  });
}

function renderRun(run) {
  $.resultsBody.classList.remove("hidden");
  $.runIdDisplay.textContent = run.run_id;
  $.currentStageDisplay.textContent = run.current_stage;
  $.statusDisplay.textContent = run.status;
  $.runStatus.textContent = run.status;
  $.runIdInput.value = run.run_id;
  state.evidenceMap = {};
  (run.evidence_summary || []).forEach((item) => {
    state.evidenceMap[item.evidence_id] = item;
  });
  renderMetrics(run.metrics || {});
  renderTimeline(run.stage_history || []);
  renderArtifacts(run.artifact_summary || []);
  renderEvidence(run.evidence_summary || []);
  renderTaskState(run.task_state || {});
  renderTrace(run.trace || []);
  renderLogFromTrace(run.trace || []);
  setNotice("Run loaded. This data is coming from the real backend response.");
}

async function fetchRun(runId) {
  const response = await fetch(`/runs/${encodeURIComponent(runId)}`);
  if (!response.ok) throw new Error("Run not found.");
  return response.json();
}

async function submitRun(event) {
  event.preventDefault();
  const payload = {
    idea: $.ideaInput.value.trim(),
    goals: [...state.goals],
    constraints: [...state.constraints],
    desired_artifacts: selectedArtifacts(),
    optional_sources: state.sources
      .map((source) => ({ kind: source.kind, value: source.value.trim() }))
      .filter((source) => source.value.length > 0),
  };

  if (payload.idea.length < 4) {
    setNotice("Please provide a more specific idea.", true);
    return;
  }

  try {
    setLoading(true);
    startLiveLog(payload);
    setNotice("Running ScopeForge and waiting for structured output...");
    const createResponse = await fetch("/runs", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!createResponse.ok) throw new Error("Failed to create run.");
    const created = await createResponse.json();
    const detail = await fetchRun(created.run_id);
    renderRun(detail);
  } catch (error) {
    stopLiveLog();
    $.liveLogStatus.textContent = "Failed";
    pushLog("Error", error.message || "Run failed");
    setNotice(error.message || "Run failed.", true);
  } finally {
    setLoading(false);
  }
}

async function loadRunById() {
  const runId = $.runIdInput.value.trim();
  if (!runId) {
    setNotice("Paste a run_id first.", true);
    return;
  }
  try {
    setLoading(true);
    $.liveLogStatus.textContent = "Loading";
    setNotice("Fetching run details...");
    const detail = await fetchRun(runId);
    renderRun(detail);
  } catch (error) {
    stopLiveLog();
    $.liveLogStatus.textContent = "Failed";
    pushLog("Error", error.message || "Failed to fetch run.");
    setNotice(error.message || "Failed to fetch run.", true);
  } finally {
    setLoading(false);
  }
}

function bindEvents() {
  document.querySelector("[data-add-tag='goals']").addEventListener("click", () => {
    addTag("goals", $.goalInput.value);
    $.goalInput.value = "";
    $.goalInput.focus();
  });
  document.querySelector("[data-add-tag='constraints']").addEventListener("click", () => {
    addTag("constraints", $.constraintInput.value);
    $.constraintInput.value = "";
    $.constraintInput.focus();
  });
  $.goalInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
      event.preventDefault();
      addTag("goals", $.goalInput.value);
      $.goalInput.value = "";
    }
  });
  $.constraintInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
      event.preventDefault();
      addTag("constraints", $.constraintInput.value);
      $.constraintInput.value = "";
    }
  });
  $.addSource.addEventListener("click", () => {
    state.sources.push({ kind: "url", value: "" });
    renderSources();
  });
  $.loadSample.addEventListener("click", () => applyPreset(presets[0]));
  $.runForm.addEventListener("submit", submitRun);
  $.loadRun.addEventListener("click", loadRunById);
}

function shouldBypassPaging(eventTarget) {
  const bypassSelectors = [
    "textarea",
    "input",
    "select",
    ".live-log",
    ".artifact-content",
    ".evidence-list",
    ".trace-list",
    ".state-list",
  ];
  return bypassSelectors.some((selector) => eventTarget.closest(selector));
}

function nearestSectionIndex(sections, scrollTop) {
  let bestIndex = 0;
  let minDistance = Number.POSITIVE_INFINITY;
  sections.forEach((section, index) => {
    const distance = Math.abs(section.offsetTop - scrollTop);
    if (distance < minDistance) {
      minDistance = distance;
      bestIndex = index;
    }
  });
  return bestIndex;
}

function initSectionPaging() {
  if (!$.main) return;
  const sections = [...$.main.querySelectorAll(".page-section")];
  if (sections.length < 2) return;

  let locked = false;
  let touchStartY = 0;

  function jumpTo(index) {
    const targetIndex = Math.max(0, Math.min(index, sections.length - 1));
    sections[targetIndex].scrollIntoView({ behavior: "smooth", block: "start" });
    locked = true;
    window.setTimeout(() => {
      locked = false;
    }, 650);
  }

  $.main.addEventListener(
    "wheel",
    (event) => {
      if (locked || shouldBypassPaging(event.target)) return;
      if (Math.abs(event.deltaY) < 16) return;
      event.preventDefault();
      const current = nearestSectionIndex(sections, $.main.scrollTop);
      const direction = event.deltaY > 0 ? 1 : -1;
      jumpTo(current + direction);
    },
    { passive: false }
  );

  $.main.addEventListener(
    "touchstart",
    (event) => {
      touchStartY = event.touches[0].clientY;
    },
    { passive: true }
  );

  $.main.addEventListener(
    "touchend",
    (event) => {
      if (locked || shouldBypassPaging(event.target)) return;
      const delta = touchStartY - event.changedTouches[0].clientY;
      if (Math.abs(delta) < 36) return;
      const current = nearestSectionIndex(sections, $.main.scrollTop);
      jumpTo(current + (delta > 0 ? 1 : -1));
    },
    { passive: true }
  );
}

function init() {
  renderPresetRail();
  renderTags("goals");
  renderTags("constraints");
  renderSources();
  bindEvents();
  initSectionPaging();
  applyPreset(presets[0]);
  pushLog("Info", "Run a task to see progress and stage logs here.");
}

init();
