from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.config.settings import get_settings


client: AsyncIOMotorClient | None = None
database: AsyncIOMotorDatabase | None = None


async def connect_to_mongo() -> None:
    global client, database
    settings = get_settings()
    client = AsyncIOMotorClient(settings.mongodb_uri)
    database = client[settings.database_name]
    await database.command("ping")
    await create_indexes(database)


async def close_mongo_connection() -> None:
    global client, database
    if client:
        client.close()
    client = None
    database = None


def get_database() -> AsyncIOMotorDatabase | None:
    return database


async def create_indexes(db: AsyncIOMotorDatabase) -> None:
    await db.users.create_index("email", unique=True)
    await db.candidate_profiles.create_index("user_id", unique=True)
    await db.skill_mastery.create_index([("user_id", 1), ("topic", 1)], unique=True)
    await db.questions.create_index("question_id")
    await db.questions.create_index("question_key")
    await db.companies.create_index("company_id", unique=True)
    await db.company_oa_profiles.create_index("company_id", unique=True)
    await db.candidate_attempts.create_index([("user_id", 1), ("timestamp", -1)])
    await db.recommendations.create_index([("user_id", 1), ("generated_at", -1)])
