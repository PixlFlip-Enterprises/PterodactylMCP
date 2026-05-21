FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY pyproject.toml README.md LICENSE ./
COPY pterodactyl_mcp ./pterodactyl_mcp

RUN pip install --upgrade pip && pip install .

ENTRYPOINT ["pterodactyl-mcp"]
CMD ["--transport", "stdio"]
