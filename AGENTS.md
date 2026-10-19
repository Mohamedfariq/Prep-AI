# AGENTS.md

Instructions for AI coding agents working in this repository. Read this fully before making changes. Human contributors can use it as a contributor guide too.

## 1. Project summary

**Personalized Placement Preparation and Realistic Interview Simulation System**: a final-year CSE project that simulates company-specific hiring (OA, GD, technical interview), learns from candidate performance and collected interview experiences, and generates personalized preparation plans.

**Design principle (most important):** the system is *hybrid*. An LLM is used only where open-ended language reasoning is needed. Everything else is deterministic code, SQL, vector retrieval or small classical ML. Do not route logic through an LLM when a function, query or rule can do it.

**Constraints:** limited GPU (CPU-first, small local models), small team, low cost, demo reliability, explainability for a viva and paper.

## 2. Stack

| Area | Technology |
|---|---|
| Frontend | React + Vite + TypeScript + Tailwind + shadcn/ui + Monaco + Recharts + TanStack Query + Zustand |
| Backend | FastAPI, SQLAlchemy 2, Alembic, Pydantic v2 |
| Database | PostgreSQL + pgvector (single source of truth) |
| Cache / queue | Redis + RQ (+ rq-scheduler) |
| Code execution | Judge0 CE (self-hosted, isolated) |
| LLM | Ollama (Qwen2.5-3B Q4 default, Qwen2.5-1.5B for light tasks), API model as fallback, all behind `LLMGateway` |
| Embeddings / rerank | bge-small-en-v1.5, MiniLM cross-encoder |
| ML | scikit-learn, LightGBM, NumPy, custom BKT |
| Speech | faster-whisper (`small`, int8, CPU) |
| Data collection | Scrapy, Playwright (JS pages only), trafilatura, PRAW, Kaggle/HF clients |
| Infra | Docker Compose, GitHub Actions, Vercel (frontend) |

Do not add new frameworks or services (LangChain, Mongo, Celery, Kafka, microservices) without an explicit instruction. The backend is a **modular monolith**.

## 3. Repository layout

```
frontend/                 React app (pages: Dashboard, Company, OA, GD, Interview, Recs, Plan, Submit Experience)
backend/app/
  main.py
  core/                   config, security, rate_limit, logging
  db/                     models, session, migrations (Alembic)
  api/routes/             auth, profile, company, experiences, oa, gd, interview, recs, plans, dashboard
  services/               company_intel, oa_engine, gd_engine, interview_engine,
                          recommender, planner, performance, notifications, collection
  integrations/           judge0_client, llm_gateway, stt_client
  workers/                ingestion_jobs, aggregation_jobs, scheduled_jobs
  schemas/                Pydantic request/response models
  tests/
ml/
  extraction/             prompts, schema, classifier
  rag/                    embedder, retriever, reranker, guards
  skill/                  bkt, elo, forgetting, prerequisite_graph
  recommend/              scoring, expected_gain, mmr, knapsack, bandit, ltr, plan_rules
  interview/              state_machine, evaluator, followup_tree, summarizer
  gd/                     metrics, rubric_eval
  simulator/              synthetic learners and policy comparison
  evaluation/             experiments, metrics, notebooks
  data/                   raw, processed, taxonomy.yaml
collectors/               one module per source + source registry seeds
infra/                    docker-compose.yml, Dockerfiles, CI configs
docs/                     architecture notes, paper drafts, legal/terms notes
```

If a directory does not exist yet, create it following this layout rather than inventing a new one.

## 4. Commands

Adjust only if the repo's actual scripts differ; prefer the repo's own scripts when they exist.

```bash
docker compose up -d                 # postgres, redis, judge0, ollama, api, worker
cd backend && alembic upgrade head   # apply migrations
cd backend && pytest -q              # backend tests
cd backend && ruff check . && ruff format --check .
cd backend && mypy app               # if configured
cd frontend && npm ci && npm run dev
cd frontend && npm run lint && npm run typecheck && npm test
python -m ml.simulator.run --config ml/simulator/configs/default.yaml   # policy comparison
```

