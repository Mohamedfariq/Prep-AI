# Personalized Placement Preparation and Realistic Interview Simulation System
## Module-wise Tech Stack and Implementation Guide (v2)

**Global stack:** React + Vite + TypeScript + Tailwind + Monaco | FastAPI + SQLAlchemy + Alembic | PostgreSQL + pgvector | Redis + RQ | Judge0 CE | Ollama (Qwen2.5-3B) + API fallback | bge-small embeddings + MiniLM cross-encoder | faster-whisper | Scrapy + Playwright (collection) | Docker Compose, Vercel, GitHub Actions.

Every module lists the **options considered**, the **pick**, and a table of **Requirement | Tech stack | Implementation**.

---

## Module 1: Candidate Profile

**Options:** Resume parsing: regex / spaCy NER / pdfplumber + LLM / commercial parser. Skill entry: free text / taxonomy selector.
**Pick:** pdfplumber + local LLM (JSON schema); taxonomy-linked selector; Postgres tables + JSONB.

| Requirement | Tech stack | Implementation |
|---|---|---|
| Skills, languages, DSA, CS fundamentals | Postgres, React multi-select | `candidate_profiles` + `skill_profiles` keyed to a fixed topic taxonomy (`taxonomy.yaml`, about 40 topics). Self-rating seeds the prior. |
| Projects, resume info | pdfplumber, Qwen2.5-3B, Pydantic, private object storage | Optional PDF upload. pdfplumber extracts text; the LLM returns `{skills, projects, education}`; Pydantic validates; the user reviews and edits before saving. |
| Previous performance, prep history | SQL views | Read from `performance_history`, `oa_attempts`, `technical_interviews`. Nothing is stored twice. |
| Target companies | Postgres (many-to-many) | Link to `companies`; one marked primary. |
| Initial mastery | Python, React quiz | A 15-question diagnostic sets `P(L0)` per topic (blend with self-rating, 70/30). |
| Resume privacy | Signed URLs, FastAPI | Delete endpoint; PII stripped before any external API call. |

---

## Module 2: Company Hiring Intelligence

**Options:** Storage: JSONB profile / normalized tables. Aggregation: live queries / materialized views + nightly job.
**Pick:** Postgres materialized views + RQ nightly job; Bayesian shrinkage; admin review queue.

| Requirement | Tech stack | Implementation |
|---|---|---|
| Hiring stages, OA structure, GD, interview patterns | Postgres JSONB, admin UI | `companies.hiring_stages`, hand-curated for 3 to 5 companies, edited by admin. |
| Frequent topics, CS fundamentals, project/behavioral patterns | SQL, pandas | Aggregate `questions` by topic: `freq(t) = (n_t + α·p0(t)) / (N + α)`, α about 10, `p0` = static prior. |
| Difficulty, round importance | SQL | Mean difficulty per round; round importance set manually, later tuned from outcomes. |
| Recent trends | SQL, NumPy | Recency-weighted counts `w = 2^(−age/h)`, h = 180 days. Trend = slope over the last 3 windows. |
| Static + dynamic combination | Python aggregation job | Static data = prior; experiences = weighted evidence (Module 3). Profile changes only via the aggregation job. |
| Unreliable data control | Python, RQ | Report weight `w_i = s_src · τ_user · 2^(−age/h) · q_i`; pending quarantine; shrinkage; review queue. |
| Explainability | React | Every insight shows report count, confidence and last-seen date. |

---

## Module 3: Real-Time Interview Experience Collection

**Options:** Extraction: rules only / LLM only / hybrid. Classifier: zero-shot / TF-IDF + LR / embedding + LightGBM.
**Pick:** Hybrid (rules + embedding match, then LLM fallback); embedding + logistic regression once about 300 labels exist; RQ workers.

| Requirement | Tech stack | Implementation |
|---|---|---|
| Submission form | React, Pydantic, Redis rate limit | Company/role autocomplete, year, stage, rounds, difficulty, outcome, free text. Size limits and rate limit. |
| Cleaning and segmentation | Python, regex, langdetect | PII strip, spam filter, split into question segments. |
| Matching to known questions | bge-small, pgvector | Similarity ≥ 0.85 links to an existing question (no LLM). |
| Extraction of unmatched segments | Qwen2.5-3B, Pydantic | One LLM call returns `{topic, concept, difficulty, round, follow_ups}` from a closed topic list; validate, retry once. Example ("longest substring… sliding window") yields Strings / Sliding Window / Medium / Technical / follow-up "justify algorithm choice". |
| Dedupe | hashlib, pgvector | Exact hash, then embedding similarity ≥ 0.9 merges and raises the report count. |
| Trust | Postgres, Python | `τ_user` from account age, verified outcome and past flags. New reports stay `pending`. |
| Profile update | RQ | Approval triggers an incremental recompute for that company only. |

