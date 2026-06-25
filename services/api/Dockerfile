# World B backend container.
# Slim base keeps the image small; pinned Python version for reproducibility.
FROM python:3.12-slim

# Don't write .pyc files, and stream logs straight to the terminal.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies first (separate layer = faster rebuilds when only code changes).
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code.
COPY app ./app

# Document the port the service listens on.
EXPOSE 8080

# Start the API. Host 0.0.0.0 so it is reachable from outside the container.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
