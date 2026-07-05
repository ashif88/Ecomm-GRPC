import grpc
import service_pb2
import service_pb2_grpc
from concurrent import futures
from app.models.order import db, Order
from app.models.product import Product
from app.utils.kafka_producer import send_message
from app.utils.auth_interceptor import AuthInterceptor

class OrderService(service_pb2_grpc.OrderServiceServicer):
    def CreateOrder(self, request, context):
        product_id = request.product_id
        user_id = request.user_id
        quantity = request.quantity

        if quantity <= 0:
            return service_pb2.OrderResponse(success=False, message="Quantity must be greater than 0")

        try:
            # Validate product exists
            product = Product.query.get(product_id)
            if not product:
                return service_pb2.OrderResponse(success=False, message="Product not found")

            # Validate user exists (required by foreign key)
            from app.models.user import User
            user = User.query.get(user_id)
            if not user:
                return service_pb2.OrderResponse(success=False, message="User not found")

            new_order = Order(product_id=product.id, user_id=user_id, quantity=quantity)
            db.session.add(new_order)
            db.session.commit()

            # Publish event to Kafka
            send_message('order_topic', f"New order placed: User {user_id}, Product {product_id}, Quantity {quantity}")

            return service_pb2.OrderResponse(success=True, message="Order created successfully")
        except Exception as e:
            db.session.rollback()
            return service_pb2.OrderResponse(success=False, message=f"Database error: {str(e)}")
        finally:
            db.session.remove()

def create_server():
    auth_interceptor = AuthInterceptor(protected_methods=['/app.OrderService/CreateOrder'])
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10),
        interceptors=(auth_interceptor,)
    )
    service_pb2_grpc.add_OrderServiceServicer_to_server(OrderService(), server)
    server.add_insecure_port('[::]:50053')
    return server
