from unittest.mock import MagicMock

import pytest

import service_pb2
from app.models.user import User
from app.services.user_service import UserService


@pytest.fixture
def user_service():
    return UserService()


def test_register_success(user_service, mocker):
    mocker.patch("app.models.user.User.query")
    User.query.filter.return_value.first.return_value = None  # No existing user
    mock_db_session = mocker.patch("app.services.user_service.db.session")

    request = service_pb2.UserRequest(
        username="test_user", email="test@test.com", password="password123"
    )
    context = MagicMock()

    response = user_service.Register(request, context)

    assert response.success is True
    assert response.message == "User registered successfully"
    mock_db_session.add.assert_called_once()
    mock_db_session.commit.assert_called_once()
    mock_db_session.remove.assert_called_once()


def test_register_empty_fields(user_service, mocker):
    request = service_pb2.UserRequest(
        username="", email="test@test.com", password="password123"
    )
    context = MagicMock()

    response = user_service.Register(request, context)

    assert response.success is False
    assert "cannot be empty" in response.message


def test_register_duplicate_user(user_service, mocker):
    mocker.patch("app.models.user.User.query")
    # Mock that a user already exists
    User.query.filter.return_value.first.return_value = User(
        username="test_user", email="test@test.com"
    )

    mock_db_session = mocker.patch("app.services.user_service.db.session")

    request = service_pb2.UserRequest(
        username="test_user", email="test@test.com", password="password123"
    )
    context = MagicMock()

    response = user_service.Register(request, context)

    assert response.success is False
    assert "already exists" in response.message
    mock_db_session.add.assert_not_called()
    mock_db_session.remove.assert_called_once()


def test_login_success(user_service, mocker):
    mocker.patch("app.models.user.User.query")
    mock_user = User(id=1, email="test@test.com", password="hashedpassword")
    User.query.filter_by.return_value.first.return_value = mock_user

    mocker.patch("app.services.user_service.check_password_hash", return_value=True)
    mocker.patch("app.services.user_service.generate_jwt", return_value="mocked_token")
    mock_db_session = mocker.patch("app.services.user_service.db.session")

    request = service_pb2.LoginRequest(email="test@test.com", password="password123")
    context = MagicMock()

    response = user_service.Login(request, context)

    assert response.success is True
    assert response.token == "mocked_token"
    mock_db_session.remove.assert_called_once()


def test_login_invalid_credentials(user_service, mocker):
    mocker.patch("app.models.user.User.query")
    mock_user = User(id=1, email="test@test.com", password="hashedpassword")
    User.query.filter_by.return_value.first.return_value = mock_user

    # Mock invalid password
    mocker.patch("app.services.user_service.check_password_hash", return_value=False)
    mock_db_session = mocker.patch("app.services.user_service.db.session")

    request = service_pb2.LoginRequest(email="test@test.com", password="wrongpassword")
    context = MagicMock()

    response = user_service.Login(request, context)

    assert response.success is False
    assert "Invalid credentials" in response.token
    mock_db_session.remove.assert_called_once()
