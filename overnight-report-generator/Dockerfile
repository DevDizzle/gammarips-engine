FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# GammaRips shared trace logger — staged by deploy.sh into ./_trace_logger_vendor
COPY _trace_logger_vendor/ /opt/trace_logger/
RUN pip install --no-cache-dir /opt/trace_logger

COPY . .
ENV PORT=8080
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "1", "--timeout", "0", "main:app"]
