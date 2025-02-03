import grpc
import service_pb2
import service_pb2_grpc
from concurrent import futures
from app.models.order import db, Order
from app.models.product import Product
from app.utils.kafka_producer import send_message

class OrderService(service_pb2_grpc.OrderServiceServicer):
    def CreateOrder(self, request, context):
        product_id = request.product_id
        user_id = request.user_id
        quantity = request.quantity

        product = Product.query.get(product_id)
        if not product:
            return service_pb2.OrderResponse(success=False, message="Product not found")

        new_order = Order(product_id=product.id, user_id=user_id, quantity=quantity)
        db.session.add(new_order)
        db.session.commit()

        # Publish event to Kafka
        send_message('order_topic', f"New order placed: User {user_id}, Product {product_id}, Quantity {quantity}")

        return service_pb2.OrderResponse(success=True, message="Order created successfully")

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    service_pb2_grpc.add_OrderServiceServicer_to_server(OrderService(), server)
    server.add_insecure_port('[::]:50053')
    server.start()
    server.wait_for_termination()
