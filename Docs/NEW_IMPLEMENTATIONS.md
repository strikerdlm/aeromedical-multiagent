# New Implementation Proposals

> Practical, near-term additions that extend the current feature set without overlapping the existing Enhancement Roadmap and Implementation Blueprint. Each proposal includes rationale, scope, first steps, and acceptance criteria. File and class names align with this repo’s structure.

---

## 1) PRISMA Record Manager + Flow Diagram Generator

- Rationale: Current PRISMA flow is narrative. Add rigorous record tracking, deduplication, and auto-generated PRISMA 2020 diagram.
- Scope:
  - `src/prisma_record_manager.py`: Ingest sources (Perplexity search results, Flowise RAG hits, manual imports), deduplicate by DOI/PMID/title-year, track counts per PRISMA stage.
  - `src/prisma_flow_diagram.py`: Render PRISMA flow as Mermaid and PNG (via `kroki` or `katex`-style service), embed into exports.
  - Extend `MarkdownExporter.export_prisma_review` to include diagram and counts.
- First steps:
  - Implement `RecordManager` with `add_records(List[Record])`, `deduplicate()`, and `prisma_counts()`.
  - Generate Mermaid snippet and save `exports/PRISMA_flow_<slug>.md`.
- Acceptance:
  - Given mixed duplicated inputs, dedup rate > 95% on a synthetic fixture.
  - Export contains PRISMA counts table and Mermaid diagram block.

---

## 2) Evidence Grading: GRADE Summary-of-Findings Tables

- Rationale: Add automated evidence profiles for included studies.
- Scope:
  - `src/prisma_grade.py`: Map extracted outcomes → GRADE domains (risk of bias, inconsistency, indirectness, imprecision, publication bias) with heuristics and LLM-assisted reasoning.
  - Export `Summary of Findings` tables in markdown and CSV.
- First steps:
  - Define `OutcomeAssessment` dataclass and a scoring rubric.
  - Hook into PRISMA pipeline right before report generation.
- Acceptance:
  - Tables rendered with per-outcome certainty ratings (High/Moderate/Low/Very low).
  - Unit tests on rubric mapping and formatting.

---

## 3) Structured Data Exports for Meta-analysis

- Rationale: Enable downstream analysis beyond narrative synthesis.
- Scope:
  - `src/exports/structured/` directory with JSONL and CSV dumps of per-study extractions.
  - `src/prisma_meta_schema.py`: Simple schema for effect sizes, CIs, sample sizes, and subgroup labels.
- First steps:
  - Add writer in `markdown_exporter.py` to emit JSONL alongside markdown.
  - Provide `--export-structured` CLI toggle.
- Acceptance:
  - After PRISMA run, `exports/structured/*.jsonl` present and validates against schema.

---

## 4) Zotero Integration (Import/Export)

- Rationale: Interop with common reference managers.
- Scope:
  - `src/integrations/zotero_client.py`: Minimal client for collections, items, and attachments.
  - Import RIS/BibTeX; export curated library for included studies.
- First steps:
  - Add `--zotero-collection <id>` to PRISMA mode to push included citations.
- Acceptance:
  - Round-trip of 10 test references with stable keys and metadata parity on authors, year, title, DOI.

---

## 5) Persistent Job Store (SQLite)

- Rationale: Current jobs appear in-memory; persist across sessions and support audits.
- Scope:
  - `src/jobs_store_sqlite.py`: `sqlite3`-backed `JobStore` implementing the same interface as `src/jobs.py`.
  - Migrate `src/ui/main_display.py` job archive views to the persistent store.
- First steps:
  - Add `APP_PERSIST_JOBS=true` env flag to select backend.
- Acceptance:
  - Jobs survive process restarts; list and download work as-is.

---

## 6) Observability: Structured Logging + Metrics

- Rationale: Improve debuggability and operations.
- Scope:
  - `src/observability/logging_setup.py`: JSON logs with request IDs, model, tokens, duration.
  - `src/observability/metrics.py`: Prometheus-style counters (requests, errors) and histograms (latency).
- First steps:
  - Replace ad-hoc logger in `src/main.py` with centralized config toggled by `LOG_FORMAT=json`.
- Acceptance:
  - Logs include correlation IDs; `metrics.txt` snapshot created during tests with sane values.

---

## 7) HTTP Caching and Rate-Limit Protection

- Rationale: Reduce API costs and avoid rate-limit failures.
- Scope:
  - `src/net/cache.py`: `requests-cache` or local `sqlite` caching for GET; exponential backoff with jitter wrappers.
  - Apply to Perplexity status polling and Flowise history.
- First steps:
  - Add `CACHE_TTL_SECONDS` env; wrap `FlowiseClient.get_session_history` and Perplexity `check_async_status`.
- Acceptance:
  - Hit ratio > 0.6 on synthetic repeated polls; fewer external calls in tests.

---

## 8) Secrets and Config Hardening (Pydantic Settings)

- Rationale: Safer config loading and validation.
- Scope:
  - `src/config_settings.py`: Pydantic `BaseSettings` with types, defaults, and `.env` schema validation.
  - Generate `.env.template` from settings with comments.
- First steps:
  - Swap imports in modules to use `Settings()` singleton instead of raw env reads in `AppConfig`.
- Acceptance:
  - Missing critical keys fail fast with friendly messages; tests cover required/optional keys.

---

## 9) Reproducibility Bundle Export

- Rationale: Make runs auditable and repeatable.
- Scope:
  - `exports/run_<id>/bundle/` containing: prompts, model versions, seeds (if available), citations, PRISMA counts, and raw API responses (redacted).
  - `src/exporters/repro_bundle.py` helper.
- First steps:
  - Add `/bundle` command to package the current session.
