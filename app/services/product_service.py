import grpc
import service_pb2
import service_pb2_grpc
from concurrent import futures
from app.models.product import db, Product
from app.utils.redis_cache import get_cached_data, set_cached_data, delete_cached_data
import json
from app.utils.auth_interceptor import AuthInterceptor

class ProductService(service_pb2_grpc.ProductServiceServicer):
    def AddProduct(self, request, context):
        name = request.name.strip()
        price = request.price

        if not name or price <= 0:
            return service_pb2.ProductResponse(success=False, message="Invalid product name or price")

        try:
            new_product = Product(name=name, price=price)
            db.session.add(new_product)
            db.session.commit()
            
            # Invalidate Redis cache
            # For simplicity, we just delete all pages or a general key.
            # In a real app, you'd track cache keys or use a pattern.
            delete_cached_data('products_all')
            
            return service_pb2.ProductResponse(success=True, message="Product added successfully")
        except Exception as e:
            db.session.rollback()
            return service_pb2.ProductResponse(success=False, message=f"Database error: {str(e)}")
        finally:
            db.session.remove()

    def GetProducts(self, request, context):
        limit = request.limit if request.limit > 0 else 10
        offset = request.offset if request.offset >= 0 else 0
        cache_key = f'products_{limit}_{offset}'

        # 1. Try cache
        cached_products = get_cached_data(cache_key)
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
            products = Product.query.limit(limit).offset(offset).all()
            product_infos = [
                service_pb2.ProductInfo(id=product.id, name=product.name, price=product.price)
                for product in products
            ]
            
            # Cache the products list as JSON
            try:
                cache_list = [{'id': p.id, 'name': p.name, 'price': p.price} for p in products]
                set_cached_data(cache_key, json.dumps(cache_list))
            except Exception:
                pass

            return service_pb2.ProductListResponse(products=product_infos)
        except Exception as e:
            return service_pb2.ProductListResponse(products=[])
        finally:
            db.session.remove()

def create_server():
    auth_interceptor = AuthInterceptor(protected_methods=['/app.ProductService/AddProduct'])
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10),
        interceptors=(auth_interceptor,)
    )
    service_pb2_grpc.add_ProductServiceServicer_to_server(ProductService(), server)
    server.add_insecure_port('[::]:50052')
    return server