---

## Module 4: Realistic OA Simulation

**Options:** Execution: Judge0 CE / Piston / custom Docker / gVisor. Timer: client-only / server-authoritative. Aptitude: LLM-generated / templated / curated.
**Pick:** Self-hosted Judge0 CE; server-authoritative timer; templated and curated aptitude; Monaco; Recharts.

| Requirement | Tech stack | Implementation |
|---|---|---|
| Dynamic assessment | FastAPI, Postgres | Blueprint from the company profile, e.g. `{coding: 2, aptitude: 15, CS_MCQ: 10, time: 90}`. |
| Question selection | Python scoring, MMR | `score(q) = α·weakness + β·freq·Conf + γ·difficultyMatch − δ·recentlySeen`; top-n per section with MMR. |
| Sections | Judge0, Python templates, curated bank | Coding (Judge0); aptitude/reasoning (templated with parametrized numbers, so answer keys are always correct); CS MCQ (curated); debugging (buggy code with hidden tests). |
| Timer | FastAPI, WebSocket/polling | Server stores `start_ts` and `deadline`; client displays; late submissions rejected. |
| Auto-evaluation, test cases, partial scoring | Judge0 batch API | Visible and hidden cases; `partial = Σ weight_i · pass_i`. |
| Metrics (time, attempts, accuracy, topic, difficulty) | SQL on `oa_question_results` | Computed in SQL, never by the LLM. |
| Report | Recharts, Qwen2.5-3B | Dashboard plus one LLM paragraph summarizing the metrics. |
| Integrity | JS event listeners | Log tab switches and paste events (log only, no auto-fail). |
| Downstream | Postgres | Results written to `performance_history` and feed the skill model. |

---

## Module 5: Group Discussion Simulation

**Options:** STT: Whisper / faster-whisper / Vosk / cloud STT / Web Speech API. Evaluation: LLM-only / separate trained models / hybrid.
**Pick:** faster-whisper `small` int8 on CPU; hybrid deterministic metrics + rubric LLM; turn-based flow.

| Requirement | Tech stack | Implementation |
|---|---|---|
| Topic generation | Curated topic bank, Qwen2.5-3B | Topics by category; the LLM only rephrases or varies. |
| Preparation time | FastAPI timer, React | 2 to 3 minutes with a notes box. |
| Multiple participants | Qwen2.5-3B (JSON output) | One call per round returns all 2 to 3 personas' turns as a JSON array (distinct stances, short turns). |
| Candidate response | MediaRecorder, faster-whisper | Record or type; transcribe with timestamps. |
| Filler words, pace, talk share, turn length | Python (regex, timestamps) | Deterministic from transcript and timing. |
| Repetition, relevance | bge-small embeddings | Similarity between the candidate's own turns and to the topic/previous turn. |
| Reasoning, evidence, counter-arguments, leadership, listening, clarity | Qwen2.5-3B (rubric prompt) | Scores 1 to 5 per dimension with an evidence quote. |
| Confidence | Python | Proxy from pace, hesitation and filler rate, labeled as a proxy in the UI. |

---

## Module 6: Technical Interview Simulation

**Options:** Orchestration: LangGraph / LangChain agents / custom state machine. Evaluation: LLM-only / embedding coverage / tiered. Streaming: polling / SSE / WebSocket.
**Pick:** Custom state machine; tiered evaluator; SSE.

