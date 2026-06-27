"""Parse sprint board data from markdown files."""

import os
import re
import sys
from typing import Dict, List

from utils.models import Ticket


def _section(content: str) -> List[Dict[str, str]]:
    """Parse markdown sections by tracking heading levels.

    Returns list of dicts with 'heading', 'content', 'level'.
    Handles nested sections (e.g., ### Approach under ## Plan).
    """
    sections: List[Dict[str, str]] = []
    lines = content.split('\n')
    current_heading: str | None = None
    current_level: int = 0
    current_content: List[str] = []

    for line in lines:
        match = re.match(r'^(#{1,6})\s+(.*)', line)
        if match:
            if current_heading is not None:
                sections.append({
                    'heading': current_heading,
                    'content': '\n'.join(current_content),
                    'level': current_level,
                })
            current_heading = match.group(2).strip()
            current_level = len(match.group(1))
            current_content = []
        else:
            current_content.append(line)

    if current_heading is not None:
        sections.append({
            'heading': current_heading,
            'content': '\n'.join(current_content),
            'level': current_level,
        })

    return sections


def parse_handoff(project_root: str) -> Dict[str, object]:
    """Read HANDOFF.md and extract Current Focus section.

    Returns dict with 'current_focus' (str) and 'active_tasks' (List[str]).
    Handles missing file gracefully (returns empty dict).
    """
    handoff_path = os.path.join(project_root, 'HANDOFF.md')
    if not os.path.isfile(handoff_path):
        return {'current_focus': '', 'active_tasks': []}

    with open(handoff_path, 'r', encoding='utf-8') as f:
        content = f.read()

    sections = _section(content)
    focus_section = None
    active_tasks: List[str] = []

    for section in sections:
        if section['heading'] == 'Current Focus':
            focus_section = section
        elif section['heading'] == 'Active Tasks':
            for line in section['content'].split('\n'):
                line = line.strip()
                if line.startswith('- '):
                    active_tasks.append(line[2:].strip())

    return {
        'current_focus': focus_section['content'].strip() if focus_section else '',
        'active_tasks': active_tasks,
    }


def parse_tickets(project_root: str) -> List[Ticket]:
    """Walk .tickets/ directory and parse each ticket markdown file.

    - Resolves paths and verifies they are within .tickets/ (path traversal protection)
    - Parses sections using _section()
    - Extracts fields: id, title, status, assignee, priority, layout
    - Counts unchecked acceptance criteria items
    - Extracts plan approach section
    - Scans for related .md files in the ticket folder → adds to docs list
    - Wraps individual ticket parsing in try/except — skips malformed tickets
    """
    tickets_dir = os.path.join(project_root, '.tickets')
    if not os.path.isdir(tickets_dir):
        return []

    tickets: List[Ticket] = []

    for filename in sorted(os.listdir(tickets_dir)):
        if not filename.endswith('.md'):
            continue

        filepath = os.path.join(tickets_dir, filename)
        ticket_id = filename[:-3]  # strip .md

        # Path traversal protection
        abs_filepath = os.path.abspath(filepath)
        abs_tickets_dir = os.path.abspath(tickets_dir)
        if not abs_filepath.startswith(abs_tickets_dir + os.sep) and abs_filepath != abs_tickets_dir:
            print(f"Warning: skipping path traversal attempt: {filepath}", file=sys.stderr)
            continue

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            sections = _section(content)

            # Extract fields from sections
            ticket_data: Dict[str, str] = {}
            for section in sections:
                heading = section['heading']
                if heading == 'Title':
                    ticket_data['title'] = section['content'].strip()
                elif heading == 'Status':
                    ticket_data['status'] = section['content'].strip()
                elif heading == 'Assignee':
                    ticket_data['assignee'] = section['content'].strip()
                elif heading == 'Priority':
                    ticket_data['priority'] = section['content'].strip()
                elif heading == 'Layout':
                    ticket_data['layout'] = section['content'].strip()

            # Count unchecked acceptance criteria
            acceptance_unchecked = 0
            for section in sections:
                if section['heading'] == 'Acceptance Criteria':
                    for line in section['content'].split('\n'):
                        line = line.strip()
                        if line.startswith('- [ ]'):
                            acceptance_unchecked += 1

            # Extract plan approach section
            plan_has_approach = False
            for section in sections:
                if section['heading'] == 'Plan':
                    for sub_section in _section(section['content']):
                        if sub_section['heading'] == 'Approach':
                            plan_has_approach = True
                            break

            # Scan for related .md files in the ticket folder
            ticket_folder = os.path.dirname(filepath)
            docs: List[str] = []
            for entry in os.listdir(ticket_folder):
                if entry.endswith('.md') and entry != filename:
                    docs.append(entry)

            ticket = Ticket(
                id=ticket_id,
                title=ticket_data.get('title', ''),
                status=ticket_data.get('status', ''),
                assignee=ticket_data.get('assignee', ''),
                priority=ticket_data.get('priority', ''),
                layout=ticket_data.get('layout', ''),
                acceptance_has_items=acceptance_unchecked > 0,
                acceptance_unchecked=acceptance_unchecked,
                plan_has_approach=plan_has_approach,
                docs=docs,
            )
            tickets.append(ticket)

        except Exception as e:
            print(f"Warning: skipping malformed ticket {ticket_id}: {e}", file=sys.stderr)

    return tickets


def get_sprint_board(project_root: str) -> Dict[str, object]:
    """Combine handoff and tickets into a sprint board view.

    Returns dict with 'handoff' and 'tickets' keys.
    """
    handoff = parse_handoff(project_root)
    tickets = parse_tickets(project_root)
    return {'handoff': handoff, 'tickets': tickets}
