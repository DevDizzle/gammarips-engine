FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# GammaRips shared trace logger — staged by deploy.sh into ./_trace_logger_vendor
COPY _trace_logger_vendor/ /opt/trace_logger/
RUN pip install --no-cache-dir /opt/trace_logger

COPY . .

EXPOSE 8080

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--timeout-keep-alive", "300"]
