from unittest.mock import MagicMock

import pytest

import service_pb2
from app.models.product import Product
from app.services.product_service import ProductService


@pytest.fixture
def product_service():
    return ProductService()


def test_add_product_success(product_service, mocker):
    mock_db_session = mocker.patch("app.services.product_service.db.session")
    mock_delete_cache = mocker.patch("app.services.product_service.delete_cached_data")

    request = service_pb2.ProductRequest(name="Test Product", price=10.99)
    context = MagicMock()

    response = product_service.AddProduct(request, context)

    assert response.success is True
    assert "successfully" in response.message
    mock_db_session.add.assert_called_once()
    mock_db_session.commit.assert_called_once()
    mock_delete_cache.assert_called_once_with("products_all")


def test_add_product_invalid_input(product_service, mocker):
    mock_db_session = mocker.patch("app.services.product_service.db.session")

    # Test empty name and negative price
    request = service_pb2.ProductRequest(name="", price=-5.0)
    context = MagicMock()

    response = product_service.AddProduct(request, context)

    assert response.success is False
    assert "Invalid product name or price" in response.message
    mock_db_session.add.assert_not_called()


def test_get_products_cache_hit(product_service, mocker):
    mock_get_cache = mocker.patch("app.services.product_service.get_cached_data")
    mock_get_cache.return_value = '[{"id": 1, "name": "Cached Product", "price": 9.99}]'

    request = service_pb2.PaginationRequest(limit=10, offset=0)
    context = MagicMock()

    response = product_service.GetProducts(request, context)

    assert len(response.products) == 1
    assert response.products[0].name == "Cached Product"
    mock_get_cache.assert_called_once_with("products_10_0")


def test_get_products_db_fallback(product_service, mocker):
    mock_get_cache = mocker.patch(
        "app.services.product_service.get_cached_data", return_value=None
    )
    mock_set_cache = mocker.patch("app.services.product_service.set_cached_data")

    mocker.patch("app.models.product.Product.query")
    mock_product = Product(id=1, name="DB Product", price=15.99)
    Product.query.limit.return_value.offset.return_value.all.return_value = [
        mock_product
    ]

    request = service_pb2.PaginationRequest(limit=10, offset=0)
    context = MagicMock()

    response = product_service.GetProducts(request, context)

    assert len(response.products) == 1
    assert response.products[0].name == "DB Product"
    mock_set_cache.assert_called_once()
