from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import text
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database URL from environment variables
DATABASE_URL = os.getenv("DATABASE_URL")

# Create an asynchronous engine for database operations
# The engine is the source of database connectivity and behavior.
# echo=True will log all SQL statements.
engine = create_async_engine(DATABASE_URL, echo=True, pool_pre_ping=True)

# Create a configured "Session" class.
# This is the factory for creating new Session objects.
SessionLocal = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False,
)

# A base class for declarative class definitions.
Base = declarative_base()

# Dependency to get a database session.
# This will create a new session for each request and close it when the request is finished.
# This is the recommended way to handle sessions in FastAPI.
async def get_db():
    """
    Dependency that provides a database session to the route.
    Ensures that the session is always closed after the request is finished.
    """
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def check_db_connection():
    """
    Checks if a connection to the database can be established.
    Returns True if the connection is successful, False otherwise.
    """
    try:
        async with engine.connect() as connection:
            await connection.execute(text("SELECT 1"))
        return True
    except Exception:
        return False

def get_pool_status():
    """
    Returns the status of the connection pool.
    """
    return engine.pool.status()