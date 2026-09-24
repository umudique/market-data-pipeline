# Contributing to Financial Market Data Pipeline

## Commit Style

Use conventional commits:

| Prefix | When to use |
|---|---|
| `feat:` | new capability within the pipeline or screener scope |
| `fix:` | bug correction |
| `test:` | adding or correcting tests |
| `refactor:` | structural change with no behavior change |
| `docs:` | documentation only |
| `chore:` | tooling, dependencies, CI |

For changes that touch a specific module, scope it: `feat(ingestion):`, `fix(validation):`, etc.

For significant changes, reference the relevant ADR or architecture section in the commit body.

## Before Contributing

- Read `financial_market_data_pipeline_c4_architecture.md` — scope boundaries are strict.
- The product is a **market-data reliability pipeline**. Changes that introduce Kafka, distributed
  event streaming, live exchange connectivity, order execution, or silent data interpolation
  are out of scope.

## Development Setup

```bash
# Install dependencies
uv sync --extra dev

# Install pre-commit hook
git config core.hooksPath .githooks

# Copy and fill environment
cp .env.example .env
```

## Quality Gates

All of the following must pass before a commit lands:

| Check | Command |
|---|---|
| Format | `uv run ruff format --check .` |
| Lint | `uv run ruff check .` |
| Type check | `uv run mypy src` |
| Unit tests | `uv run pytest -m "not integration"` |
| All tests | `uv run pytest` |

The pre-commit hook runs format, lint, mypy, and unit tests automatically.
Integration tests (require PostgreSQL) run in CI thorough and on demand locally.

## Testing Requirements

| Change type | Required tests |
|---|---|
| New validation rule | Test for valid input (no issue) and invalid input (correct IssueType) |
| New normalization step | Deterministic fixture with known expected canonical output |
| New screener calculation | Unit test with known inputs and analytically computed expected value |
| New storage operation | Test for idempotency — repeated write must not duplicate records |
| New API endpoint | Test for valid request (200), invalid request (422), and error mapping |

## Data-Quality Boundary

The pipeline exists to expose data-quality defects, not conceal them.

- Missing intervals are flagged as `MISSING_INTERVAL` — never interpolated.
- Invalid prices are rejected — never coerced into valid values.
- Every defect produces a `ValidationIssue` record.
- The screener reads normalized trusted bars only — never raw or staging data.
- Idempotency is enforced at both application level and database level.

Changes that shift this toward silent repair or silent normalization are out of scope.
