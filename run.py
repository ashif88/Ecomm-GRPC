from app.services.user_service import serve as user_service
from app.services.product_service import serve as product_service
from app.services.order_service import serve as order_service
from app.services.notification_service import serve as notification_service

if __name__ == '__main__':
    from app.utils.db import db
    from app.models.user import User
    from app.models.product import Product
    from app.models.order import Order

    print("Initializing database tables...")
    db.Model.metadata.create_all(bind=db.engine)
    print("Database tables initialized successfully.")

    from concurrent.futures import ThreadPoolExecutor

    with ThreadPoolExecutor(max_workers=4) as executor:
        executor.submit(user_service)
        executor.submit(product_service)
        executor.submit(order_service)
        executor.submit(notification_service)
