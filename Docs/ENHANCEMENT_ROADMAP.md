# Enhancement Roadmap for the **Advanced Aeromedical Evidence Review & Research System**

> The ideas below focus on practical, *near-term* improvements that can be delivered by a small engineering team (≈1–3 developers) within 3–6 months.  Each item lists an **impact**, a **difficulty estimate**, and **first steps** to jump-start implementation.  A dedicated astronaut-support “Procedure Supervisor” framework is detailed in a standalone section.

---

## 1. Core Usability Improvements

| # | Idea | Impact | Difficulty | First Steps |
|---|------|--------|------------|-------------|
| **U-1** | **Rich TUI Dashboard** powered by `Textual` or `Rich Prompt Toolkit`. Tabs for *Live Jobs*, *History*, *Exports*, *Modes*. | ★★★★☆ | ◼◼◻︎◻︎ | - Evaluate `textual.app` prototype; map existing CLI commands → widgets. |
| **U-2** | **Voice Interaction Layer** (`vosk` offline ASR ➜ text ➜ existing pipeline). Text-to-speech for responses with `pyttsx3`. | ★★★☆☆ | ◼◼◼◻︎ | - Build thin wrapper around `run.py` that pipes voice I/O. |
| **U-3** | **Contextual Autocomplete**: as user types, show matching commands, mode names, last queries. | ★★★☆☆ | ◼◻︎◻︎ | - Integrate `prompt_toolkit` `AutoCompleter`. |
| **U-4** | **One-shot `--profile astronaut` flag** that loads pre-configured env vars (model, temperature, checklists). | ★★☆☆☆ | ◼◻︎◻︎ | - Add profile loader to `config.py`. |
| **U-5** | **Interactive Export Selector**: choose subset of conversation or PRISMA tables before saving. | ★★☆☆☆ | ◼◼◻︎◻︎ | - Extend `markdown_exporter.py` with selection prompts. |

---

## 2. Accuracy & Reliability Enhancements

| # | Idea | Impact | Difficulty | First Steps |
|---|------|--------|------------|-------------|
| **A-1** | **Structured Citation Validator**: regex-extract citations → cross-check with DOI/PubMed API → mark missing metadata. | ★★★★☆ | ◼◼◼◻︎ | - Build `citation_checker.py`; add as post-processor in export pipeline. |
| **A-2** | **Ensemble Response Voting**: call two models (e.g., GPT-4o + Claude-3) → compare embeddings → flag divergence > τ. | ★★★★☆ | ◼◼◼◼ | - Add optional `--dual-model` flag in `config.py`; write `consensus_agent`. |
| **A-3** | **Red-Team Prompt Library**: predefined adversarial prompts run against every new agent build; fail CI on hallucinations. | ★★★☆☆ | ◼◼◻︎◻︎ | - Create `tests/red_team/`; integrate with `pytest`. |
| **A-4** | **Temporal Data Guardrails**: every answer must state *cut-off date*; automatically prepend “Knowledge current as of YYYY-MM”. | ★★☆☆☆ | ◼◻︎◻︎ | - Modify `openai_enhanced_client.py` system prompt template. |
| **A-5** | **Offline Fallback Knowledge Pack**: embed vector DB of ~5k core aerospace medicine papers; use local RAG when external APIs unavailable. | ★★★☆☆ | ◼◼◼◻︎ | - Evaluate `chromadb`; script to ingest PubMed CSV. |

---

## 3. Astronaut-Focused **Procedure Supervisor Framework**

> Codename **“Orion Copilot”**

### 3.1 Goals
1. **Step-by-step execution** of medical, EVA, and contingency procedures.  
2. **Continuous verification**: Confirm each step completion via voice or manual check.  
3. **Context-aware reminders**: Timers, medication intervals, vitals thresholds.  
4. **Fail-safe offline mode**: Operates without ground link or external APIs.  

### 3.2 Agent Types

| Agent | Responsibilities | Key Tech |
|-------|------------------|----------|
| **ChecklistAgent** | Load procedure YAML → deliver next step → await `ACK` or voice confirmation. | YAML schemas, speech detection hooks |
| **MonitorAgent** | Subscribe to spacecraft telemetry (vitals JSON feed) → trigger alerts or skip steps automatically. | WebSocket / serial ingest, rule engine |
| **KnowledgeAgent** | On-demand “why” explanations, risk rationales, quick look-ups. | Local RAG + embedding model |
| **LoggerAgent** | Timestamps every action/assertion → creates tamper-evident log (e.g., hash-chained). | SQLite + SHA-256 chaining |
| **SupervisorAgent** | High-level orchestrator: pauses/resumes procedure, switches modes, escalates to ground. | Finite state machine |

