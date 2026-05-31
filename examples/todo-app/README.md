# Todo App Canon Walkthrough

This example is a small vanilla JavaScript Todo app used to show canon's workflow on a real project shape. The app scope is intentionally narrow: add a Todo, mark it complete, and verify the behavior with tests.

```text
examples/todo-app/
  docs/          walkthrough docs
  src/           browser app source
  tests/         Node test coverage for Todo behavior
  .tickets/     local sprint state created during the walkthrough
```

The app has no runtime dependencies. Tests use Node's built-in test runner.

## Run It

```bash
npm test
python3 -m http.server 4173 -d src
```

Open `http://127.0.0.1:4173`.

## Walk The Canon Flow

1. Read [docs/01-setup.md](docs/01-setup.md).
2. Start the sprint in [docs/02-sprint-start.md](docs/02-sprint-start.md).
3. Open the board with [docs/04-sprint-check.md](docs/04-sprint-check.md).
4. Build and test with [docs/03-implementation.md](docs/03-implementation.md).
5. Complete the sprint with [docs/05-sprint-complete.md](docs/05-sprint-complete.md).

The local `.tickets/` folder lets the walkthrough run from here without mixing
ticket state into the canon repo root. It starts empty; `sprint start` creates
the first ticket.
