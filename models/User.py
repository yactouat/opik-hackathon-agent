from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field

class User(BaseModel):
    """
    Represents a user in the system.
    """
    id: Optional[int] = Field(default=None, description="Unique identifier for the user")
    unique_id: Optional[str] = Field(default=None, description="Unique ID of the user")
    bio: Optional[str] = Field(default=None, description="Biography of the user")
    city: str = Field(description="City where the user resides")
    created_at: Optional[datetime] = Field(default=None, description="Timestamp when the user was created")
    email: str = Field(description="Email address of the user")
    full_name: str = Field(description="Full name of the user")
    interests: Optional[List[str]] = Field(default=None, description="List of user interests")