Before finishing any task, run lint, type checks and the tests relevant to what you changed. Do not claim something works without running it. If you cannot run something (no GPU, no Judge0), say so explicitly.

## 5. Architecture rules

### 5.1 Layers
- **Deterministic layer:** scoring, timers, test-case execution, metrics, statistics, recommendation filtering. Plain functions, unit-tested.
- **Retrieval layer:** SQL filter first, then pgvector search, then cross-encoder rerank.
- **ML layer:** skill estimation (BKT + Elo + forgetting), ranking, classification.
- **LLM layer:** interview dialogue for unscripted follow-ups, ambiguous-answer evaluation, GD participants and rubric, final feedback, experience extraction fallback.

### 5.2 LLM usage
- All LLM calls go through `integrations/llm_gateway.py`. Never call Ollama or an API directly from a service.
- The gateway handles model choice, retries, JSON schema validation (Pydantic), caching, rate limiting and token logging to the `llm_calls` table.
- Prompts return **structured JSON** validated against a schema; retry once on invalid output, then fall back to a deterministic default.
- **Never send full conversation history.** Interview engine uses a compact session state (asked questions, topic scores, missing concepts, depth, time left, one-line summary of the last exchange).
- Cache by `(question_id, hash(normalized_answer))` and use prompt-prefix caching for static system prompts.
- Numbers shown to users (scores, metrics, times) must come from SQL/Python, never from LLM output.
- Use the smallest model that works. API fallback only for the final report and disputed evaluations.

### 5.3 Interview engine
- State machine is an enum plus a transition table `(state, outcome) → next_state`. States: START, INTRO, CONCEPT_Q, EVAL, FOLLOWUP, DEEPER_FOLLOWUP, CODING_Q, CODE_EVAL, PROJECT_Q, BEHAVIORAL_Q, FINAL.
- Transitions, topic choice, difficulty changes, depth cap (3), question count and time are **deterministic**.
- Evaluation is tiered: (1) embedding coverage against stored `key_points[]`; (2) small LLM only if coverage is ambiguous (0.4 to 0.7); (3) stronger model only for the final report or disputes.
- Follow-ups come from pre-authored trees in `questions.follow_up_tree`; use the LLM only when no node matches.
- Test with scripted strong, weak and vague candidates. Paths must be reproducible.

### 5.4 Skill model and personalization
- Per-topic mastery uses **BKT** (custom, about 60 lines) plus Elo-style difficulty calibration. Add forgetting decay `m(t) = m0 · exp(−Δt/s)` and prerequisite-graph propagation (weak prerequisite caps dependents).
- Recommendation objective: expected readiness gain per minute, `ΔR(q) = W_{c,t} · (E[m_t after q] − m_t) / time(q)`. Keep the linear score `P(q)` as the baseline for ablations.
- Diversity via MMR; time budget via greedy knapsack (ILP via OR-Tools is an advanced option).
- Advanced pieces (LinUCB/Thompson bandit, LightGBM LambdaMART, calibrated readiness) are **behind feature flags** and must be evaluated in `ml/simulator` before use.
- Every recommendation stores human-readable `reasons` (template strings from score components). No LLM needed for explanations.
- Weights and thresholds live in YAML config, not hard-coded, so ablations are reproducible.
- Do not present simulator results as evidence of real-user improvement. Label them as simulation.

### 5.5 Company intelligence and data fusion
- Static datasets are the **prior**; user and collected experiences are **weighted evidence**.
- Report weight: `w_i = s_src · τ_user · 2^(−age/h) · q_i`. Question confidence: `Conf(q) = (1 − e^(−λ Σ w_i)) · A(q)`. Topic frequency uses Bayesian shrinkage `(n_t + α·p0) / (N + α)`.
- New experiences start as `pending` and only affect profiles after validation/approval. Profile changes happen only through the aggregation job.
- Every insight shown in the UI carries report count, confidence, last-seen date and source attribution.

