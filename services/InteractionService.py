import logging
import asyncpg
from fastapi import HTTPException, status
from services.dtos.UpdateInteractionPayload import UpdateInteractionPayload
from services.UserService import UserService
from graphs.extract_interaction_with_a_person_card import extract_interaction_with_a_person_card_graph
from models.InteractionWithAPersonCard import InteractionWithAPersonCard
from opik.integrations.langchain import OpikTracer

logger = logging.getLogger(__name__)

class InteractionService:
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def create_interaction(self, payload: UpdateInteractionPayload) -> str:
        if not self.pool:
             raise HTTPException(
                 status_code=status.HTTP_503_SERVICE_UNAVAILABLE, 
                 detail="Database not available"
             )

        # 1. Validate requester
        UserService.validate_authorization(payload.sub, payload.user_id, "Unauthorized: Requester must be the user recording the interaction")

        async with self.pool.acquire() as conn:
            # 2. Get User IDs (integers) from Unique IDs (strings)
            # We can do this in one query or two. Two is clearer for error reporting.
            
            # Get User (Recorder)
            user_row = await conn.fetchrow(
                "SELECT id FROM users WHERE unique_id = $1", 
                payload.user_id
            )
            if not user_row:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"User not found: {payload.user_id}"
                )
            user_db_id = user_row['id']

            # Get Target User
            target_user_row = await conn.fetchrow(
                "SELECT id FROM users WHERE unique_id = $1", 
                payload.target_user_id
            )
            if not target_user_row:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Target user not found: {payload.target_user_id}"
                )
            target_user_db_id = target_user_row['id']

            # 3. Process with Graph
            tracer = OpikTracer(graph=extract_interaction_with_a_person_card_graph.get_graph(xray=True))
            inputs = {"input": payload.input}
            
            try:
                result = await extract_interaction_with_a_person_card_graph.ainvoke(
                    inputs,
                    config={"callbacks": [tracer]}
                )
            except Exception as e:
                logger.error(f"Error processing interaction graph: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="An unexpected error occurred while processing the request."
                )

            if "error" in result and result["error"]:
                 logger.error(f"Graph extraction error: {result['error']}")
                 raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="The interaction content could not be processed."
                )

            interaction_card: InteractionWithAPersonCard = result.get("interaction_card")
            if not interaction_card:
                logger.error("Graph did not return an interaction card")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="An unexpected error occurred."
                )

            # 4. Save to Database
            try:
                await conn.execute("""
                    INSERT INTO interactions (who, "where", "when", why, how, user_id, target_user_id)
                    VALUES ($1, $2, $3, $4, $5, $6, $7)
                """, 
                interaction_card.who,
                interaction_card.where,
                interaction_card.when,
                interaction_card.why,
                interaction_card.how,
                user_db_id,
                target_user_db_id
                )
            except Exception as e:
                logger.error(f"Error saving interaction to DB: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="An unexpected error occurred."
                )

            return "Interaction recorded successfully"
