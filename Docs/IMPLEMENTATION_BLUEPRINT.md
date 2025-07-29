# Implementation Blueprint  
### (Step-by-Step plan to realise the Road-map improvements)

> This playbook breaks every previously-proposed idea into concrete, sequential tasks that a small team can execute.  Each block lists **who** owns it, **what** to do, **how long** it should take, and **deliverables**.  Follow the phases in order; each phase is self-contained and can be merged after review.

---

## Phase 0 • Foundation (1–2 days)

| Step | Action | Owner | Notes |
|------|--------|-------|-------|
| 0.1 | Create new branch `feat/roadmap-foundation` | Lead Dev |  |
| 0.2 | Install dev helpers<br>`pip install black flake8 pre-commit poetry` | All | |
| 0.3 | Add **pre-commit** config to run *black* & *flake8* | Lead Dev | Push & verify hook |
| 0.4 | Set up **GitHub Actions** CI matrix (Py 3.9-3.12) | DevOps | Re-use existing `pytest` suite |
| 0.5 | Publish **VS Code DevContainer** (`.devcontainer/`) with Python, Poetry, & extensions | DevOps | |

**Deliverables:** passing CI badge in `README`, devcontainer build succeeds locally and in Codespaces.

---

## Phase 1 • Usability Enhancements (≈2 wks)

### U-1 Rich TUI Dashboard (Textual)

1. **Dependency**:  
   ```bash
   poetry add textual~=0.50
   ```
2. Scaffold `src/ui/dashboard_app.py`  
   ```python
   from textual.app import App
   class DashboardApp(App): …
   ```
3. Create **widgets**  
   - `JobsTable` → subscribes to JobStore events.  
   - `HistoryPane` → scrollable Markdown.  
   - `ModesBar` → toggle buttons.
4. Integrate **command** `/dash` in `mode_manager.py` to `await DashboardApp().run_async()`.
5. **Tests**: snapshot test for layout using `pytest-textual`.

### U-2 Voice Interface

1. Install offline ASR & TTS:  
   ```bash
   poetry add vosk pyttsx3 sounddevice
   ```
2. `src/voice_interface.py`  
   - Thread reads mic → Vosk model → queue text → CLI handler.  
   - TTS reads last AI response.
3. Flag `--voice` in `run.py`.

### U-3 Contextual Autocomplete

1. Replace raw `input()` in `multiline_input.py` with `prompt_toolkit.PromptSession`.  
2. Implement custom `Completer` that merges: commands list, mode names, history.

### U-4 Profile Loader

1. Add `profiles/astronaut.json` (model, temperature, local RAG).  
2. `config.py`: `load_profile("astronaut")` merges into env.

### U-5 Interactive Export Selector

1. Extend `markdown_exporter.py` with `select_conversation_segments()` using `prompt_toolkit` check-boxes.  
2. `/export -i` triggers interactive selection.

---

## Phase 2 • Accuracy & Reliability (≈3 wks)

### A-1 Structured Citation Validator

1. Add dependency:  
   ```bash
   poetry add crossrefapi
   ```
2. `src/validators/citation_checker.py`  
   - Regex DOI/PMID.  
   - Cross-check via CrossRef / PubMed API.  
   - Return list of warnings.
3. Hook into `markdown_exporter` post-process; append “Citation Audit” table.

### A-2 Ensemble Response Voting

1. Update `.env` to accept `SECONDARY_MODEL`.  
2. `openai_enhanced_client.py`: add `generate_secondary()` branch.  
3. `consensus_agent.py`  
   - Embed both responses with OpenAI embeddings.  
   - Cosine similarity; if < 0.85 → emit “Divergence Alert” + side-by-side diff.

### A-3 Red-Team Prompt Library

1. New directory `tests/red_team/prompts/*.txt`.  
2. Parametrised pytest that feeds each prompt to `/prompt` mode with `--dry` (no external hits).  
3. Fail test if hallucination regex (e.g., “as an AI developed…”).

