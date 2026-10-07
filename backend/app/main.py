import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config.settings import get_settings
from app.database.init_db import init_db
from app.database.mongodb import close_mongo_connection, connect_to_mongo
from app.routers import admin, assessments, attempts, auth, candidate, companies, questions, recommendations

logger = logging.getLogger("uvicorn")
settings = get_settings()

app = FastAPI(title="PrepAI Placement Intelligence API", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin, "http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup() -> None:
    try:
        logger.info("Initializing PostgreSQL database...")
        await init_db()
        logger.info("PostgreSQL database initialized successfully.")
    except Exception as e:
        logger.error(f"PostgreSQL initialization failed: {e}")

    try:
        await connect_to_mongo()
        logger.info("MongoDB connected.")
    except Exception as e:
        logger.warning(f"MongoDB connection skipped or failed: {e}")


@app.on_event("shutdown")
async def shutdown() -> None:
    await close_mongo_connection()


@app.get("/api/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "PrepAI API"}


app.include_router(auth.router)
app.include_router(candidate.router)
app.include_router(companies.router)
app.include_router(questions.router)
app.include_router(attempts.router)
app.include_router(recommendations.router)
app.include_router(assessments.router)
app.include_router(admin.router)