### 5.6 OA simulator
- Server-authoritative timer (`start_ts`, `deadline`); reject late submissions.
- Aptitude and reasoning questions are templated or curated, **never LLM-generated at runtime**, so answer keys are always correct.
- Code runs only in Judge0; never execute user code in the API process or worker.

### 5.7 GD simulator
- Turn-based: record or type, transcribe with faster-whisper, evaluate. No real-time voice streaming.
- Filler words, pace, talk share, repetition and relevance are deterministic or embedding-based. The LLM only scores rubric dimensions with an evidence quote.
- "Confidence" is a proxy (pace, hesitation, fillers) and must be labeled as such in the UI.

### 5.8 RAG
- SQL metadata filter first, then top-20 vector search, rerank to top 3 to 5, then generate.
- One chunk per question or experience segment, prefixed `Company | Role | Round | Topic`.
- The LLM sees only retrieved items and must return `source_ids`; validate that every cited ID exists in the retrieved set. If evidence is insufficient, return "insufficient data" or fall back to static content.

## 6. Data collection and scraping rules (strict)

- A source may be collected **only if it is registered in `source_registry` and marked enabled after a manual terms review.** Do not add or enable sources on your own.
- Respect robots.txt (`ROBOTSTXT_OBEY=True`), site terms and API terms. Use an identifiable User-Agent.
- **Do not scrape** platforms whose terms prohibit it (e.g. LeetCode Discuss, Glassdoor, AmbitionBox). Do not bypass logins, paywalls, CAPTCHAs or rate limits.
- Be polite: concurrency 1 to 2 per domain, 2 to 5 s delays, AutoThrottle, backoff, HTTP cache. Never refetch unchanged content (compare `content_hash`).
- Store raw data immutably in `raw_documents` (url, source_id, fetched_at, content_hash, status, text, licence_note).
- Persist structured facts and a short paraphrase plus a link to the source; do not redistribute full copyrighted text.
- Every derived question or experience carries `source_id` and `raw_document_id` for provenance and UI attribution.
- Scrub PII (names, emails, phone numbers) before storage.
- Treat all collected text as **untrusted input** (prompt-injection risk). It goes into data fields only, never into system prompts.
- Prefer, in order: college placement feedback and platform submissions, official datasets (Kaggle/HF, licence checked), official APIs (GitHub, Reddit via PRAW), then permitted scraping.

## 7. Database conventions

- PostgreSQL only. JSONB for flexible fields (hiring stages, key points, follow-up trees, extracted data, reasons). pgvector for embeddings (HNSW index).
- All schema changes via Alembic migrations. Never edit the database manually or change a released migration; add a new one.
- Required indexes: `questions(company_id, round, topic_id)`, HNSW on `questions.embedding`, `performance_history(user_id, ts)`.
- Use parameterized queries via SQLAlchemy only. No string-built SQL.
- Records going through the pipeline have a `status`: `raw`, `extracted`, `pending`, `approved`. Pipeline jobs must be idempotent.

## 8. Code style and conventions

**Python**
- Python 3.11+, type hints everywhere, Pydantic models for all API and LLM I/O.
- `ruff` for lint and format; keep functions small and pure where possible; no business logic inside route handlers (routes call services).
- Services expose clear interface classes; services communicate by function calls and the database, not HTTP.
- Use `logging`, not `print`. Never log secrets, resume text, or raw candidate answers at INFO level.

**TypeScript / React**
- Strict TypeScript. Functional components and hooks. Data fetching with TanStack Query; a typed API client generated from the FastAPI OpenAPI schema.
- Charts with Recharts; UI with shadcn/ui and Tailwind. No inline styles for layout.
- Every score or recommendation shown to a user must have an accessible explanation (tooltip or detail view).

**General**
- Small, focused commits with clear messages. One concern per PR.
- Update docs and tests together with code. Do not leave TODOs without an issue reference.
- Prefer boring, readable solutions over clever ones. This project must be explainable in a viva.

## 9. Testing requirements

