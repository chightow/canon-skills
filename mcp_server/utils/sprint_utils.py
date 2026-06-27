from pathlib import Path
from typing import List, Dict, Any
from .parsers import parse_tickets, parse_handoff
from .models import Ticket

def get_sprint_board(project_root: Path) -> List[Dict[str, Any]]:
    tickets_dir = project_root / ".tickets"
    handoff_path = project_root / "HANDOFF.md"
    
    tickets = parse_tickets(tickets_dir)
    handoff_data = parse_handoff(handoff_path)
    
    # Aggregate data
    board = {
        "active_tasks": handoff_data.get("active_tasks", []),
        "tickets": [t.dict() for t in tickets],
        "context": handoff_data.get("context", "No context found")
    }
    
    return board
