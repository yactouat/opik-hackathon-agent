from typing import Optional
from pydantic import BaseModel, Field

class InteractionWithAPersonCard(BaseModel):
    """
    A card that represents an interaction with a person.
    """
    additional_tags: Optional[list[str]] = Field(default=[], description="Additional tags that may describe the interaction with the person")
    shared_interests: Optional[list[str]] = Field(default=[], description="Shared interests with the person with whom the interaction took place")
    was_stimulating: Optional[bool] = Field(default=None, description="Whether the interaction with the person was particularly stimulating or not")
    where: Optional[str] = Field(default=None, description="Where the interaction with the person took place")
    when: Optional[str] = Field(default=None, description="When the interaction with the person took place")
    who: str = Field(description="The name of the person with whom the interaction took place")