from typing import Annotated
from fastapi import Depends, Query
from pydantic import BaseModel, TypeAdapter, model_validator
from datetime import date, timedelta


class FilterSchema(BaseModel):
    oil_id: Annotated[
        str | None,
        Query(description="Фильтрация по идентификатору нефти (опционально)."),
    ] = None
    delivery_type_id: Annotated[
        str | None, Query(description="Фильтрация по типу поставки (опционально).")
    ] = None
    delivery_basis_id: Annotated[
        str | None, Query(description="Фильтрация по базису поставки (опционально).")
    ] = None


class DynamicsQueryParamsSchema(BaseModel):
    start_date: date = Query(
        description="Дата начала периода", default=date.today() - timedelta(1)
    )
    end_date: date = Query(description="Дата окончания периода", default=date.today())
    option: Annotated[FilterSchema, Depends()]

    @model_validator(mode="after")
    def validate_dates(cls, values):
        start_date = values.start_date
        end_date = values.end_date

        if start_date > end_date:
            raise ValueError(
                "Дата начала (start_date) не может быть позже даты окончания (end_date)"
            )

        return values
