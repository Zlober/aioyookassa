from unittest.mock import patch

import aiohttp
import pytest
from aioresponses import aioresponses

from aioyookassa.core.client import YooKassa
from aioyookassa.types import Payment, PaymentsList


class TestHttpSessionInit:
    """Constructor accepts an optional http_session parameter."""

    async def test_default_http_session_is_none(self, api_key, shop_id):
        client = YooKassa(api_key=api_key, shop_id=shop_id)
        assert client._http_session is None

    async def test_can_pass_http_session(self, api_key, shop_id):
        async with aiohttp.ClientSession() as session:
            client = YooKassa(api_key=api_key, shop_id=shop_id, http_session=session)
            assert client._http_session is session

    async def test_http_session_kwarg_accepted_as_none(self, api_key, shop_id):
        client = YooKassa(api_key=api_key, shop_id=shop_id, http_session=None)
        assert client._http_session is None


class TestSessionLifecycle:
    """Verify when sessions are created/closed depending on http_session."""

    async def test_default_creates_new_session_per_request(
        self, api_key, shop_id, base_url, payment_response
    ):
        client = YooKassa(api_key=api_key, shop_id=shop_id)

        with patch(
            "aioyookassa.core.abc.client.ClientSession",
            wraps=aiohttp.ClientSession,
        ) as session_cls, aioresponses() as m:
            m.get(f"{base_url}/payments/pay_1", payload=payment_response)
            m.get(f"{base_url}/payments/pay_2", payload=payment_response)

            await client.get_payment("pay_1")
            await client.get_payment("pay_2")

        assert session_cls.call_count == 2

    async def test_provided_session_is_used_not_recreated(
        self, api_key, shop_id, base_url, payment_response
    ):
        async with aiohttp.ClientSession() as session:
            client = YooKassa(
                api_key=api_key, shop_id=shop_id, http_session=session
            )

            with patch(
                "aioyookassa.core.abc.client.ClientSession"
            ) as session_cls, aioresponses() as m:
                m.get(f"{base_url}/payments/pay_1", payload=payment_response)
                m.get(f"{base_url}/payments/pay_2", payload=payment_response)

                await client.get_payment("pay_1")
                await client.get_payment("pay_2")

            session_cls.assert_not_called()

    async def test_provided_session_not_closed_after_request(
        self, api_key, shop_id, base_url, payment_response
    ):
        session = aiohttp.ClientSession()
        try:
            client = YooKassa(
                api_key=api_key, shop_id=shop_id, http_session=session
            )
            with aioresponses() as m:
                m.get(f"{base_url}/payments/pay_1", payload=payment_response)
                await client.get_payment("pay_1")

            assert not session.closed
        finally:
            await session.close()

    async def test_multiple_requests_reuse_provided_session(
        self, api_key, shop_id, base_url, payment_response
    ):
        async with aiohttp.ClientSession() as session:
            client = YooKassa(
                api_key=api_key, shop_id=shop_id, http_session=session
            )
            with aioresponses() as m:
                m.get(f"{base_url}/payments/pay_1", payload=payment_response)
                m.get(f"{base_url}/payments/pay_2", payload=payment_response)
                m.post(
                    f"{base_url}/payments/pay_3/cancel", payload=payment_response
                )

                p1 = await client.get_payment("pay_1")
                p2 = await client.get_payment("pay_2")
                p3 = await client.cancel_payment("pay_3")

            assert p1.id == p2.id == p3.id == payment_response["id"]
            assert not session.closed


class TestGetPayment:
    async def test_default_session(
        self, api_key, shop_id, base_url, payment_response
    ):
        client = YooKassa(api_key=api_key, shop_id=shop_id)
        with aioresponses() as m:
            m.get(f"{base_url}/payments/pay_1", payload=payment_response)
            payment = await client.get_payment("pay_1")
        assert isinstance(payment, Payment)
        assert payment.id == payment_response["id"]

    async def test_with_provided_session(
        self, api_key, shop_id, base_url, payment_response
    ):
        async with aiohttp.ClientSession() as session:
            client = YooKassa(
                api_key=api_key, shop_id=shop_id, http_session=session
            )
            with aioresponses() as m:
                m.get(f"{base_url}/payments/pay_1", payload=payment_response)
                payment = await client.get_payment("pay_1")
            assert isinstance(payment, Payment)
            assert payment.id == payment_response["id"]
            assert not session.closed


