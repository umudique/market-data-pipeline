# Migrations

Alembic manages schema migrations.

```bash
# Init (first time only)
uv run alembic init migrations

# Create a new migration
uv run alembic revision --autogenerate -m "description"

# Apply
uv run alembic upgrade head

# Rollback one step
uv run alembic downgrade -1
```

Tables: `ingestion_batches`, `raw_market_data`, `validation_issues`, `market_bars`
