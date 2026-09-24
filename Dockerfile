FROM python:3.12-slim

WORKDIR /app

RUN pip install uv --quiet

COPY pyproject.toml uv.lock ./
RUN uv sync --no-dev --frozen

COPY . .

EXPOSE 8000 8501

CMD ["sh", "-c", "uv run alembic upgrade head && uv run streamlit run app/main.py --server.port 8501 --server.address 0.0.0.0 & uv run uvicorn src.api.main:app --host 0.0.0.0 --port 8000"]