- Acceptance:
  - Directory is self-contained; `manifest.json` enumerates artifacts.

---

## 10) Safety: PHI/PII Redaction Filter

- Rationale: Reduce accidental leakage in clinical contexts.
- Scope:
  - `src/safety/redaction.py`: Regex + lightweight NER pass to redact names/IDs/dates; opt-in via `ENABLE_REDACTION=true`.
  - Hook before export and prior to external API calls in PRISMA.
- First steps:
  - Provide `RedactionReport` with counts and examples.
- Acceptance:
  - Test texts show > 90% recall on synthetic PHI patterns; exports contain redacted tokens.

---

## 11) Web UI (Read-Only v0) for Archives

- Rationale: Share results without CLI.
- Scope:
  - `src/web/app.py` (FastAPI): browse `exports/`, render markdown (with Mermaid), download bundles.
  - No auth initially; serve on `localhost` only.
- First steps:
  - Add `uvicorn` optional dependency and `run.py --web` flag.
- Acceptance:
  - Visiting `/exports` lists files, clicking opens rendered markdown with diagrams.

---

## 12) Plugin SDK for Agents and Tools

- Rationale: Allow external teams to add agents without touching core.
- Scope:
  - `src/plugins/sdk.py`: Simple interface for `register_agent`, `register_tool`, entry points via `plugins/` folder.
  - Load at startup and expose `/plugins` CLI to list.
- First steps:
  - Define `PluginSpec` dataclass and discovery via `pkgutil.iter_modules(['plugins'])`.
- Acceptance:
  - Example plugin adds a toy agent visible under `/modes`.

---

## 13) Offline Literature Pack Ingestion Pipeline

- Rationale: Complement A-5 (offline RAG) with a clean ingest path.
- Scope:
  - `scripts/ingest_pubmed.py` → `knowledge_base/chroma/` with persistent DB.
  - `src/knowledge/local_rag.py` exposes `search(query)->List[Doc]` with metadata.
- First steps:
  - Add `OFFLINE_ONLY=true` flag to route all searches through local RAG.
- Acceptance:
  - When offline, PRISMA search still returns relevant cached items from sample pack.

---

## 14) Prompt Provenance and Diff Viewer

- Rationale: Track how prompts evolve across the pipeline.
- Scope:
  - `src/provenance/tracer.py`: Capture inputs/outputs at each agent hop; save as JSON.
  - `/provenance` command to open a compact textual diff of prompt stages.
- First steps:
  - Wrap calls in `core_agents/research_orchestrator.py` to emit trace events.
- Acceptance:
  - Provenance file exists per run; diff shows optimizer → research prompt changes.

---

## 15) Pandoc-based PDF Export with Bibliography

- Rationale: Produce shareable PDFs with proper references.
- Scope:
  - `src/exporters/pdf_exporter.py`: Use `pandoc` (if installed) to convert markdown → PDF; support CSL styles for APA.
  - Add `--pdf` flag to `/export` and `/report` paths.
- First steps:
  - Bundle default `apa.csl` and `references.bib` generation from verified citations.
- Acceptance:
  - A PDF is produced locally matching the markdown content; references formatted in APA.

---

## 16) Concurrency Upgrade for External Calls

- Rationale: Reduce wall-clock time for research.
- Scope:
  - Switch Perplexity polling and Flowise history fetches to `httpx.AsyncClient` with bounded concurrency.
  - `src/net/async_http.py` wrapper with retries.
- First steps:
  - Add async variants and integrate where event loops already exist.
- Acceptance:
  - On a test scenario, total runtime decreases by > 25% vs. baseline.

---

## 17) Model Routing Policy as Configurable Rules

- Rationale: Make mode routing transparent and adjustable.
- Scope:
  - `src/routing/policy.py`: YAML-driven rules mapping keywords/regex to modes and models, with weights.
  - Expose `/routing test <query>` to preview decisions.
- First steps:
  - Load default policy; deprecate hard-coded heuristics in `mode_manager.py` behind the policy.
- Acceptance:
  - Changing YAML updates routing without code changes; unit tests cover precedence.

---

## 18) CI: Golden Answers + Adversarial Suites

- Rationale: Detect regressions in behavior.
- Scope:
  - `tests/golden/`: Small inputs with frozen, sanitized outputs; tolerance via cosine similarity on embeddings.
  - `tests/adversarial/`: Misleading prompts to ensure guardrails.
- First steps:
  - Add fast `--offline --dry` modes for deterministic outputs (stubbed clients).
- Acceptance:
  - CI fails on drift beyond thresholds; report links to failing diffs.

---

## 19) Signed Exports for Integrity

- Rationale: Ensure export authenticity in clinical/audit settings.
- Scope:
  - `src/security/signing.py`: Sign export files with `age`/`minisign` if available; store detached signatures.
  - Verify command `/verify <file>`.
- First steps:
  - Add optional `SIGNING_KEY` env var and graceful no-op if absent.
- Acceptance:
  - Signature created and verified locally; tampered files fail verification.

---

## 20) Minimal Slack/Matrix Notifier for Long Jobs

- Rationale: Alert users when background jobs complete.
- Scope:
  - `src/integrations/notifier.py`: Post simple messages with job IDs and export paths.
  - Config via `SLACK_WEBHOOK_URL` or `MATRIX_HOMESERVER/ACCESS_TOKEN`.
- First steps:
  - Hook into `JobStore` completion path.
- Acceptance:
  - Notification received in a test workspace upon job completion.

---

### Notes on Compatibility and Footprint

- All items are additive and opt-in via flags or environment variables to keep the current CLI behavior and tests stable.
- Priority candidates for immediate work: 1) PRISMA Record Manager, 5) Persistent Job Store, 6) Observability, 10) Redaction Filter, 15) PDF Export.