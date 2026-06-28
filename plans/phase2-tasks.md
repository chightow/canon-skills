# Phase 2: Write Tools — Discrete Tasks

Parent plan: [mcp_migration_plan.md](./mcp_migration_plan.md)

---

## Task 2.1: `create_sprint_ticket`

**Goal:** Create a new sprint ticket file in `.tickets/` with associated acceptance and test artifacts.

**Inputs:**
- `description` (string) — ticket description/title
- `priority` (string) — e.g. `P0`, `P1`, `P2`

**Actions:**
1. Generate a unique ticket ID (e.g. `TICKET-NNNN`).
2. Create `.tickets/<ticket_id>/ticket.md` with frontmatter (id, description, priority, status, created_at).
3. Create `.tickets/<ticket_id>/acceptance.md` with initial acceptance criteria template.
4. Create `.tickets/<ticket_id>/test_plan.md` with initial test plan template.

**Acceptance Criteria:**
- [x] Ticket file created with correct frontmatter.
- [x] `acceptance.md` and `test_plan.md` initialized.
- [x] Output is valid JSON to the MCP client.

---

## Task 2.2: `update_ticket_status`

**Goal:** Update the status field of an existing ticket's frontmatter.

**Inputs:**
- `ticket_id` (string) — e.g. `TICKET-0001`
- `new_status` (string) — e.g. `in_progress`, `done`, `blocked`

**Actions:**
1. Locate the ticket directory under `.tickets/<ticket_id>/`.
2. Parse the frontmatter of `ticket.md`.
3. Update the `status` field to `new_status`.
4. Persist the change back to `ticket.md`.

**Acceptance Criteria:**
- [x] Status field updated in-place.
- [x] File remains valid Markdown with frontmatter.
- [x] No other ticket data is affected.

---

## Task 2.3: `add_acceptance_criterion`

**Goal:** Append a new acceptance criterion to a ticket's `acceptance.md`.

**Inputs:**
- `ticket_id` (string) — e.g. `TICKET-0001`
- `criterion_text` (string) — the acceptance criterion to append

**Actions:**
1. Locate `.tickets/<ticket_id>/acceptance.md`.
2. Append the new criterion as a numbered list item (or bullet, matching existing format).
3. Persist the change.

**Acceptance Criteria:**
- [x] Criterion appended to `acceptance.md`.
- [x] Existing criteria are preserved and renumbered if needed.
- [x] No other ticket files are modified.
