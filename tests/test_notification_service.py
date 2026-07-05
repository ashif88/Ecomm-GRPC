from unittest.mock import MagicMock

import pytest

import service_pb2
from app.services.notification_service import NotificationService


@pytest.fixture
def notification_service():
    return NotificationService()


def test_send_email_success(notification_service, mocker):
    mock_send_message = mocker.patch("app.services.notification_service.send_message")

    request = service_pb2.NotificationRequest(
        subject="Test Subject", body="Test Body", recipient="test@test.com"
    )
    context = MagicMock()

    response = notification_service.SendEmail(request, context)

    assert response.success is True
    assert response.message == "Email sent successfully"
    mock_send_message.assert_called_once_with(
        "email_topic", "To: test@test.com, Subject: Test Subject, Body: Test Body"
    )
