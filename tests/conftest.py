import pytest

from aioyookassa.types.payment import PaymentAmount


API_KEY = "test_api_key"
SHOP_ID = 123456
BASE_URL = "https://api.yookassa.ru/v3"


@pytest.fixture
def api_key() -> str:
    return API_KEY


@pytest.fixture
def shop_id() -> int:
    return SHOP_ID


@pytest.fixture
def base_url() -> str:
    return BASE_URL


@pytest.fixture
def amount() -> PaymentAmount:
    return PaymentAmount(value=100, currency="RUB")


@pytest.fixture
def payment_response() -> dict:
    return {
        "id": "2c85beb4-000f-5000-8000-15c5a86e6f0f",
        "status": "pending",
        "amount": {"value": 100, "currency": "RUB"},
        "recipient": {"account_id": "100500", "gateway_id": "654321"},
        "created_at": "2024-01-01T12:00:00.000Z",
        "test": False,
        "paid": False,
        "refundable": False,
    }


@pytest.fixture
def payments_list_response(payment_response) -> dict:
    return {
        "type": "list",
        "items": [payment_response],
        "cursor": None,
    }
