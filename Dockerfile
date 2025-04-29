FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app

COPY . .

RUN uv sync

EXPOSE 8000

CMD ["uv", "run", "server.py"]
