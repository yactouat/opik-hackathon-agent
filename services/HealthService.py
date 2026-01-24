import asyncpg
import logging

logger = logging.getLogger(__name__)

class HealthService:
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def check_db_connection(self) -> str:
        """
        Run a basic query to verify database connection.
        """
        async with self.pool.acquire() as conn:
            current_date = await conn.fetchval("SELECT CURRENT_DATE")
            return str(current_date)
