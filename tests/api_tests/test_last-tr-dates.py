import json
import pytest
from unittest.mock import MagicMock


@pytest.mark.usefixtures("client")
class TestGetLastTrDates:
    
    @pytest.fixture(autouse=True)
    def set_up(self, client):
        self.client = client
        self.params = {"count": 4}
        self.fake_db_result = [
            "2025-02-21",
            "2025-02-20",
            "2025-02-19",
            "2025-02-18"
        ]

    @pytest.mark.asyncio
    async def test_get_last_trading_dates_with_no_cache(self, mock_redis_cache, mock_db_session):
        
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = self.fake_db_result
        mock_db_session.scalars.return_value = mock_scalars

        mock_redis_cache.get_cached_data.return_value = None
        mock_redis_cache.set_cached_data.return_value = None
        response = self.client.get("/trades/last-trading-dates", params=self.params)

        assert response.status_code == 200
        assert response.json() == self.fake_db_result
    

    @pytest.mark.asyncio
    async def test_get_last_trading_dates_with_cache(self, mock_redis_cache):

        mock_redis_cache.get_cached_data.return_value = json.dumps(self.fake_db_result)
        response = self.client.get("/trades/trading-results", params=self.params)

        assert response.status_code == 200
        assert response.json() == self.fake_db_result

    @pytest.mark.parametrize("count, expected_status_code", [
        (0, 422),  
        (31, 422),
        (-5, 422),
    ])
    @pytest.mark.asyncio
    async def test_get_last_trading_dates_with_invalid_count(self, count, expected_status_code):
        response = self.client.get("/trades/last-trading-dates", params={"count": count})
        assert response.status_code == expected_status_code