| Requirement | Tech stack | Implementation |
|---|---|---|
| Adaptive flow | Python enum + transition table | See Module 17; driven by evaluation score and missing concepts. |
| Evaluation, tier 1 | bge-small, NumPy | Each question stores `key_points[]`; embed answer sentences; cosine coverage per key point plus keyword checks. |
| Evaluation, tier 2 | Qwen2.5-3B via Ollama, Pydantic | Only when coverage is 0.4 to 0.7: input question + key points + answer; output `{covered, missing, incorrect_claims, score}`. |
| Follow-ups | Postgres JSONB follow-up trees | Keyed by the missing concept (BFS → why BFS for shortest path → weighted edges → Dijkstra). LLM only if no node matches. |
| Dynamic control | Python rules | Difficulty ±1 level, topic, depth cap 3, question count, time left. |
| Coding question | Judge0, Qwen2.5-3B | Judge0 for correctness; one LLM call for complexity and style feedback. |
| Final report | SQL, API LLM | Aggregated topic scores plus one feedback call. |

---

## Module 7: Low-Token Adaptive Interview Engine

**Pick:** Structured state instead of transcript, JSON-only prompts, small local model, Redis caching, retrieval before generation.

| Technique | Tech stack | Implementation |
|---|---|---|
| Avoid full history | Redis/Postgres session state | State JSON: asked questions, topic scores, missing concepts, depth, time left, one-line summary of the last exchange (about 200 to 400 tokens). |
| Structured prompts, JSON responses | Pydantic | Fixed schema, validation, one retry, short outputs. |
| Smaller and local models | Ollama, Qwen2.5-3B | Local model for most calls; API model only for the final report and disputed evaluations. |
| RAG and question banks | pgvector, SQL | Next question chosen by SQL + vector retrieval, no LLM. |
| Pre-generated follow-ups | Postgres JSONB | About 150 to 200 questions with trees, drafted offline by an LLM and human-reviewed. |
| Embeddings and similarity | bge-small | Tier 1 evaluation and duplicate-answer detection. |
| Rule-based transitions | Python | Thresholds on score (≥0.75, 0.4 to 0.75, <0.4). |
| Caching | Redis | Key `(question_id, hash(normalized_answer))`; prefix caching for the static system prompt. |
| Summarization and compression | Qwen2.5-1.5B | One-line rolling summary per turn; drop raw text after evaluation. |
| Measurement | Prometheus/logging or a `llm_calls` table | Log tokens and calls per interview; compare with an LLM-every-turn baseline. |

---

## Module 8: Personalized Performance Analysis

**Options:** Rule-based / weighted / BKT / IRT / ML (DKT, LightGBM).
**Pick:** BKT per topic (primary), weighted score for display, Elo-style difficulty calibration.

| Requirement | Tech stack | Implementation |
|---|---|---|
| Topic scores | Custom Python BKT (about 60 lines) | Update `P(L)` per outcome: correct → `P(L)(1−slip) / [P(L)(1−slip) + (1−P(L))·guess]`; wrong → `P(L)·slip / [P(L)·slip + (1−P(L))(1−guess)]`; then add `(1−P(L|obs))·P(T)`. Weight by partial score and difficulty. |
| Strong and weak topics | SQL | Weak if mastery < 0.5 after ≥ 3 observations. |
| Knowledge gaps | SQL on interview evaluations | Count concepts in `missing[]`. |
| Repeated mistakes | Judge0 verdicts, error tags, SQL | Flag tags with ≥ 3 occurrences per user. |
| Time management | SQL | Compare time per question against expected time for the difficulty. |
| Communication weakness | GD/interview rubric scores | Tracked as separate skill dimensions. |
| Difficulty calibration | Python | Elo update of user ability and question difficulty. |
| Validation | scikit-learn metrics, pytest | Simulated-learner tests; AUC and log-loss versus the weighted baseline. |

---

## Module 9: Personalized Problem Recommendation

**Options:** Rule scoring / LightGBM ranker / contextual bandit.
**Pick:** Linear scoring + MMR + greedy knapsack (bandit as optional extension).

| Requirement | Tech stack | Implementation |
|---|---|---|
| Candidate generation | SQL | Filter by company/role, unsolved, within difficulty band. |
| Scoring | Python, NumPy | `P(q) = w1·Need + w2·CompanyRel + w3·Trend + w4·DiffFit + w5·Novelty − w6·Redundancy`; `Need = 1 − mastery`; `CompanyRel = freq·Conf`; `DiffFit = exp(−(d−d*)²/2σ²)`. |
| Time available | Python | Greedy knapsack by `P(q) / expected_minutes` under the daily budget. |
| Diversity | bge-small, MMR | Penalize embedding similarity to already-selected items. |
| Explanation | Python templates | Stored in `recommendations.reasons`, e.g. "Graphs 35% mastery; frequent in company OAs". No LLM. |
| Weight tuning | scikit-learn logistic regression | Start hand-set; later fit on "solved successfully" outcomes. |