### A-4 Temporal Data Guardrails

1. Extend system prompt template in `openai_enhanced_client.py` with:  
   ```
   "Knowledge cutoff: 2025-06. Always state this in answer."
   ```

### A-5 Offline Fallback Knowledge Pack

1. Download PubMed aerospace subset CSV (~500 MB).  
2. `scripts/build_vector_db.py` → `chromadb` persistence.  
3. `knowledge_base/local_rag.py` loads DB; `ModeManager` checks `offline=True` env flag.

---

## Phase 3 • Orion Copilot Framework (≈6 wks)

### Milestone P1 YAML Schema + ChecklistAgent (2 wks)

| Step | Task |
|------|------|
| P1-1 | Define JSON Schema `docs/procedure_schema.json` |
| P1-2 | `src/copilot/checklist_agent.py` loads YAML, exposes `next_step()`, `ack(step_id)` |
| P1-3 | Add CLI `/procedure start <file>` command |
| P1-4 | Unit tests: happy path, invalid YAML |

### Milestone P2 Voice Confirmation & Logging (1 wk)

| Step | Task |
|------|------|
| P2-1 | Re-use Voice Interface to listen for `verify` phrases |
| P2-2 | `LoggerAgent` → `sqlite:///copilot_logs.db`, SHA-256 prev-hash chain |
| P2-3 | Export logs to Markdown after run |

### Milestone P3 Telemetry Adapter & Rule Engine (1.5 wks)

| Step | Task |
|------|------|
| P3-1 | Define adapter interface `TelemetryProvider.get(metric:str)->float` |
| P3-2 | `monitor_agent.py` registers rules like `{"heart_rate":"< 30"}` |
| P3-3 | Simulated feed for tests (`tests/fake_telemetry.py`) |

### Milestone P4 Offline Bundle (1.5 wks)

| Step | Task |
|------|------|
| P4-1 | Build local RAG index for medical procedures manuals |
| P4-2 | Add `KnowledgeAgent` querying this index |
| P4-3 | Package minimal **onnx** LLM (GPT-J 6B) via `ctransformers` for offline answers |

---

## Phase 4 • Documentation & Training (1 wk)

1. Generate Sphinx docs (`Docs/source/`), host on GitHub Pages.  
2. Jupyter notebook `Docs/notebooks/orion_demo.ipynb` with voice-guided ACLS walk-through.  
3. One-page **Quick-Look cards** using LaTeX `tcolorbox`.

---

## Phase 5 • Compliance & Safety (Parallel, continuous)

- Maintain **IEC 62304** traceability matrix in `Docs/compliance/`.  
- Add “Explainability Mode” toggle to dump model metadata into every log.  
- Quarterly review with domain expert; minutes stored in repo under `Docs/QA/`.

---

## Phase 6 • Launch & Feedback (ongoing)

1. Tag **v1.0-beta** after Phase 3 completes.  
2. Open internal beta with flight surgeons & analog astronauts.  
3. Collect GitHub Discussions feedback, triage weekly.  
4. Road-map v1.1 based on real-world use.

---

### Gantt-like Timeline (rough)

```
Week:   1 2 3 4 5 6 7 8 9 10 11
Phase0: =====
Phase1:    ==========
Phase2:             ========
Phase3 P1-4:                  ====================
Phase4:                                      ====
```

---

## Contribution Guide (Abbreviated)

1. Fork → branch `feat/<ticket>`  
2. Write/adjust unit tests (>= 90 % cov).  
3. Run `make lint test`.  
4. Open PR + link to issue.  
5. Reviewer hits **“Checklist — Safety & Compliance”** before merge.

---

### Final Note

By following this step-wise blueprint, the team moves from **idea** to **deployed, crew-usable system** while maintaining code quality, scientific rigor, and flight-ready reliability.