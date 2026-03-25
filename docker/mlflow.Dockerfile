# Optimized minimal image for MLflow only
FROM python:3.12-slim-bookworm

WORKDIR /app

# Install only mlflow and essential dependencies
RUN pip install --no-cache-dir mlflow[extras]

# Expose MLflow port
EXPOSE 5000

# Run MLflow UI with minimal workers and no background jobs if possible
# We use --workers 1 to limit process count
CMD ["mlflow", "ui", "--host", "0.0.0.0", "--port", "5000", "--workers", "1"]
