from datetime import date, timedelta
import json
import pytest
from api.trade.schemas import FilterSchema
from db.models import SpimexTradingResults as Trade
from unittest.mock import MagicMock


@pytest.mark.usefixtures("client")
class TestGetDynamics:
    
    @pytest.fixture(autouse=True)
    def set_up(self, client):
        self.client = client
        option = FilterSchema(oil_id="A100", delivery_type_id=None, delivery_basis_id="NVY")

        self.params = {
            "start_date": "2025-02-20",
            "end_date": "2025-03-07",
            "oil_id": option.oil_id,
            "delivery_type_id": option.delivery_type_id,
            "delivery_basis_id": option.delivery_basis_id,
        }
        
        self.fake_db_result = [
            Trade(
                exchange_product_name="ДТ ЕВРО, летнее, сорта C, эк. класса К5 марки ДТ-Л-К5 по ГОСТ 32511-2013, ЛПДС Невская (франко-резервуар ОТП Транснефть)",
                delivery_basis_id="NVL",
                delivery_type_id="O",
                total=32540250,
                date="2025-02-21T00:00:00",
                updated_at="2025-02-21T23:07:13.128524",
                oil_id="DST5",
                id="489ade0a-c69d-40c0-946c-be95ae5b104a",
                exchange_product_id="DST5NVL001O",
                delivery_basis_name="ЛПДС Невская",
                volume=550,
                count=9,
                created_at="2025-02-21T23:07:13.128524"
            )
        ]
        
    @pytest.mark.asyncio
    async def test_get_dynamics_with_no_cache(self, mock_redis_cache, mock_db_session):
        
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = self.fake_db_result
        mock_db_session.scalars.return_value = mock_scalars

        mock_redis_cache.get_cached_data.return_value = None
        mock_redis_cache.set_cached_data.return_value = None
        response = self.client.get("/trades/trading-results", params=self.params)

        assert response.status_code == 200
        assert response.json() == [row.as_dict() for row in self.fake_db_result]

    @pytest.mark.asyncio
    async def test_get_dynamics_with_cache(self, mock_redis_cache, mock_db_session):

        fake_db_result_dicts = [row.as_dict() for row in self.fake_db_result]
        mock_redis_cache.get_cached_data.return_value = json.dumps(fake_db_result_dicts)
        response = self.client.get("/trades/trading-results", params=self.params)

        assert response.status_code == 200
        assert response.json() == [row.as_dict() for row in self.fake_db_result]

    @pytest.mark.asyncio
    async def test_date_ranges(self, client):

        self.params["start_date"] = "2025-03-03"
        self.params["end_date"] = "2025-02-28"
        

        with pytest.raises(ValueError, match=r".*Дата начала \(start_date\) не может быть позже даты окончания \(end_date\).*"):
            response = client.get("/trades/dynamics", params=self.params)
