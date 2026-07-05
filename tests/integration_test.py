import os
import random
import sys

import grpc
import jwt
import pytest
from dotenv import load_dotenv

# Add root folder to python path dynamically
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import service_pb2
import service_pb2_grpc

load_dotenv()


@pytest.mark.integration
def test_e2e_system_flow():
    """
    End-to-End integration test covering the core paths across microservices.
    Requires the gRPC servers to be running locally on their default ports.
    """
    # Setup Channels
    user_channel = grpc.insecure_channel("localhost:50051")
    product_channel = grpc.insecure_channel("localhost:50052")
    order_channel = grpc.insecure_channel("localhost:50053")

    user_stub = service_pb2_grpc.UserServiceStub(user_channel)
    product_stub = service_pb2_grpc.ProductServiceStub(product_channel)
    order_stub = service_pb2_grpc.OrderServiceStub(order_channel)

    uid = random.randint(1000, 9999)
    email = f"user_{uid}@example.com"
    username = f"user_{uid}"

    # 1. Register User
    reg_response = user_stub.Register(
        service_pb2.UserRequest(
            username=username, email=email, password="securepassword"
        )
    )
    assert reg_response.success is True
    assert "successfully" in reg_response.message

    # 2. Register Duplicate User
    reg_duplicate_response = user_stub.Register(
        service_pb2.UserRequest(
            username=username, email=email, password="securepassword"
        )
    )
    assert reg_duplicate_response.success is False
    assert "already exists" in reg_duplicate_response.message

    # 3. Login
    login_response = user_stub.Login(
        service_pb2.LoginRequest(email=email, password="securepassword")
    )
    assert login_response.success is True
    assert login_response.token != ""

    jwt_token = login_response.token
    metadata = (("authorization", f"Bearer {jwt_token}"),)

    # Decode token to get user_id
    decoded = jwt.decode(
        jwt_token,
        os.getenv("SECRET_KEY", "default_secret_key"),
        algorithms=["HS256"],
        options={"verify_signature": False},
    )
    user_id = int(decoded["sub"])

    # 4. Add Product (Auth Protected)
    prod_response = product_stub.AddProduct(
        service_pb2.ProductRequest(name=f"Laptop {uid}", price=999.99),
        metadata=metadata,
    )
    assert prod_response.success is True
    assert "successfully" in prod_response.message

    # 5. Get Products (Pagination)
    products_response = product_stub.GetProducts(
        service_pb2.PaginationRequest(limit=5, offset=0)
    )
    assert len(products_response.products) > 0
    # Store the ID of the last product to ensure we order a real product
    product_id = products_response.products[-1].id

    # 6. Create Order (Auth Protected)
    order_response = order_stub.CreateOrder(
        service_pb2.OrderRequest(product_id=product_id, user_id=user_id, quantity=2),
        metadata=metadata,
    )
    assert order_response.success is True
    assert "successfully" in order_response.message

    # 7. Create Order without Auth metadata
    with pytest.raises(grpc.RpcError) as exc_info:
        order_stub.CreateOrder(
            service_pb2.OrderRequest(product_id=product_id, user_id=user_id, quantity=2)
        )

    assert exc_info.value.code() == grpc.StatusCode.UNAUTHENTICATED
    assert "Missing or invalid token" in exc_info.value.details()


if __name__ == "__main__":
    # Allows running directly via `python tests/integration_test.py`
    pytest.main(["-v", __file__])
