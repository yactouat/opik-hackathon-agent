import logging
import os
from contextlib import asynccontextmanager
from typing import Any

import asyncpg
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from pydantic import BaseModel

from database.migrations import migrate_users_table

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()


class APIResponse(BaseModel):
    msg: str
    data: Any | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Connect to database on startup
    try:
        pool = await asyncpg.create_pool(
            user=os.getenv("POSTGRES_USER", "postgres"),
            password=os.getenv("POSTGRES_PASSWORD", "postgres"),
            database=os.getenv("POSTGRES_DB", "app"),
            host=os.getenv("POSTGRES_HOST", "localhost"),
            port=os.getenv("POSTGRES_PORT", "5432"),
        )
        app.state.pool = pool
        
        # Run basic query to verify connection
        async with pool.acquire() as conn:
            current_date = await conn.fetchval("SELECT CURRENT_DATE")
            logger.info(f"Successfully connected to database! Current date: {current_date}")
        
        # Run migrations
        await migrate_users_table(pool)
            
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        # We don't block startup, but DB features won't work
        app.state.pool = None

    yield

    # Cleanup on shutdown
    if getattr(app.state, "pool", None):
        await app.state.pool.close()


app = FastAPI(lifespan=lifespan)


@app.get("/", response_model=APIResponse)
def root(request: Request) -> APIResponse:
    db_connected = getattr(request.app.state, "pool", None) is not None
    return APIResponse(
        msg="Paramis API is up and running",
        data={
            "status": {
                "database": db_connected
            }
        }
    )
