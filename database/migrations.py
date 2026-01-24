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

async def add_unique_id_column(pool: asyncpg.Pool):
    """
    Adds unique_id column to users table if it doesn't exist and ensures it is unique.
    """
    check_column_query = """
    SELECT EXISTS (
        SELECT FROM information_schema.columns 
        WHERE table_schema = 'public' 
        AND table_name = 'users' 
        AND column_name = 'unique_id'
    );
    """
    
    alter_table_query = """
    ALTER TABLE users ADD COLUMN IF NOT EXISTS unique_id TEXT;
    """

    add_unique_index_query = """
    CREATE UNIQUE INDEX IF NOT EXISTS users_unique_id_idx ON users (unique_id);
    """
    
    try:
        async with pool.acquire() as conn:
            column_exists = await conn.fetchval(check_column_query)
            
            if not column_exists:
                await conn.execute(alter_table_query)
                logger.info("Added unique_id column to users table.")
            else:
                logger.info("unique_id column already exists in users table, skipping add column.")
            
            # Always try to ensure uniqueness
            await conn.execute(add_unique_index_query)
            logger.info("Ensured unique index on unique_id column.")
                
    except Exception as e:
        logger.error(f"Error adding unique_id column: {e}")
        raise e

async def make_email_unique(pool: asyncpg.Pool):
    """
    Ensures that the email column in the users table is unique.
    """
    query = """
    CREATE UNIQUE INDEX IF NOT EXISTS users_email_idx ON users (email);
    """
    
    try:
        async with pool.acquire() as conn:
            await conn.execute(query)
            logger.info("Ensured unique index on email column.")
    except Exception as e:
        logger.error(f"Error making email unique: {e}")
        raise e

MIGRATIONS = [
    migrate_users_table,
    add_unique_id_column,
    make_email_unique,
]