---

## Module 10: Company-Specific Preparation Plan

**Options:** Fixed templates / proportional rules / optimization solver.
**Pick:** Proportional allocation with threshold rules; versioned plans.

| Requirement | Tech stack | Implementation |
|---|---|---|
| Roadmap structure | Python, Postgres JSONB | Weeks: fundamentals, company OA prep, technical prep, mocks. Last week is always mocks (OA + GD + interview). |
| Time allocation | Python | Share per topic ∝ `W_{c,t} · (1 − mastery_t)`, normalized to available hours. |
| Dynamic changes | Python rules | If mastery stays below threshold after N attempts, multiply that topic's share by 1.3 and take the time proportionally from topics above 0.85. |
| Re-planning | RQ scheduled job | Weekly and after every mock. |
| Versioning | `preparation_plans.version` | UI shows a diff between versions. |
| Readiness score | SQL + Python | `Ready(c) = Σ_r I_r · Σ_t W_{c,t} · mastery_t`. |
| UI | React, FullCalendar | Week view with a "why changed" note. |

---

## Module 11: Company-Wise Question Dataset

**Pick:** Postgres `questions` table with JSONB for follow-ups and key points; pgvector embedding column.

| Requirement | Tech stack | Implementation |
|---|---|---|
| Schema | Postgres, SQLAlchemy | `company, role, round, text, type, topic, concept, difficulty, frequency, confidence, source, last_seen, tags, key_points, follow_up_tree, embedding`. |
| Sources | Importers (Module 19) | Public datasets, curated banks, user experiences, each tagged with `source` and a reliability prior `s_src`. |
| Confidence score | Python, SQL | `Conf(q) = (1 − e^(−λ Σ w_i)) · A(q)`, with `w_i = s_src · τ_user · 2^(−age/h)`; `A(q)` = share of reports agreeing on company, round and difficulty. |
| Recency | SQL | `last_seen` plus time-decayed frequency. |
| Ingestion | pandas, bge-small, Qwen2.5-3B | CSV/JSON importer, hash dedupe, embedding dedupe, LLM-assisted labelling with human spot checks. |

---

## Module 12: AI Architecture (hybrid)

| Layer | Responsibility | Tech stack | Implementation |
|---|---|---|---|
| Deterministic | Scoring, timers, test execution, metrics, filtering | Python, SQL, Judge0 | Plain functions with unit tests. |
| Retrieval | Questions, similar questions, experiences, follow-ups | pgvector, SQL, MiniLM cross-encoder | Filter, vector search, rerank. |
| ML | Skill estimation, ranking, difficulty prediction, classification | Custom BKT, scikit-learn, LightGBM | Trained or updated offline and in jobs. |
| LLM | Dialogue, ambiguous evaluation, follow-ups, GD, feedback, extraction | Ollama Qwen2.5-3B, API fallback | A single `LLMGateway` class handling model choice, retries, JSON validation, caching, rate limiting and token logging. |

---

## Module 13: RAG Architecture

**Options:** Vector DB: FAISS / Chroma / Qdrant / pgvector. Framework: LangChain / LlamaIndex / hand-rolled.
**Pick:** pgvector (HNSW), bge-small-en-v1.5, MiniLM cross-encoder, hand-rolled pipeline.

| Requirement | Tech stack | Implementation |
|---|---|---|
| Company and role detection | rapidfuzz, alias table, LLM fallback | Fuzzy match first. |
| Metadata filtering | SQL | `WHERE company_id, round, confidence > θ` before vector search. |
| Chunking | Python | One chunk per question or experience segment, prefixed `Company | Role | Round | Topic`. |
| Retrieval and reranking | pgvector, sentence-transformers cross-encoder | Top-20 by cosine, rerank, keep top 3 to 5. |
| Generation | Qwen2.5-3B | LLM sees only retrieved items and must cite `source_ids`. |
| Hallucination prevention | Pydantic validation | Closed-context prompt with an "insufficient data" option; verify cited IDs exist in the retrieved set; confidence threshold with fallback to static content. |

---

## Module 14: Database Design

