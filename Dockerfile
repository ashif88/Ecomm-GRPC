# ---- Build Stage ----
FROM python:3.11-slim AS builder

WORKDIR /app

# Install build dependencies for grpcio
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ---- Runtime Stage ----
FROM python:3.11-slim

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy application source code
COPY . .

# Expose all gRPC service ports
EXPOSE 50051 50052 50053 50054

# Run the orchestrator
CMD ["python", "run.py"]
