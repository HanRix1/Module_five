import json
import pytest
from api.trade.schemas import FilterSchema
from db.models import SpimexTradingResults as Trade
from unittest.mock import MagicMock


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
        
        self.fake_db_result = [
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

    @pytest.mark.asyncio
    async def test_get_trading_results_with_no_cache(self, mock_redis_cache, mock_db_session):
        
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = self.fake_db_result
        mock_db_session.scalars.return_value = mock_scalars

        mock_redis_cache.get_cached_data.return_value = None
        mock_redis_cache.set_cached_data.return_value = None
        response = self.client.get("/trades/trading-results", params=self.params)

        assert response.status_code == 200
        assert response.json() == [row.as_dict() for row in self.fake_db_result]

    @pytest.mark.asyncio
    async def test_get_trading_results_with_cache(self, mock_redis_cache, mock_db_session):

        fake_db_result_dicts = [row.as_dict() for row in self.fake_db_result]
        mock_redis_cache.get_cached_data.return_value = json.dumps(fake_db_result_dicts)
        response = self.client.get("/trades/trading-results", params=self.params)

        assert response.status_code == 200
        assert response.json() == [row.as_dict() for row in self.fake_db_result]