**Pick:** PostgreSQL only (JSONB + pgvector). MongoDB rejected because the data is relational and analytics are join-heavy.

| Requirement | Tech stack | Implementation |
|---|---|---|
| Tables | PostgreSQL, SQLAlchemy | users, candidate_profiles, companies, roles, topics, questions, question_topics, interview_experiences, oa_attempts, oa_question_results, coding_submissions, gd_sessions, technical_interviews, interview_messages, skill_profiles, performance_history, recommendations, preparation_plans, plus `raw_documents` and `source_registry` (Module 19). |
| Indexes | Postgres, pgvector | `questions(company_id, round, topic_id)`, HNSW on `questions.embedding`, `performance_history(user_id, ts)`. |
| Migrations and seeds | Alembic, Python scripts | Seed taxonomy and one demo user. |

---

## Module 15: Technology Stack Decisions (summary)

| Area | Options | Pick | Reason |
|---|---|---|---|
| Frontend | React, Next.js, Vue | React + Vite + Tailwind | No SSR need; static deploy |
| Backend | FastAPI, Node, Django | FastAPI | Same language as ML |
| DB | Postgres, MongoDB | Postgres + pgvector | Relational data; one store |
| Vector | FAISS, Chroma, Qdrant, pgvector | pgvector | SQL filter + vector together |
| ML | scikit-learn, XGBoost, PyTorch | scikit-learn + LightGBM | Small tabular data |
| LLM | Qwen, Llama, Phi, Gemma, API | Qwen2.5-3B + API fallback | JSON quality at small size |
| STT | Whisper, faster-whisper, Vosk | faster-whisper small | CPU-friendly |
| Sandbox | Judge0, Piston, gVisor | Judge0 CE | Limits and batching built in |
| Scraping | requests + BeautifulSoup, Scrapy, Playwright, Selenium | Scrapy (+ Playwright for JS pages) | Throttling, retries and pipelines built in |
| Auth | JWT, Firebase, Auth0 | JWT + Google OAuth | No lock-in |
| Deploy | Vercel, Render, VM, cloud | Vercel + one Docker VM | Cheap, demo-reliable |

---

## Module 16: System Architecture and Data Flow

**Pick:** Modular monolith. Each "service" is a Python package with an interface class.

| Component | Tech stack | Implementation |
|---|---|---|
| Entry and auth | React, FastAPI, JWT | Browser calls FastAPI; middleware handles auth and rate limits. |
| Application services | Python packages | `CompanyIntelService`, `OAEngine`, `GDEngine`, `InterviewEngine`, `Recommender`, `PerformanceAnalyzer`, `RAGService`, `NotificationService`, `CollectionService`. Services communicate via function calls and the database. |
| Data stores | Postgres/pgvector, Redis | Postgres is the source of truth; Redis holds cache, queue and rate-limit counters. |
| External processes | Judge0, Ollama, faster-whisper | Called over HTTP or local sockets from the services. |
| Notifications | FastAPI, SMTP or web push | Daily practice reminders and plan-change alerts. |

---

## Module 17: Interview State Machine

**States:** START, INTRO, CONCEPT_Q, EVAL, FOLLOWUP, DEEPER_FOLLOWUP, CODING_Q, CODE_EVAL, PROJECT_Q, BEHAVIORAL_Q, FINAL.

| Requirement | Tech stack | Implementation |
|---|---|---|
| Transition logic | Python enum + table | `(state, outcome) → next_state`, where `outcome` (strong, partial, weak, timeout) comes from the evaluator. |
| Guards | Python | Depth cap, question count, time left and the round blueprint from the company profile. |
| LLM-driven parts | Qwen2.5-3B | Only unscripted follow-up wording, ambiguous-answer evaluation and feedback. Transitions, topic choice, difficulty and stopping are deterministic. |
| Testing | pytest with scripted candidates | Strong, weak and vague candidates must produce distinct, reproducible paths. |

---

## Module 18: Personalization Engine

| Requirement | Tech stack | Implementation |
|---|---|---|
| Unified score | Python, NumPy | Combine candidate profile, company profile, performance, experiences, frequency, gaps and trends in `P(q)` (Module 9). |
| Outputs | Python | `personalize(user, company)` returns `{questions, plan_weights, mock_blueprint, reasons}`. |
| Ablations | YAML config | Weights live in a config file so you can run ablation experiments. |

