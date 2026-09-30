# Contributing

Thanks for contributing. Please open an issue before substantial architectural changes, keep changes focused, and never commit documents, vector data, or `.env` files.

Run these checks before opening a pull request:

```bash
cd backend && uv sync --extra dev && uv run ruff check . && uv run pytest && uv run mypy app
cd ../frontend && npm ci && npm run build
```

Tests must mock Ollama, browser-use, and external websites. Contributions should preserve the local-first privacy model and document any network behavior.