class TestGetPayments:
    async def test_default_session(
        self, api_key, shop_id, base_url, payments_list_response
    ):
        client = YooKassa(api_key=api_key, shop_id=shop_id)
        with aioresponses() as m:
            m.get(f"{base_url}/payments", payload=payments_list_response)
            result = await client.get_payments()
        assert isinstance(result, PaymentsList)
        assert len(result.list) == 1

    async def test_with_provided_session(
        self, api_key, shop_id, base_url, payments_list_response
    ):
        async with aiohttp.ClientSession() as session:
            client = YooKassa(
                api_key=api_key, shop_id=shop_id, http_session=session
            )
            with aioresponses() as m:
                m.get(f"{base_url}/payments", payload=payments_list_response)
                result = await client.get_payments()
            assert isinstance(result, PaymentsList)
            assert len(result.list) == 1
            assert not session.closed


class TestCreatePayment:
    async def test_default_session(
        self, api_key, shop_id, base_url, amount, payment_response
    ):
        client = YooKassa(api_key=api_key, shop_id=shop_id)
        with aioresponses() as m:
            m.post(f"{base_url}/payments", payload=payment_response)
            payment = await client.create_payment(
                amount=amount, description="test"
            )
        assert isinstance(payment, Payment)
        assert payment.id == payment_response["id"]

    async def test_with_provided_session(
        self, api_key, shop_id, base_url, amount, payment_response
    ):
        async with aiohttp.ClientSession() as session:
            client = YooKassa(
                api_key=api_key, shop_id=shop_id, http_session=session
            )
            with aioresponses() as m:
                m.post(f"{base_url}/payments", payload=payment_response)
                payment = await client.create_payment(
                    amount=amount, description="test"
                )
            assert isinstance(payment, Payment)
            assert payment.id == payment_response["id"]
            assert not session.closed


class TestCapturePayment:
    async def test_default_session(
        self, api_key, shop_id, base_url, payment_response
    ):
        client = YooKassa(api_key=api_key, shop_id=shop_id)
        with aioresponses() as m:
            m.post(
                f"{base_url}/payments/pay_1/capture", payload=payment_response
            )
            payment = await client.capture_payment("pay_1")
        assert isinstance(payment, Payment)
        assert payment.id == payment_response["id"]

    async def test_with_provided_session(
        self, api_key, shop_id, base_url, payment_response
    ):
        async with aiohttp.ClientSession() as session:
            client = YooKassa(
                api_key=api_key, shop_id=shop_id, http_session=session
            )
            with aioresponses() as m:
                m.post(
                    f"{base_url}/payments/pay_1/capture",
                    payload=payment_response,
                )
                payment = await client.capture_payment("pay_1")
            assert isinstance(payment, Payment)
            assert not session.closed


class TestCancelPayment:
    async def test_default_session(
        self, api_key, shop_id, base_url, payment_response
    ):
        client = YooKassa(api_key=api_key, shop_id=shop_id)
        with aioresponses() as m:
            m.post(
                f"{base_url}/payments/pay_1/cancel", payload=payment_response
            )
            payment = await client.cancel_payment("pay_1")
        assert isinstance(payment, Payment)

    async def test_with_provided_session(
        self, api_key, shop_id, base_url, payment_response
    ):
        async with aiohttp.ClientSession() as session:
            client = YooKassa(
                api_key=api_key, shop_id=shop_id, http_session=session
            )
            with aioresponses() as m:
                m.post(
                    f"{base_url}/payments/pay_1/cancel",
                    payload=payment_response,
                )
                payment = await client.cancel_payment("pay_1")
            assert isinstance(payment, Payment)
            assert not session.closed
