from app.services.user_service import serve as user_service
from app.services.product_service import serve as product_service
from app.services.order_service import serve as order_service
from app.services.notification_service import serve as notification_service

if __name__ == '__main__':
    from concurrent.futures import ThreadPoolExecutor

    with ThreadPoolExecutor(max_workers=4) as executor:
        executor.submit(user_service)
        executor.submit(product_service)
        executor.submit(order_service)
        executor.submit(notification_service)
