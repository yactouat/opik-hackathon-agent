import asyncpg
import logging

logger = logging.getLogger(__name__)

async def migrate_users_table(pool: asyncpg.Pool):
    """
    Migrates the users table in the database.
    
    Schema:
    - mandatory: city, email, full_name
    - optional: bio, interests (array of strings)
    """
    create_table_query = """
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        email TEXT NOT NULL UNIQUE,
        full_name TEXT NOT NULL,
        city TEXT NOT NULL,
        bio TEXT,
        interests TEXT[],
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    check_table_query = """
    SELECT EXISTS (
        SELECT FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name = 'users'
    );
    """
    
    try:
        async with pool.acquire() as conn:
            # Check if table exists before attempting creation
            table_exists = await conn.fetchval(check_table_query)
            
            if not table_exists:
                await conn.execute(create_table_query)
                logger.info("Created users table.")
            else:
                logger.info("Users table already exists, skipping creation.")
                
    except Exception as e:
        logger.error(f"Error migrating users table: {e}")
        raise e
