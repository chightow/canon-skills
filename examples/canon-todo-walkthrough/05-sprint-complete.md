# 05 - Sprint Complete

**What this step does:** The CLI verifies acceptance is complete before closing
the ticket. It is a hard gate — the close command will print what is missing and
refuse to proceed until the doc is fixed.

## Step 1 - Confirm Acceptance

Before closing, `.tickets/<id>/acceptance.md` must have:
- At least one checked item under `## Criteria`
- At least one checked item under `## Test Plan`

Open the ticket on the board and check every item as it passes tests.

## Step 2 - See the gate in action (try it early)

You can run the close command with unchecked or missing items to see the guard.

**If Test Plan is missing or empty:**

```
$ sprint complete
Sprint t-xxxx cannot close: acceptance.md ## Test Plan has no checklist items.
Add test commands to acceptance.md, then re-run.
```

Fix: open `acceptance.md` and add at least one test command under `## Test Plan`,
then check it.

**If items are still unchecked:**

```
$ sprint complete
Sprint t-xxxx is not complete. Unchecked acceptance/test items remain:
- [ ] npm test
```

Fix: run `npm test`, confirm it passes, then have the agent check that item.

The board's readiness indicator also reflects this: a card that shows
`acceptance incomplete` has the same problem the close gate will catch — it's an
early warning you can act on before running `sprint complete`.

## Step 3 - Complete the Sprint

Tell the agent in chat:

```text
Sprint complete
```

The agent should:

- Verify each item in `.tickets/<id>/acceptance.md`.
- Confirm the test command passed.
- Update `DECISIONS.md` only for durable non-obvious decisions.
- Update `HANDOFF.md` with follow-up work.
- Run `sprint complete` to close the active ticket.

Expected output when all items are checked:

```
Sprint completed: t-xxxx
```

## Step 4 - Verify Done

Reload `sprint-check`. The Todo ticket should now appear in Done, with the same
Acceptance, Blueprint, and Plan tabs still available in the detail view.
