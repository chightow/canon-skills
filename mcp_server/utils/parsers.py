import os
import re
from pathlib import Path
from typing import List, Dict, Any
from .models import Ticket

def parse_tickets(tickets_dir: Path) -> List[Ticket]:
    tickets = []
    if not tickets_dir.exists():
        return tickets
    
    # Iterate through subdirectories in .tickets/
    for subdir in tickets_dir.iterdir():
        if subdir.is_dir():
            ticket_file = subdir / "ticket.md"
            if ticket_file.exists():
                content = ticket_file.read_text(encoding='utf-8')
                # Simple YAML-like frontmatter parsing
                # Looking for id, title, status, etc.
                data = {}
                # Try frontmatter first (---\n...\n---), then fall back to first line
                frontmatter_match = re.search(r'^---\n(.*?)\n---', content, re.MULTILINE | re.DOTALL)
                if frontmatter_match:
                    lines = frontmatter_match.group(1).strip().split('\n')
                    for line in lines:
                        if ':' in line:
                            key, value = line.split(':', 1)
                            data[key.strip().lower()] = value.strip()
                else:
                    # Fall back: parse first line as id, rest as body
                    first_line = content.strip().split('\n', 1)[0]
                    if first_line:
                        data['id'] = first_line.strip()
                
                # Extract Acceptance Criteria from the body
                acceptance_criteria = ""
                body_match = re.search(r'^## Acceptance Criteria\n(.*?)(?=\n\n##|$)', content, re.DOTALL)
                if body_match:
                    acceptance_criteria = body_match.group(1).strip()
                
                # Extract description: everything between ## Description and the next heading
                description = ""
                desc_match = re.search(r'^## Description\n(.*?)(?=\n\n##|$)', content, re.DOTALL)
                if desc_match:
                    description = desc_match.group(1).strip()
                
                tickets.append(Ticket(
                    id=data.get('id', 'unknown'),
                    status=data.get('status', 'unknown'),
                    title=data.get('title', 'No Title'),
                    description=description,
                    acceptance_criteria=acceptance_criteria
                ))
    return tickets

def parse_handoff(handoff_path: Path) -> Dict[str, Any]:
    if not handoff_path.exists():
        return {"active_tasks": []}
    
    content = handoff_path.read_text(encoding='utf-8')
    active_tasks = []
    
    # Extract Active Tasks section — handle both bold and plain formats
    tasks_match = re.search(r'## Active Tasks\n(.*?)(?=\n\n##|$)', content, re.DOTALL)
    if tasks_match:
        tasks_section = tasks_match.group(1).strip()
        for line in tasks_section.split('\n'):
            line = line.strip()
            # Strip markdown bold markers (**text** or *text*)
            line = re.sub(r'\*\*(.*?)\*\*', r'\1', line)
            line = re.sub(r'\*(.*?)\*', r'\1', line)
            if line and line.startswith('- '):
                active_tasks.append(line[2:].strip())
                
    return {
        "active_tasks": active_tasks,
        "context": "Extracted from HANDOFF.md"
    }


def get_sprint_board(project_root: Path) -> List[Dict[str, Any]]:
    """Combine ticket parsing and handoff parsing into a single structured response."""
    tickets = parse_tickets(project_root / ".tickets")
    handoff = parse_handoff(project_root / "HANDOFF.md")
    
    return {
        "tickets": tickets,
        "handoff": handoff,
        "project_root": str(project_root)
    }
