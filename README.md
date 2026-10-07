# Smart Prep (PrepAI)
## Personalized Placement Preparation and Realistic Interview Simulation System

[![FastAPI](https://img.shields.io/badge/FastAPI-0.121+-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18+-61DAFB.svg?logo=react&logoColor=black)](https://reactjs.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16+-336791.svg?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Tailwind CSS](https://img.shields.io/badge/TailwindCSS-3.4+-38B2AC.svg?logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
[![Ollama](https://img.shields.io/badge/Ollama-Qwen2.5--3B-black.svg?logo=ollama&logoColor=white)](https://ollama.com/)

Smart Prep is an end-to-end intelligent placement preparation platform. It combines company-specific hiring intelligence, adaptive evaluation (Bayesian Knowledge Tracing), realistic Online Assessment (OA) sandboxing, and hybrid AI mock interview simulations (OA, GD, and Technical Interviews) to provide candidate-tailored readiness roadmaps.

---

## 🌟 Key Highlights & Modules

1. **Candidate Profile & Diagnostic (Module 1)**:
   - Topic taxonomy mapping (~40 CS/DSA topics).
   - Automated resume parsing (`pdfplumber` + local `Qwen2.5-3B` JSON extraction with Pydantic validation).
   - Secure private resume storage with signed expiring URLs (via **Supabase Storage**).
   - 15-question diagnostic quiz setting initial Bayesian Knowledge Tracing priors $P(L_0)$.

2. **Company Hiring Intelligence (Module 2 & 11)**:
   - Empirical topic frequencies and difficulty profiles derived from real interview observations.
   - Materialized hiring stages, OA structure, and recency-decayed trend analysis.

3. **Data Collection & Real-Time Experiences (Module 3 & 19)**:
   - Scrapy & platform-based interview experience ingestion.
   - Deduplication using content hashing and vector similarity (`bge-small` embeddings + `pgvector`).

4. **Realistic Online Assessment Simulation (Module 4)**:
   - Server-authoritative timed tests.
   - Code execution sandbox using self-hosted **Judge0 CE** (supporting multi-language execution and partial scoring).
   - Monaco code editor with test case validation and performance metrics.

5. **Group Discussion Simulation (Module 5)**:
   - Turn-based multi-persona discussion powered by LLM.
   - Speech-to-text with `faster-whisper` and metrics on pace, filler words, and argument clarity.

6. **Adaptive Technical Interview Engine (Module 6 & 7)**:
   - Deterministic finite-state machine (FSM) controlling flow and difficulty tiers.
   - Tiered low-token evaluator (Tier 1 vector similarity vs. Tier 2 targeted LLM verification).

7. **Personalized Analytics & Dynamic Roadmap (Module 8, 9 & 10)**:
   - Topic mastery tracking via Bayesian Knowledge Tracing (BKT).
   - Adaptive problem recommender using MMR knapsack diversity scoring.
   - Dynamic week-by-week preparation plan.

---

## 🏗️ Architecture & Technology Stack

| Layer | Technologies |
|---|---|
| **Frontend** | React 18, Vite, TypeScript, Tailwind CSS, Monaco Editor, Recharts, Lucide React |
| **Backend API** | FastAPI, Pydantic v2, SQLAlchemy (Async), Alembic |
| **Primary Database** | PostgreSQL 16+ with `pgvector` extension |
| **Object Storage** | Supabase Storage (Private bucket with signed URLs) |
| **Task Queue & Cache** | Redis + RQ (Redis Queue) |
| **Code Execution Sandbox** | Judge0 CE (Dockerized) |
| **AI / NLP** | Ollama (`Qwen2.5-3B`), `bge-small-en-v1.5` embeddings, `faster-whisper` |
| **Offline Data Science** | Pandas, Scikit-learn, NumPy |

---

## 📂 Project Structure

```text
Smart Prep/
├── backend/
│   ├── app/
│   │   ├── config/          # Pydantic environment settings
│   │   ├── database/        # Database connection & models
│   │   ├── routers/         # API routes (auth, candidate, questions, etc.)
│   │   ├── schemas/         # Pydantic request/response schemas
│   │   ├── services/        # Business logic & LLM gateway
│   │   ├── bkt/             # Bayesian Knowledge Tracing algorithms
│   │   └── utils/           # Serializers & security helpers
│   ├── requirements.txt     # Python dependencies
│   └── requirements-ml.txt  # ML/data processing dependencies
│
├── frontend/
│   ├── src/
│   │   ├── components/      # Reusable UI components & Monaco wrapper
│   │   ├── pages/           # Application views (Dashboard, OA, Profile, etc.)
│   │   ├── services/        # Axios API clients
│   │   └── types/           # TypeScript definitions
│   ├── package.json
│   └── vite.config.ts
│
├── data/                    # Raw & processed company question datasets
├── features/                # Topic feature engineering scripts
├── models/                  # Clustering & company similarity models
├── profiling/               # Company profile generation logic
├── outputs/                 # Generated matrices, plots, and cluster outputs
├── Implementation_Plan.md   # Complete system architecture & module guide
└── main.py                  # Offline data preprocessing & profiling pipeline
```

---

## 🚀 Getting Started

### Prerequisites
- **Python**: 3.10+
- **Node.js**: 18+ and `npm`
- **PostgreSQL**: 15+ (with `pgvector` enabled)
- **Supabase Account**: (For private resume object storage)
- **Ollama**: (For local LLM inference)

---

### 1. Backend Setup

1. **Navigate to the backend directory and set up a virtual environment:**
   ```bash
   cd backend
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables:**
   Create a `.env` file inside `backend/` (or copy from `.env.example`):
   ```env
   # Application
   ENVIRONMENT=development
   FRONTEND_ORIGIN=http://localhost:5173

   # Database (PostgreSQL)
   DATABASE_URL=postgresql+asyncpg://postgres:your_password@localhost:5432/smart_prep

   # Authentication
   JWT_SECRET=your_super_secret_key_at_least_32_chars
   JWT_ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=10080

   # Supabase Storage (Resumes)
   SUPABASE_URL=https://<your-project-ref>.supabase.co
   SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key
   SUPABASE_BUCKET_NAME=resumes
   SUPABASE_SIGNED_URL_EXPIRY_SECONDS=900

   # Local LLM
   OLLAMA_BASE_URL=http://localhost:11434
   OLLAMA_MODEL=qwen2.5:3b
   ```

4. **Start the FastAPI backend server:**
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

---

### 2. Frontend Setup

1. **Navigate to the frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install Node dependencies:**
   ```bash
   npm install
   ```

3. **Start the Vite development server:**
   ```bash
   npm run dev
   ```
   Open `http://localhost:5173` in your browser.

---

### 3. Local LLM Setup (Ollama)

For local resume parsing and interview simulation:
```bash
# Pull and start Qwen 2.5 (3B parameters)
ollama pull qwen2.5:3b
ollama serve
```

---

### 4. Running Offline Company Intelligence Pipeline

To preprocess company question datasets and build similarity matrices:
```bash
python main.py
```
Outputs and cluster plots will be generated in the `outputs/` directory.

---

## 📖 Documentation
Detailed module-by-module architecture, formulas, BKT specification, and engineering decisions can be found in [Implementation_Plan.md](Implementation_Plan.md).