---

# Module 19: Data Collection and Web Scraping

## Purpose

Automatically collect company-wise hiring-process facts, interview experiences, rounds, questions, and follow-ups from permitted sources. The system should maintain provenance, remove duplicates, estimate source reliability, and refresh the collected data every **2 weeks**.

## Options

- **Web crawling:** Scrapy + Playwright
- **Reddit:** PRAW / official platform APIs
- **Datasets:** Kaggle / Hugging Face APIs
- **Storage:** PostgreSQL
- **Scheduling:** Redis + RQ Scheduler
- **Text extraction:** trafilatura + BeautifulSoup
- **LLM extraction:** Qwen2.5-3B + Pydantic validation

## Pick

**Scrapy + Playwright + PRAW/APIs + PostgreSQL + Redis/RQ Scheduler**

| Requirement | Tech Stack | Implementation |
|---|---|---|
| Source registry | PostgreSQL | Store source name, URL, access method, licence/terms, robots status, reliability score `s_src`, rate limit and enabled flag. |
| GitHub collection | GitHub API | Collect permitted company-wise question repositories and verify repository licence. |
| Reddit collection | PRAW / Reddit API | Collect permitted interview-experience posts and comments. Treat Reddit content as candidate-reported evidence. |
| Web collection | Scrapy + Playwright | Scrape permitted public pages. Use Playwright only for JavaScript-heavy pages. |
| Compliance | `robots.txt` + source terms | Check `robots.txt`, respect terms, use an identifiable User-Agent, and never bypass login, CAPTCHA or paywalls. |
| Polite crawling | Scrapy AutoThrottle | Use low concurrency, delays, caching and exponential backoff. |
| Content extraction | trafilatura + BeautifulSoup | Convert raw HTML into clean readable text before processing. |
| Experience extraction | Qwen2.5-3B + Pydantic | Extract company, role, round, questions, follow-ups, topics and hiring-process facts into structured JSON. |
| Raw storage | PostgreSQL | Store `url`, `source_id`, `fetched_at`, `content_hash`, `http_status`, raw text/HTML and licence notes. Keep raw records immutable. |
| Provenance | PostgreSQL | Every extracted question/experience stores `source_id` and `raw_document_id` for attribution. |
| Deduplication | SHA-256 + pgvector | Use content hashes for exact duplicates and embedding similarity for near-duplicate experiences/questions. |
| Reliability | PostgreSQL | Maintain source reliability prior `s_src` and use it when calculating confidence. |
| Biweekly update | Redis + RQ Scheduler | Automatically run the collection pipeline every **14 days** for all enabled sources. |
| Change detection | Content hash | Compare the new content hash with the previous version and reprocess only changed content. |
| Incremental update | PostgreSQL + RQ | Preserve existing records and insert/update only new or modified experiences, rounds and questions. |
| Privacy | Regex PII scrubber | Remove names, email addresses, phone numbers and other unnecessary personal information before processing/storage. |
| Quality control | Pydantic + pytest | Validate required fields, language, minimum length, spam/anomaly checks and quarantine unusual source spikes. |
| Monitoring | Logging + Admin UI | Track source status, last update, next update, errors, records added/rejected and collection statistics. |

## Data Collection Pipeline

