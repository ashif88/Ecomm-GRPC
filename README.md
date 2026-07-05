# Ecomm-GRPC

A Python-based e-commerce microservices backend built completely on **gRPC** (Google Remote Procedure Calls). Instead of a traditional REST API, all service-to-service communication uses gRPC's binary protocol buffers for fast, type-safe, and scalable communication.

## 🚀 Features

- **Microservices Architecture**: 4 independent services running on distinct ports.
- **gRPC & Protocol Buffers**: Strongly typed API contracts using `.proto` files.
- **JWT Authentication**: Custom gRPC interceptors to secure protected routes.
- **SQLAlchemy ORM**: Database interactions (configured for SQLite by default, easy to swap to MySQL/PostgreSQL).
- **Redis Caching**: Caches product catalogs to reduce database load.
- **Kafka Event Streaming**: Asynchronous event publishing for order creation and email notifications.
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

## 🛠️ Setup & Installation

### Prerequisites
- **Python 3.9+**
- **Redis Server** (Running locally on default port 6379, or updated in `.env`)
- **Apache Kafka** (Optional: defaults to gracefully degrade if offline)

### 1. Clone the repository
```bash
git clone https://github.com/ashif88/Ecomm-GRPC.git
cd Ecomm-GRPC
```

### 2. Create a Virtual Environment
It is highly recommended to use an isolated Python virtual environment.
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
Create a `.env` file in the root directory and add the following configuration:
```bash
DATABASE_URL=sqlite:///ecomm.db
SECRET_KEY=default_secret_key
JWT_ACCESS_TOKEN_EXPIRES=3600
KAFKA_BROKER_URL=
```
_You can customize the database URLs, JWT Secrets, or Kafka/Redis host ports here._

---

## 🚀 Running the Services

To start the database, initialize the tables, and boot all 4 gRPC servers simultaneously, simply run the entry point script:

```bash
python run.py
```

You should see:
```text
Initializing database tables...
Database tables initialized successfully.
Starting gRPC services...
All services are running. Press Ctrl+C to stop.
```

To gracefully shut down the servers, simply press `Ctrl+C`. The script will trap the signal and give ongoing requests 5 seconds to finish before terminating.

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
