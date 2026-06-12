import grpc
import service_pb2
import service_pb2_grpc
from concurrent import futures
from app.models.product import db, Product
from app.utils.redis_cache import get_cached_data, set_cached_data, delete_cached_data
import json

class ProductService(service_pb2_grpc.ProductServiceServicer):
    def AddProduct(self, request, context):
        name = request.name
        price = request.price

        try:
            new_product = Product(name=name, price=price)
            db.session.add(new_product)
            db.session.commit()
            
            # Invalidate Redis cache
            delete_cached_data('products')
            
            return service_pb2.ProductResponse(success=True, message="Product added successfully")
        except Exception as e:
            db.session.rollback()
            return service_pb2.ProductResponse(success=False, message=f"Database error: {str(e)}")

    def GetProducts(self, request, context):
        # 1. Try cache
        cached_products = get_cached_data('products')
        if cached_products:
            try:
                product_list = json.loads(cached_products)
                product_infos = [
                    service_pb2.ProductInfo(id=p['id'], name=p['name'], price=p['price'])
                    for p in product_list
                ]
                return service_pb2.ProductListResponse(products=product_infos)
            except Exception:
                pass # Fall back to DB

        # 2. Try DB
        try:
            products = Product.query.all()
            product_infos = [
                service_pb2.ProductInfo(id=product.id, name=product.name, price=product.price)
                for product in products
            ]
            
            # Cache the products list as JSON
            try:
                cache_list = [{'id': p.id, 'name': p.name, 'price': p.price} for p in products]
                set_cached_data('products', json.dumps(cache_list))
            except Exception:
                pass

            return service_pb2.ProductListResponse(products=product_infos)
        except Exception as e:
            return service_pb2.ProductListResponse(products=[])

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    service_pb2_grpc.add_ProductServiceServicer_to_server(ProductService(), server)
    server.add_insecure_port('[::]:50052')
    server.start()
    server.wait_for_termination()
