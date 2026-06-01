# Todo App Reference

This example is the finished minimal Todo app used as the reference
implementation for the canon walkthrough. The app scope is intentionally narrow:
add a Todo, mark it complete, and verify the behavior with tests.

```text
examples/todo-app/
  src/           browser app source
  tests/         Node test coverage for Todo behavior
```

The app has no runtime dependencies. Tests use Node's built-in test runner.

## Run It

```bash
npm test
python3 -m http.server 4173 -d src
```

Open `http://127.0.0.1:4173`.

## Walk The Canon Flow

Use [`../canon-todo-walkthrough`](../canon-todo-walkthrough) to build this app
from scratch with `sprint`, `sprint-check`, and sprint docs.
