from typing import Optional
from pydantic import BaseModel, Field

class InteractionWithAPersonCard(BaseModel):
    """
    A card that represents an interaction with a person, following the 5 Ws (Who, Where, When, Why, How).
    """
    who: str = Field(description="The name of the person with whom the interaction took place")
    where: Optional[str] = Field(default=None, description="Where the interaction took place")
    when: Optional[str] = Field(default=None, description="When the interaction took place")
    why: Optional[str] = Field(default=None, description="Why the interaction took place (the reason/purpose)")
    how: Optional[str] = Field(default=None, description="How the interaction took place (the context/manner)")
