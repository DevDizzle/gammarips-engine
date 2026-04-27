# x-poster — ADK multi-agent X publisher for @gammarips
FROM python:3.11-slim

RUN pip install --no-cache-dir uv==0.8.13

WORKDIR /code

COPY ./pyproject.toml ./README.md ./uv.lock* ./

COPY ./app ./app

# Bundled assets (logo, Space Grotesk Bold TTF for ticker overlay).
COPY ./assets ./assets

# Resolve + install Python deps (no --frozen; lockfile regenerated at build)
RUN uv sync

# GammaRips shared content lib — staged into build context by deploy.sh
COPY ./_gammarips_content_vendor/ /opt/gammarips_content/
RUN uv pip install --no-deps /opt/gammarips_content

ARG COMMIT_SHA=""
ENV COMMIT_SHA=${COMMIT_SHA}

ARG AGENT_VERSION=0.0.0
ENV AGENT_VERSION=${AGENT_VERSION}

EXPOSE 8080

CMD ["uv", "run", "uvicorn", "app.fast_api_app:app", "--host", "0.0.0.0", "--port", "8080"]