### 3.3 Data & Procedure Format

```yaml
id: PROC-ACLS-001
title: Cardiac Arrest – Microgravity ACLS
revision: 2.1
steps:
  - num: 1
    action: "Call for help and retrieve AED."
    verify: "voice: 'AED ready'"
  - num: 2
    action: "Start chest compressions at 100–120/min."
    timer: 120  # seconds
  - num: 3
    action: "Attach AED pads..."
    reference: "NASA ACLS v2 p.14"
```

### 3.4 Interaction Flow

1. **`/procedure start PROC-ACLS-001`**  
2. `ChecklistAgent`: *“Step 1: Call for help…”*  
3. Astronaut: *“AED ready”* → matches verify clause.  
4. `MonitorAgent`: Auto-advances if heart rate < 30 bpm detected.  
5. **At any time** `/why` or voice *“explain”* → `KnowledgeAgent` elaborates.  
6. On completion → `LoggerAgent` hashes log, exports to Markdown & QR code.

### 3.5 Implementation Milestones

| Phase | Deliverable | Est. Time |
|-------|-------------|-----------|
| P1 | YAML schema + `ChecklistAgent` CLI prototype | 2 wks |
| P2 | Voice confirmation & logging | 3 wks |
| P3 | Telemetry adapter & rule engine | 4 wks |
| P4 | Full offline bundle (local RAG + models) | 4 wks |

---

## 4. Developer Experience

1. **Pre-commit Git Hooks**: auto-run `black`, `flake8`, minimal test suite.  
2. **Preset DevContainers** with VS Code + all Python deps to shorten onboarding.  
3. **CI Matrix** across Python 3.9-3.12 using GitHub Actions → badges in README.  
4. **Issue Templates** for *feature*, *bug*, *procedure-pack request*.  

---

## 5. Documentation & Training

| Item | Notes |
|------|-------|
| Interactive **Jupyter notebooks** demonstrating mode APIs (hidden in `Docs/notebooks`). |
| **Sphinx-based** docs site deployed to GitHub Pages; include auto-generated API ref. |
| *Quick-Look Cards* for each mode & the Orion Copilot agents; printable PDF. |
| In-sim **VR demo** (Unity or WebXR) showcasing voice-guided ACLS scenario. |

---

## 6. Compliance & Safety

1. **IEC 62304 Class A** alignment checklist for software of non-critical medical device.  
2. **NASA-STD-3001** crosswalk: map Copilot outputs to human-system integration requirements.  
3. **Explainability Mode**: attaches model temperature, token count, and chain-of-thought outline (redacted) for auditability.  

---

## 7. Funding & Collaboration Opportunities

| Program | Rationale |
|---------|-----------|
| **NASA SBIR Subtopic Z8.02** – “Crew Health & Performance” | Procedure Supervisor qualifies as decision support. |
| **ESA → OSIP** Open Space Innovation | European partnership for multilingual procedure packs. |
| **NIH NLSTTR** – Translational research for autonomous medical care | Covers deep-space medical autonomy. |

---

## 8. Quick-Win Backlog (≤ 1 day each)

- Add `/open <file.md>` command to open last export in the default editor.  
- Shortcut `/last` to re-ask previous question in different mode.  
- Color-blind-safe palette in Rich themes (Perceptual-Uniform).  
- Output timestamp in ISO-8601 across logs & exports.  

---

## 9. Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Over-reliance on cloud APIs in comms-loss scenarios | Bundled local models & cached literature (see A-5). |
| Checklist fatigue for crew | Allow “condensed mode” summarizing multiple trivial steps. |
| Mismatched telemetry formats across vehicles | Adapter pattern; config-based field mapping. |
| Hallucinated citations | Citation Validator (A-1) + Ensemble Voting (A-2). |

---

## 10. Conclusion

Implementing the above roadmap will:

1. Elevate day-to-day usability for researchers and operators.  
2. Enhance scientific **accuracy & trustworthiness** through structured validation.  
3. Deliver a mission-critical **Procedure Supervisor** framework, empowering astronauts to execute and audit complex medical tasks even during deep-space comms blackouts.

*Prepared by: AI Code Assistant*  
*Date: 2025-07-28*