import grpc
import service_pb2
import service_pb2_grpc
from concurrent import futures
from app.models.product import db, Product
from app.utils.redis_cache import get_cached_data, set_cached_data

class ProductService(service_pb2_grpc.ProductServiceServicer):
    def AddProduct(self, request, context):
        name = request.name
        price = request.price

        new_product = Product(name=name, price=price)
        db.session.add(new_product)
        db.session.commit()

        return service_pb2.ProductResponse(success=True, message="Product added successfully")

    def GetProducts(self, request, context):
        cached_products = get_cached_data('products')
        if cached_products:
            return service_pb2.ProductListResponse(products=cached_products.split(','))

        products = Product.query.all()
        product_names = [product.name for product in products]
        set_cached_data('products', ','.join(product_names))

        return service_pb2.ProductListResponse(products=product_names)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    service_pb2_grpc.add_ProductServiceServicer_to_server(ProductService(), server)
    server.add_insecure_port('[::]:50052')
    server.start()
    server.wait_for_termination()
