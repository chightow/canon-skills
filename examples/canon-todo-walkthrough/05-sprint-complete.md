# 05 - Sprint Complete

## Step 1 - Confirm Acceptance

Before closing, `.tickets/<id>/acceptance.md` should have every criterion and
test item checked.

## Step 2 - Complete the Sprint

Tell the agent this in chat:

```text
Sprint complete
```

The agent should:

- Run the wrapup pipeline where applicable.
- Verify each item in `.tickets/<id>/acceptance.md`.
- Confirm the test command passed.
- Update `DECISIONS.md` only for durable non-obvious decisions.
- Update `HANDOFF.md` with follow-up work.
- Run `sprint complete` to close the active ticket.

For this example, the close command should only succeed after the acceptance and
test checkboxes are marked complete.

## Step 3 - Verify Done

Reload `sprint-check`. The Todo ticket should now appear in Done, with the same
Acceptance, Blueprint, and Plan tabs still available in the detail view.
