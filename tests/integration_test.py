import grpc
import sys
from pathlib import Path
import random

import os
# Add root folder to python path dynamically
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import service_pb2
import service_pb2_grpc

def run_tests():
    print("Connecting to UserService...")
    user_channel = grpc.insecure_channel('localhost:50051')
    user_stub = service_pb2_grpc.UserServiceStub(user_channel)

    # 1. Register a new user
    print("\nTest 1: Register User")
    uid = random.randint(1000, 9999)
    email = f"user_{uid}@example.com"
    try:
        reg_response = user_stub.Register(service_pb2.UserRequest(
            username=f"user_{uid}",
            email=email,
            password="securepassword"
        ))
        print(f"Register response: success={reg_response.success}, message={reg_response.message}")
    except Exception as e:
        print(f"Register failed: {e}")

    # 2. Register same user (should fail)
    print("\nTest 2: Register Duplicate User")
    try:
        reg_response = user_stub.Register(service_pb2.UserRequest(
            username=f"user_{uid}",
            email=email,
            password="securepassword"
        ))
        print(f"Register response (duplicate): success={reg_response.success}, message={reg_response.message}")
    except Exception as e:
        print(f"Register duplicate failed: {e}")

    # 3. Login
    print("\nTest 3: User Login")
    jwt_token = ""
    try:
        login_response = user_stub.Login(service_pb2.LoginRequest(
            email=email,
            password="securepassword"
        ))
        jwt_token = login_response.token
        print(f"Login response: success={login_response.success}, token={jwt_token[:15]}...")
    except Exception as e:
        print(f"Login failed: {e}")
        return

    metadata = (('authorization', f'Bearer {jwt_token}'),)

    # 4. Add Product
    print("\nTest 4: Add Product (Auth Protected)")
    product_channel = grpc.insecure_channel('localhost:50052')
    product_stub = service_pb2_grpc.ProductServiceStub(product_channel)
    try:
        prod_response = product_stub.AddProduct(service_pb2.ProductRequest(
            name=f"Laptop {uid}",
            price=999.99
        ), metadata=metadata)
        print(f"Add product response: success={prod_response.success}, message={prod_response.message}")
    except Exception as e:
        print(f"Add product failed: {e}")

    # 5. Get Products
    print("\nTest 5: Get Products (Pagination)")
    try:
        products_response = product_stub.GetProducts(service_pb2.PaginationRequest(
            limit=5,
            offset=0
        ))
        print(f"Get products count: {len(products_response.products)}")
        for p in products_response.products:
            print(f" - Product: id={p.id}, name={p.name}, price={p.price}")
    except Exception as e:
        print(f"Get products failed: {e}")

    # 6. Create Order
    print("\nTest 6: Create Order (Success, Auth Protected)")
    order_channel = grpc.insecure_channel('localhost:50053')
    order_stub = service_pb2_grpc.OrderServiceStub(order_channel)
    
    import jwt
    import os
    from dotenv import load_dotenv
    load_dotenv()
    try:
        decoded = jwt.decode(jwt_token, os.getenv("SECRET_KEY", "default_secret_key"), algorithms=["HS256"], options={"verify_signature": False})
        user_id = decoded['sub']

        order_response = order_stub.CreateOrder(service_pb2.OrderRequest(
            product_id=1,
            user_id=user_id,
            quantity=2
        ), metadata=metadata)
        print(f"Create order response: success={order_response.success}, message={order_response.message}")
    except Exception as e:
        print(f"Create order failed: {e}")

    # 7. Create Order without Auth metadata
    print("\nTest 7: Create Order (Without Auth)")
    try:
        order_response = order_stub.CreateOrder(service_pb2.OrderRequest(
            product_id=1,
            user_id=user_id,
            quantity=2
        ))
        print(f"Create order response (no auth): success={order_response.success}, message={order_response.message}")
    except grpc.RpcError as e:
        print(f"Create order (no auth) correctly failed: {e.code()} - {e.details()}")

if __name__ == '__main__':
    run_tests()
