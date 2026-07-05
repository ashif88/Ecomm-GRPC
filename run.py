import sys
import time

from dotenv import load_dotenv

# Load env vars before anything else
load_dotenv()

from app.services.notification_service import (
    create_server as create_notification_server,
)
from app.services.order_service import create_server as create_order_server
from app.services.product_service import create_server as create_product_server
from app.services.user_service import create_server as create_user_server

if __name__ == "__main__":
    from app.models.order import Order
    from app.models.product import Product
    from app.models.user import User
    from app.utils.db import db

    print("Initializing database tables...")
    db.Model.metadata.create_all(bind=db.engine)
    print("Database tables initialized successfully.")

    servers = [
        create_user_server(),
        create_product_server(),
        create_order_server(),
        create_notification_server(),
    ]

    print("Starting gRPC services...")
    for server in servers:
        server.start()

    print("All services are running. Press Ctrl+C to stop.")

    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        print("\nStopping services gracefully...")
        for server in servers:
            server.stop(5)
        print("Services stopped.")
        sys.exit(0)
