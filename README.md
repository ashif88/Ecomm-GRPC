# Ecomm-GRPC

A Python-based e-commerce microservices backend built completely on **gRPC** (Google Remote Procedure Calls). Instead of a traditional REST API, all service-to-service communication uses gRPC's binary protocol buffers for fast, type-safe, and scalable communication.

## 🚀 Features

- **Microservices Architecture**: 4 independent services running on distinct ports.
- **gRPC & Protocol Buffers**: Strongly typed API contracts using `.proto` files.
- **JWT Authentication**: Custom gRPC interceptors to secure protected routes.
- **SQLAlchemy ORM**: Database interactions (configured for SQLite by default, easy to swap to MySQL/PostgreSQL).
- **Redis Caching**: Caches product catalogs to reduce database load.
- **Kafka Event Streaming**: Asynchronous event publishing for order creation and email notifications.
- **Dockerized Deployment**: Full `docker-compose.yml` with Redis, Kafka, and the app — one command to run everything.
- **Pagination support**: Optimized data retrieval.
- **Comprehensive Testing**: Includes integration and unit tests using `pytest` and `pytest-mock`.

---

## 🏗️ Architecture

The system consists of a single orchestrator (`run.py`) that launches 4 distinct gRPC services in parallel on the same machine (for development). In a production environment, these would be deployed as separate containers.

1. **UserService (Port 50051)**: Handles User Registration and Login (JWT token generation).
2. **ProductService (Port 50052)**: Manages product catalog with Redis caching and pagination.
3. **OrderService (Port 50053)**: Creates orders and validates them against UserService and ProductService.
4. **NotificationService (Port 50054)**: Listens for Kafka events to send emails.

---

## 🐳 Quick Start with Docker (Recommended)

The fastest way to get the full stack running — **no manual Redis or Kafka setup needed**.

### Prerequisites
- **Docker** & **Docker Compose** (v2+)

### 1. Clone the repository
```bash
git clone https://github.com/ashif88/Ecomm-GRPC.git
cd Ecomm-GRPC
```

### 2. Start everything
```bash
docker compose up --build
```

This builds the app image and spins up **Redis**, **Kafka** (with Zookeeper), and the **gRPC app** — with health checks ensuring the app waits for infrastructure to be ready.

You should see:
```text
Initializing database tables...
Database tables initialized successfully.
Starting gRPC services...
All services are running. Press Ctrl+C to stop.
```

### Useful commands
```bash
# Run in detached (background) mode
docker compose up --build -d

# View live logs
docker compose logs -f app

# Stop and remove all containers
docker compose down

# Stop and remove containers, volumes, and images
docker compose down -v --rmi local
```

---

## 🛠️ Local Development Setup (Without Docker)

If you prefer running directly on your machine.

### Prerequisites
- **Python 3.9+**
- **Redis Server** (running locally on default port 6379, or configured via env vars)
- **Apache Kafka** (optional — the app degrades gracefully if Kafka is offline)

### 1. Clone the repository
```bash
git clone https://github.com/ashif88/Ecomm-GRPC.git
cd Ecomm-GRPC
```

### 2. Create a Virtual Environment
```bash
# On Windows
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# On macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Variables Setup
Create a `.env` file in the root directory:
```bash
DATABASE_URL=sqlite:///ecomm.db
SECRET_KEY=default_secret_key
JWT_ACCESS_TOKEN_EXPIRES=3600
REDIS_HOST=localhost
REDIS_PORT=6379
KAFKA_BROKER_URL=
```

### 5. Run the Services
```bash
python run.py
```

To gracefully shut down, press `Ctrl+C`. The script gives ongoing requests 5 seconds to finish before terminating.

---

## ⚙️ Environment Variables

| Variable | Description | Default |
|---|---|---|
| `DATABASE_URL` | SQLAlchemy database connection string | `sqlite:///ecomm.db` |
| `SECRET_KEY` | Secret key for JWT token signing | `default_secret_key` |
| `JWT_ACCESS_TOKEN_EXPIRES` | JWT token expiry in seconds | `3600` |
| `REDIS_HOST` | Redis server hostname | `localhost` |
| `REDIS_PORT` | Redis server port | `6379` |
| `KAFKA_BROKER_URL` | Kafka bootstrap server address (leave empty to disable) | _(empty)_ |

---

## 🧪 Running the Tests

The project includes a robust suite of isolated unit tests and full integration tests.

To run the unit test suite:
```bash
python -m pytest tests/ -v
```

To run the full end-to-end integration test (requires the servers to be running in another terminal):
```bash
python tests/integration_test.py
```

---

## 📜 Regenerating gRPC Code (For Developers)

If you modify the `app/protos/service.proto` file to add new endpoints or change request structures, you must regenerate the Python bindings. 

From the root directory, run:
```bash
python -m grpc_tools.protoc -Iapp/protos --python_out=. --grpc_python_out=. app/protos/service.proto
```
_This will update `service_pb2.py` and `service_pb2_grpc.py`._

---

## 📁 Project Structure

```
Ecomm-GRPC/
├── app/
│   ├── models/          # SQLAlchemy ORM models
│   ├── protos/          # Protocol Buffer definitions
│   ├── services/        # gRPC service implementations
│   └── utils/           # Shared utilities (DB, Redis, Kafka, JWT, Auth)
├── tests/               # Unit and integration tests
├── service_pb2.py       # Generated protobuf code
├── service_pb2_grpc.py  # Generated gRPC stubs
├── run.py               # Application entry point
├── requirements.txt     # Python dependencies
├── Dockerfile           # Multi-stage Docker build
├── docker-compose.yml   # Full-stack orchestration
├── .dockerignore        # Docker build context exclusions
└── .env                 # Environment variables (not committed)
```
