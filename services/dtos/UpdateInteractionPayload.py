from pydantic import BaseModel, Field

class UpdateInteractionPayload(BaseModel):
    input: str = Field(..., description="Context of the interaction")
    user_id: str = Field(..., description="Unique ID of the first user (the one recording the interaction)")
    target_user_id: str = Field(..., description="Unique ID of the second user (the target of the interaction)")
    sub: str = Field(..., description="Unique ID of the requester for validation")
