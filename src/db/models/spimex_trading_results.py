from db import Base, uuid_pk, str_128, str_256
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import func
from datetime import datetime


class SpimexTradingResults(Base):
    __tablename__ = "spimex_trading_results"

    id: Mapped[uuid_pk]
    exchange_product_id: Mapped[str_128]
    exchange_product_name: Mapped[str_256]
    oil_id: Mapped[str_128]
    delivery_basis_id: Mapped[str_128]
    delivery_basis_name: Mapped[str_128]
    delivery_type_id: Mapped[str_128]
    volume: Mapped[int]
    total: Mapped[int]
    count: Mapped[int]
    date: Mapped[datetime]
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.now, onupdate=datetime.now
    )

    def as_dict(self):
        return {
            "id": str(self.id),
            "exchange_product_id": self.exchange_product_id,
            "exchange_product_name": self.exchange_product_name,
            "oil_id": self.oil_id,
            "delivery_basis_id": self.delivery_basis_id,
            "delivery_basis_name": self.delivery_basis_name,
            "delivery_type_id": self.delivery_type_id,
            "volume": self.volume,
            "total": self.total,
            "count": self.count,
            "date": str(self.date),
            "created_at": str(self.created_at),
            "updated_at": str(self.updated_at),
        }
