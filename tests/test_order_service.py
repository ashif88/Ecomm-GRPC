from unittest.mock import MagicMock

import pytest

import service_pb2
from app.models.order import Order
from app.models.product import Product
from app.models.user import User
from app.services.order_service import OrderService


@pytest.fixture
def order_service():
    return OrderService()


def test_create_order_success(order_service, mocker):
    mocker.patch("app.models.product.Product.query")
    mocker.patch("app.models.user.User.query")

    mock_product = Product(id=1, name="Test Product", price=10.0)
    mock_user = User(id=1, username="test_user")

    Product.query.get.return_value = mock_product
    User.query.get.return_value = mock_user

    mock_db_session = mocker.patch("app.services.order_service.db.session")
    mock_send_message = mocker.patch("app.services.order_service.send_message")

    request = service_pb2.OrderRequest(product_id=1, user_id=1, quantity=2)
    context = MagicMock()

    response = order_service.CreateOrder(request, context)

    assert response.success is True
    assert "successfully" in response.message
    mock_db_session.add.assert_called_once()
    mock_db_session.commit.assert_called_once()
    mock_send_message.assert_called_once()


def test_create_order_invalid_quantity(order_service, mocker):
    request = service_pb2.OrderRequest(product_id=1, user_id=1, quantity=0)
    context = MagicMock()

    response = order_service.CreateOrder(request, context)

    assert response.success is False
    assert "Quantity must be greater than 0" in response.message


def test_create_order_product_not_found(order_service, mocker):
    mocker.patch("app.models.product.Product.query")
    Product.query.get.return_value = None

    request = service_pb2.OrderRequest(product_id=99, user_id=1, quantity=2)
    context = MagicMock()

    response = order_service.CreateOrder(request, context)

    assert response.success is False
    assert "Product not found" in response.message
