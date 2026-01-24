import logging
import os
import asyncio
from contextlib import asynccontextmanager
from typing import Any

import asyncpg
from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException, status
from pydantic import BaseModel

from database.migrations import MIGRATIONS
from services.dtos.UpdateUserPayload import UpdateUserPayload
from services.UserService import UserService
from services.HealthService import HealthService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()


class APIResponse(BaseModel):
    msg: str
    data: Any | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Connect to database on startup with retries
    max_retries = 5
    base_delay = 2
    
    for attempt in range(max_retries):
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
            health_service = HealthService(pool)
            current_date = await health_service.check_db_connection()
            logger.info(f"Successfully connected to database! Current date: {current_date}")
            
            # Run migrations
            for migration in MIGRATIONS:
                await migration(pool)
                
            # If we get here, connection and migrations were successful
            break
            
        except Exception as e:
            if attempt < max_retries - 1:
                delay = base_delay * (2 ** attempt)
                logger.warning(f"Failed to connect to database (attempt {attempt + 1}/{max_retries}): {e}. Retrying in {delay}s...")
                await asyncio.sleep(delay)
            else:
                logger.error(f"Final failure connecting to database after {max_retries} attempts: {e}")
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


@app.post("/users", response_model=APIResponse)
async def create_or_update_user(payload: UpdateUserPayload, request: Request) -> APIResponse:
    pool = getattr(request.app.state, "pool", None)
    if not pool:
         raise HTTPException(
             status_code=status.HTTP_503_SERVICE_UNAVAILABLE, 
             detail="Database not available"
         )
    
    user_service = UserService(pool)
    msg = await user_service.process_user_payload(payload)
    
    return APIResponse(msg=msg)
