import asyncio
from datetime import date, datetime, timedelta
import json
from typing import Annotated
from fastapi import APIRouter, Depends, Query
from api.trade.schemas import DynamicsQueryParamsSchema, FilterSchema
from db.base import async_session
from sqlalchemy import desc, distinct, select
from db.models import SpimexTradingResults as Trade
from cache.reddis_client import redis_client


router = APIRouter(
    prefix="/trades",
    tags=["trading"],
)


def time_to_cache_clean() -> datetime:
    now = datetime.now()
    target_time = now.replace(hour=14, minute=11, second=0, microsecond=0)
    if now > target_time:
        target_time += timedelta(days=1)
    time_left = target_time - now
    return time_left


@router.get("/last-trading-dates")
async def get_last_trading_dates(
    count: Annotated[
        int,
        Query(
            gt=0,
            lt=31,
            example=1,
            description="Количество последних торговых дней (от 1 до 30).",
        ),
    ],
) -> list[date]:
    cache_key = f"last-trading-dates:{count}"

    redis = redis_client.get_client()
    cached_data = await redis.get(cache_key)
    if cached_data:
        return json.loads(cached_data)

    async with async_session() as session:
        query = select(distinct(Trade.date)).order_by(desc(Trade.date)).limit(count)
        result = (await session.scalars(query)).all()
        result_data = [str(row) for row in result]
        time_left = await asyncio.to_thread(time_to_cache_clean)
        await redis.setex(cache_key, time_left.seconds, json.dumps(result_data))
    return result


@router.get("/dynamics")
async def get_dynamics(params: DynamicsQueryParamsSchema = Depends()):
    cache_key = f"dynamics:{params.start_date}:{params.end_date}:{params.option.oil_id}:{params.option.delivery_type_id}:{params.option.delivery_basis_id}"

    redis = redis_client.get_client()
    cached_data = await redis.get(cache_key)
    if cached_data:
        return json.loads(cached_data)

    async with async_session() as session:
        query = select(Trade).where(
            Trade.date > params.start_date, Trade.date < params.end_date
        )
        if params.option.oil_id:
            query = query.where(Trade.oil_id == params.option.oil_id)

        if params.option.delivery_type_id:
            query = query.where(
                Trade.delivery_type_id == params.option.delivery_type_id
            )

        if params.option.delivery_basis_id:
            query = query.where(
                Trade.delivery_basis_id == params.option.delivery_basis_id
            )

        result = (await session.scalars(query)).all()
        result_data = [row.as_dict() for row in result]
        time_left = await asyncio.to_thread(time_to_cache_clean)
        await redis.setex(cache_key, time_left.seconds, json.dumps(result_data))

    return result


async def last_date_of_trade() -> date:
    async with async_session() as session:
        query = select(distinct(Trade.date)).order_by(desc(Trade.date))
        date = (await session.scalars(query)).first()
    return date


@router.get("/trading-results")
async def get_trading_results(
    option: Annotated[FilterSchema, Depends()],
    date: Annotated[date, Depends(last_date_of_trade)],
):
    cache_key = f"trading-results:{option.oil_id}:{option.delivery_type_id}:{option.delivery_basis_id}"

    redis = redis_client.get_client()
    cached_data = await redis.get(cache_key)
    if cached_data:
        return json.loads(cached_data)

    async with async_session() as session:
        query = select(Trade).where(Trade.date == date)
        if option.oil_id:
            query = query.where(Trade.oil_id == option.oil_id)

        if option.delivery_type_id:
            query = query.where(Trade.delivery_type_id == option.delivery_type_id)

        if option.delivery_basis_id:
            query = query.where(Trade.delivery_basis_id == option.delivery_basis_id)

        result = (await session.scalars(query)).all()
        time_left = await asyncio.to_thread(time_to_cache_clean)
        result_data = [row.as_dict() for row in result]
        await redis.setex(
            cache_key, time_left.seconds, json.dumps(result_data)
        )
    return result
