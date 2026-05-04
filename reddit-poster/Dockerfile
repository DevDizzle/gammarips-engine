# reddit-poster — minimal Reddit auto-poster (trade ideas + pnl receipts)
FROM python:3.12-slim

RUN pip install --no-cache-dir uv==0.8.13

WORKDIR /code

COPY ./pyproject.toml ./uv.lock* ./
COPY ./app ./app

RUN uv sync

# GammaRips shared content lib — staged into build context by deploy.sh
COPY ./_gammarips_content_vendor/ /opt/gammarips_content/
RUN uv pip install --no-deps /opt/gammarips_content

ARG COMMIT_SHA=""
ENV COMMIT_SHA=${COMMIT_SHA}

EXPOSE 8080

CMD ["uv", "run", "uvicorn", "app.fast_api_app:app", "--host", "0.0.0.0", "--port", "8080"]
