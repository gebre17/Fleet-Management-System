# Contributing

## Getting started

1. Fork and clone the repo.
2. Copy the env files and start the stack:
   ```bash
   cp backend/.env.example backend/.env
   cp frontend/.env.example frontend/.env.local
   docker-compose up -d --build
   ```
3. See [QUICKSTART.md](QUICKSTART.md) for local (non-Docker) backend/frontend setup.

## Making changes

- Create a branch off `main` for your change.
- Keep commits small and focused — one logical change per commit, with tests
  for behavior changes landing in the same commit as the code they verify.
- Run the checks locally before opening a PR:

  **Backend** (from `backend/`):
  ```bash
  pytest --cov=app --cov-report=term-missing
  ruff check app
  black --check app
  ```

  **Frontend** (from `frontend/`):
  ```bash
  npm run type-check
  npm run lint
  npm test
  npm run build
  ```

- CI (`.github/workflows/ci.yml`) runs the same checks on every push and PR.

## Pull requests

- Describe what changed and why, not just what.
- Link any related issue.
- Make sure CI is green before requesting review.

## Reporting issues

Open a GitHub issue with steps to reproduce, expected vs. actual behavior,
and relevant logs (`docker-compose logs <service>`).
