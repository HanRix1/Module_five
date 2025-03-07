import pytest
from fastapi.testclient import TestClient
from unittest import mock
from datetime import date
import json
from api.app import create_app
from api.trade.schemas import FilterSchema
from db.base import async_session
from db.models import SpimexTradingResults as Trade

@pytest.fixture(scope="class")
def application():
    return create_app()

@pytest.fixture(scope="class")
def client(application):
    return TestClient(application)


@pytest.mark.usefixtures("client")
class TestGetTraidingResult:
    
    @pytest.fixture(autouse=True)
    def set_up(self, client):
        self.client = client
        option = FilterSchema(oil_id="A100", delivery_type_id=None, delivery_basis_id="NVY")

        self.params = {
            "oil_id": option.oil_id,
            "delivery_type_id": option.delivery_type_id,
            "delivery_basis_id": option.delivery_basis_id,
        }

    @pytest.mark.asyncio
    async def test_get_trading_results_cache_hit(self):
        with mock.patch(
            "api.trade.routers.RedisCache.get_cached_data",
            return_value=json.dumps([{"oil_id": "A100", "delivery_type_id": "NVY"}])
        ) as redis_method:
            response = self.client.get("/trades/trading-results", params=self.params)

            assert response.status_code == 200


    @pytest.mark.asyncio
    async def test_get_trading_results_cache_no_hit(self):
        fake_db_result = [
            Trade(
                exchange_product_name="Бензин (АИ-100-К5), ст. Новоярославская (ст. отправления)",
                delivery_basis_id="NVY",
                delivery_type_id="F",
                total=4080000,
                date="2025-02-21T00:00:00",
                updated_at="2025-02-21T23:07:13.127525",
                id="ea10696e-f63a-486b-9f02-d747ec73c486",
                exchange_product_id="A100NVY060F",
                oil_id="A100",
                delivery_basis_name="ст. Новоярославская",
                volume=60,
                count=1,
                created_at="2025-02-21T23:07:13.127525"
            )
        ]

        with mock.patch("api.trade.routers.RedisCache.get_cached_data", return_value=None) as redis_get_mock, \
        mock.patch("api.trade.routers.RedisCache.set_cached_data") as redis_set_mock:

            response = self.client.get("/trades/trading-results", params=self.params)

            assert response.status_code == 200
            assert response.json() == [row.as_dict() for row in fake_db_result]

