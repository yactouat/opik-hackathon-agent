import logging
import asyncpg
from fastapi import HTTPException, status
from services.dtos.UpdateUserPayload import UpdateUserPayload

logger = logging.getLogger(__name__)

class UserService:
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    @staticmethod
    def validate_authorization(token_sub: str, expected_id: str, error_detail: str) -> None:
        """
        Validates that the token subject matches the expected user ID.
        Raises HTTPException 401 if they don't match.
        """
        if token_sub != expected_id:
             raise HTTPException(
                 status_code=status.HTTP_401_UNAUTHORIZED,
                 detail=error_detail
             )

    async def process_user_payload(self, payload: UpdateUserPayload) -> str:
        """
        Process a user update payload: create user if not exists, update if exists and changed.
        """
        if not self.pool:
             raise HTTPException(
                 status_code=status.HTTP_503_SERVICE_UNAVAILABLE, 
                 detail="Database not available"
             )
        
        async with self.pool.acquire() as conn:
            # Check if user exists by email
            existing_user = await conn.fetchrow("SELECT * FROM users WHERE email = $1", payload.email)

            ERROR_PROCESSING_USER = "Error processing user"
            
            if existing_user:
                # User exists
                db_unique_id = existing_user['unique_id']
                
                # DO NOT allow updates if the unique id present in the payload does not match the unique id present in DB
                UserService.validate_authorization(payload.sub, db_unique_id, ERROR_PROCESSING_USER)
                
                # Update only the fields that have changed BUT NEVER UPDATE unique id
                # We assume email is the key, so we don't update it.
                if existing_user['full_name'] != payload.full_name or existing_user['city'] != payload.city:
                    await conn.execute("""
                        UPDATE users 
                        SET full_name = $1, city = $2 
                        WHERE email = $3
                    """, payload.full_name, payload.city, payload.email)
                    return "User updated"
                else:
                    return "User already up to date"
                
            else:
                # If user does not exist create one (sub being the unique_id of the user)
                try:
                    await conn.execute("""
                        INSERT INTO users (email, full_name, city, unique_id)
                        VALUES ($1, $2, $3, $4)
                    """, payload.email, payload.full_name, payload.city, payload.sub)
                except asyncpg.UniqueViolationError:
                     raise HTTPException(
                         status_code=status.HTTP_401_UNAUTHORIZED,
                         detail=ERROR_PROCESSING_USER
                     )
                
                return "User payload processed successfully"
