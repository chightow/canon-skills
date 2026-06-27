# MCP Server Tasks

<!-- Keep this doc under ~500 words — it is injected at every session start. -->

## Sign-off
Tier: normal | Risk: low — fixes bugs and missing deps

- [x] Plan approved — proceed to implementation

## Approach
Tier: normal — fix the adversarial review findings from Phase 1.

1. Fix `models.py` duplicate `priority` field.
2. Fix `parsers.py` ticket parsing (robust description extraction, correct acceptance regex, fix handoff parsing).
3. Fix `server.py` platform detection for `open_dashboard`, add error handling, add `fastmcp` to `requirements.txt`.
4. Fix `project_context.py` edge case for `.tickets/` subdirectory traversal.

## Files
<!-- List files to create or modify. -->

- `mcp_server/utils/models.py`
- `mcp_server/utils/parsers.py`
- `mcp_server/server.py`
- `mcp_server/utils/project_context.py`
- `mcp_server/requirements.txt`

## Test Plan
<!-- Add or edit test commands below. Keep this heading unchanged. -->

- [ ] Verify `models.py` loads without duplicate field errors.
- [ ] Verify `get_sprint_board` returns correct data for `mcp-migration-001` ticket.
- [ ] Verify `get_sprint_board` handles `t-7f1d` ticket (no `ticket.md`, only `plan.md`).
- [ ] Verify `parse_handoff` extracts ticket IDs from bold format in `HANDOFF.md`.
- [ ] Verify `open_dashboard` works on Windows (uses `cmd`/`powershell` instead of `bash`).
- [ ] Verify `find_project_root` returns correct path when called from `.tickets/` subdirectory.
- [ ] Verify `requirements.txt` includes `fastmcp`.

## QA
<!-- Add sign-off items below. Keep this heading unchanged. -->

- [ ] Tested locally
