from pydantic import BaseModel, ConfigDict


class Ticket(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    status: str
    assignee: str
    priority: str
    layout: str
    acceptance_has_items: bool
    acceptance_unchecked: int
    plan_has_approach: bool
    docs: list[str]
