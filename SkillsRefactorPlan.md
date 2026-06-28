# Plan: Complete `skills.sh` Refactoring

**Goal**: Eliminate all duplication, ensure a clean separation of concerns, and finalize the modular structure.

**Current State Analysis**:
- `skills.sh`: The main entry point. It currently contains many functions that are also present in the sub-scripts.
- `lib.sh`: Contains shared utilities, but some are duplicated in `agents.sh` or `commands.sh`.
- `agents.sh`: Contains `AGENTS.md` manipulation logic.
- `commands.sh`: Contains command implementations, but some logic (like `offer_tkt_path`) is duplicated in `commands.sh` and `skills.sh`.
- `project.sh`: Contains project registration and symlink logic.
- `display.sh`: Contains the `cmd_list` logic.

**Steps**

### Phase 1: Consolidation of Shared Utilities (`lib.sh`)
1.  [x]**Identify all unique utility functions** across all files.
    - [x] 1.1.1 `skill_row_name` (found in `skills.sh`, `lib.sh`)
    - [x] 1.1.2 `skill_row_path` (found in `skills.sh`, `lib.sh`)
    - [x] 1.1.3 `registered_skill_rows` (found in `skills.sh`, `lib.sh`)
    - [x] 1.1.4 `registered_skill_names` (found in `skills.sh`, `lib.sh`)
    - [x] 1.1.5 `covered_deps_for_skills` (found in `skills.sh`, `lib.sh`)
    - [x] 1.1.6 `is_canon_project_import_line` (found in `skills.sh`, `agents.sh`, `commands.sh`)
    - [x] 1.1.7 `strip_canon_project_imports` (found in `agents.sh`, `commands.sh`)
2.  [x] **Move all "pure" utility functions** (those that don't depend on command-specific state) into `lib.sh`.
    *   *Target functions to move to `lib.sh`*: `skill_row_name`, `skill_row_path`, `registered_skill_rows`, `registered_skill_names`, `covered_deps_for_skills`, `is_canon_project_import_line`, `strip_canon_project_imports`.
3.  **Remove duplicates** from `agents.sh`, `commands.sh`, `project.sh`, and `display.sh`.
4.  **Update `skills.sh`** to source `lib.sh` and remove its local copies of these utilities.

### Phase 2: Finalizing Module Responsibilities
1.  **`project.sh`**: Ensure it contains *only* `register_project`, `deregister_project`, `upsert_skills_symlinks`, and `remove_skills_symlinks`.
2.  **`agents.sh`**: Ensure it contains *only* `skills_table_upsert`.
3.  **`display.sh`**: Ensure it contains *only* `cmd_list`.
4.  **`commands.sh`**: Move all "helper" functions that are used by commands but aren't "pure utilities" here (e.g., `offer_tkt_path`, `ensure_sprint_project_marker`, `_post_register_prompts`, `_prune_redundant_deps`).
5.  **`skills.sh`**: Should act strictly as a dispatcher. It should source the sub-scripts and then call the appropriate `cmd_*` functions.

### Phase 3: Cleanup and Verification
1.  **Refactor `skills.sh` dispatch logic**: Simplify the `case` statement to call functions defined in the sourced sub-scripts.
2.  **Remove redundant `source` calls**: Ensure each script sources only what it needs.
3.  **Verification**:
    *   Run `skills.sh list` to ensure display works.
    *   Run `skills.sh add <skill>` to ensure registration works.
    *   Run `skills.sh status` to ensure status reporting works.
    *   Run `skills.sh remove <skill>` to ensure removal works.

**Relevant files**
- `tools/skills.sh` — The main entry point to be cleaned.
- `tools/skills/lib.sh` — The destination for shared utilities.
- `tools/skills/agents.sh` — For `AGENTS.md` logic.
- `tools/skills/commands.sh` — For command implementations.
- `tools/skills/project.sh` — For project/symlink logic.
- `tools/skills/display.sh` — For listing logic.

**Decisions**
- **Separation of Concerns**: `lib.sh` is for stateless utilities; `commands.sh` is for stateful command logic; `project.sh`/`agents.sh`/`display.sh` are domain-specific modules.
- **Dispatcher Pattern**: `skills.sh` will be a thin wrapper.
