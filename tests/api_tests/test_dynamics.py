import pytest
import json
from unittest import mock
from httpx import AsyncClient
from api.app import create_app
from api.trade.schemas import FilterSchema
from db.models import SpimexTradingResults as Trade

@pytest.fixture(scope="class")
async def application():
    return create_app()

@pytest.fixture(scope="class")
async def client(application):
    async with AsyncClient(app=application, base_url="http://test") as ac:
        yield ac

@pytest.mark.usefixtures("client")
class TestDynamicsEndPoint:
    
    @pytest.fixture(autouse=True)
    def set_up(self, client):
        self.client = client
        option = FilterSchema(oil_id="A100", delivery_type_id=None, delivery_basis_id="NVY")

        self.params = {
            "oil_id": option.oil_id,
            "delivery_type_id": option.delivery_type_id,
            "delivery_basis_id": option.delivery_basis_id,
        }