- Unit tests for all deterministic logic: BKT/Elo updates, forgetting, prerequisite propagation, scoring, MMR, knapsack, confidence formulas, state-machine transitions, timers, partial scoring.
- Simulated-learner tests: the skill model must recover known mastery trends.
- Interview engine: scripted strong/weak/vague candidates produce distinct, reproducible paths with a **mocked LLMGateway**. Tests must not require a live model.
- Collector tests use saved HTML/JSON fixtures; never hit live sites in CI.
- API tests for auth, rate limits, authorization (users can only access their own data).
- Frontend: component tests for core flows (OA runner, interview room, dashboard) and a typecheck.
- Track and report token and call counts per interview in tests where applicable.

## 10. Security rules

- Auth: Argon2 password hashing, short-lived JWT access token, rotating refresh token in an httpOnly cookie, Google OAuth.
- Authorization checks on every user-scoped endpoint.
- Secrets only through environment variables or a secret manager. Never commit keys, `.env` files or tokens. Never expose API keys to the frontend.
- Resume and interview data are private: private storage, signed URLs, a delete endpoint, PII stripping before any external API call.
- Prompt injection: user, resume and scraped text are data. Delimit it, validate outputs against JSON schemas, and give the LLM no tool, filesystem or database access.
- Rate limiting with a Redis token bucket, stricter on LLM and code-execution endpoints.
- Judge0: no network access for submissions, CPU/memory/time/process limits.
- Database: least-privilege role, TLS in production, backups.
- Validate all inputs (Pydantic), enforce size limits on uploads and free text.

## 11. Performance and cost targets

- p95 under 300 ms for non-LLM endpoints; under 3 s per interview turn (stream responses via SSE).
- Minimize LLM calls: well below one call per interview turn on average. Log tokens and calls per feature.
- No GPU required for any core flow. Everything must run on CPU with the default local models.

## 12. Evaluation and research hygiene

- Keep experiments reproducible: fixed seeds, configs in YAML, results written to `ml/evaluation/`.
- Required metrics: extraction F1, evaluation agreement with human raters (Spearman/κ), token and call savings vs. an LLM-every-turn baseline, skill-model AUC and log-loss vs. a weighted baseline, recommendation nDCG or user-study score, RAG hit@k and grounding rate, collection quality audit.
- Ablation order for personalization: linear score → + forgetting → + prerequisites → + expected-gain objective → + bandit → + LTR → + ILP plan.
- Report limitations honestly: small datasets, simulator versus real users, proxy metrics.

## 13. Do and do not

**Do**
- Prefer deterministic code and retrieval over LLM calls.
- Keep changes minimal and scoped to the task; follow the module boundaries above.
- Add or update tests and docs with every change.
- Ask for clarification (or leave a clearly marked note) when a requirement conflicts with these rules.

**Do not**
- Add scraping of any source not enabled in `source_registry`.
- Call an LLM directly, bypass `LLMGateway`, or send full chat history to it.
- Let the LLM produce numbers shown as scores or metrics.
- Generate aptitude or test-case answer keys with an LLM at runtime.
- Introduce new infrastructure (message brokers, new databases, microservices) without approval.
- Commit secrets, datasets with unclear licences, or personal data.
- Make claims in docs or the paper that no experiment supports.

## 14. Definition of done

A task is done when: code is implemented within the correct module; lint, type checks and relevant tests pass; migrations (if any) are included and reversible; docs and config examples are updated; security and privacy rules above are respected; and the change is explainable in one or two sentences, including *why* it uses (or avoids) an LLM.

## 15. MVP scope (freeze at about week 14)

In scope: auth, profile and diagnostic, 3 to 5 curated companies, OA simulator with Judge0, BKT skill profile with forgetting and prerequisite graph, recommendations with reasons, text-based technical interview with tiered evaluation, basic dashboard, source registry plus first collectors.
Advanced (after MVP, behind flags): experience NLP pipeline at scale, RAG polish, voice GD, bandit/LTR/ILP, calibrated readiness with conformal bands, resume-based project questions.
