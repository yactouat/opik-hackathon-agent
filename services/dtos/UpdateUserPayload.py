from pydantic import BaseModel, Field

class UpdateUserPayload(BaseModel):
    city: str = Field(description="City of the user")
    email: str = Field(description="Email address of the user")
    full_name: str = Field(description="Full name of the user")
    sub: str = Field(description="Subject identifier (UUID)")