```text
Every 14 days
      ↓
Check enabled sources
      ↓
Check robots.txt / terms
      ↓
Detect content changes
      ↓
Collect new/modified content
      ↓
Store raw documents
      ↓
Extract interview experience
      ↓
Validate structured data
      ↓
Remove duplicates
      ↓
Apply quality/reliability checks
      ↓
Approve records
      ↓
Update PostgreSQL
      ↓
Send to Module 20

## Module 20: Data Pipeline

`Collect → Clean → Dedupe → NLP extraction → Topic/difficulty classification → Company mapping → Embedding → Store → Aggregate → Recommendation/RAG`.

| Requirement | Tech stack | Implementation |
|---|---|---|
| Stage orchestration | RQ, Redis | One job per stage, idempotent, with a `status` column (`raw`, `extracted`, `pending`, `approved`). |
| Collection input | Module 19 collectors | Raw documents enter the pipeline from `raw_documents`. |
| Classification | scikit-learn / LightGBM, Qwen2.5-3B fallback | Classifier first; LLM only for low-confidence cases. |
| Company mapping | rapidfuzz, alias table | Normalizes names ("Amazon", "AMZN", "Amazon India"). |
| Embeddings | sentence-transformers (bge-small) | Batch job after approval. |
| Aggregation | SQL, nightly RQ job | Recompute confidence, frequencies and trends; incremental update per company when new experiences are approved. |

---

## Module 21: Dashboard

**Pick:** React + shadcn/ui + Recharts + TanStack Query.

| Section | Tech stack | Implementation |
|---|---|---|
| Overview | React, `/dashboard/summary` | Readiness score, overall skill score, target company, plan week. |
| Performance | Recharts | Line charts per round type; topic radar or heatmap from `skill_profiles`. |
| Recommendations | React | Today's list with reason tooltips, weak-topic chips, suggested mock. |
| Company intelligence | Recharts | Stage timeline, topic frequency bars, trend arrows, difficulty gauge, confidence and source badges. |
| Progress | Recharts, SQL | Weekly mastery delta, problems solved, mocks completed, skill progression from `performance_history`. |

---

## Module 22: Novelty, Non-Functional Requirements and Security

**Novelty (defensible):** (1) reliability-weighted fusion of static datasets and crowd/collected experiences with shrinkage and trust; (2) cost-aware tiered interview evaluation with measured token savings; (3) one shared skill model across OA, GD and interview; (4) explainable, versioned, performance-driven planning. Standard: LLM mock interviews, RAG, code judging, a dashboard.

| Concern | Tech stack | Implementation |
|---|---|---|
| Auth and sessions | Argon2, JWT, httpOnly cookies | Short-lived access token, rotating refresh token. |
| Resume and interview privacy | Private storage, signed URLs | Delete endpoint, PII stripping. |
| Secure code execution | Judge0 containers | No network, CPU/memory/time/process limits. |
| API keys | Env secrets | Server-side only. |
| Prompt injection | Pydantic, delimited prompts | User and scraped text confined to data fields; JSON schema validation; no tool or DB access for the LLM. Scraped content is untrusted input. |
| Rate limiting | Redis token bucket | Stricter on LLM endpoints. |
| Database | Postgres roles, ORM, TLS | Least-privilege role, parameterized queries, backups. |
| Performance | Streaming (SSE), Redis cache | p95 under 300 ms (non-LLM), under 3 s per interview turn. |
| Explainability and data quality | Stored reasons, review queue | Confidence scores and source attribution on every insight. |

---

## Deployment

| Component | Tech stack | Implementation |
|---|---|---|
| Frontend | Vercel | Static build from GitHub. |
| Backend stack | Docker Compose on one VM | Services: api, worker, scheduler, postgres, redis, judge0, ollama. |
| CI/CD | GitHub Actions | Lint (ruff, tsc), tests (pytest), build, deploy on merge. |
| Demo reliability | Ollama pre-warm, seeded demo account | Keep a recorded fallback video and an API-LLM switch. |

---

## Evaluation Plan

| Metric | Tech stack | Implementation |
|---|---|---|
| Extraction F1 | scikit-learn metrics | 200 to 300 hand-labelled experiences. |
| Evaluation agreement | SciPy (Spearman), scikit-learn (κ) | Two human raters on 100 interview answers vs. tiers 1, 1+2 and full-LLM. |
| Token and call savings | `llm_calls` table | Compare with an LLM-every-turn baseline. |
| Skill-model quality | scikit-learn | AUC and log-loss versus weighted baseline. |
| Recommendation quality | Python, Likert survey | nDCG or user study. |
| RAG quality | Python | hit@k and grounding rate. |
| Collection quality | SQL, manual audit | Acceptance rate, duplicate rate, label accuracy on a 100-row audit per source. |
| Learning outcome | Spreadsheet/Python | Pre/post mock scores for 15 to 20 students. |

---

## Build Order (about 24 weeks)

Foundation (1 to 3) → question bank, source registry and first collectors (3 to 6) → company profile (4 to 6) → OA (5 to 9) → skill model (8 to 11) → recommender (11 to 14) → interview engine (13 to 18) → experience pipeline and RAG (17 to 21) → GD (20 to 22) → planner (21 to 23) → evaluation and paper (22 to 24). Freeze the MVP at week 14. Cut GD voice first if time runs short. Run the terms and robots.txt review for every source before its collector is enabled.