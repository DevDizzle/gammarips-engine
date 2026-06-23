FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# The dbt project is vendored into ./dbt by deploy.sh before the build.
COPY . .

# Pre-install dbt packages (dbt_utils) into the image so cold starts don't fetch.
RUN cd dbt && dbt deps --profiles-dir . || true

ENV PORT=8080
# Long timeout: a full dbt build of the layer can take a few minutes.
CMD exec gunicorn --bind :$PORT --workers 1 --threads 2 --timeout 1800 main:app
