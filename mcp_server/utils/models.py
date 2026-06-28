from pydantic import BaseModel, Field
from typing import List, Optional

class Ticket(BaseModel):
    id: str = Field(..., description="The unique identifier for the ticket")
    status: str = Field(..., description="The current status of the ticket (e.g., Todo, In Progress, Done)")
    acceptance_criteria: Optional[str] = Field(None, description="The criteria that must be met for the ticket to be considered complete")
    title: Optional[str] = Field(None, description="The title or summary of the ticket")
    description: Optional[str] = Field(None, description="A detailed description of the ticket")
    priority: Optional[str] = Field(None, description="The priority of the ticket (e.g., Low, Medium, High, Critical)")
