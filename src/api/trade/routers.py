import asyncio
from datetime import date, datetime, timedelta
import json
from typing import Annotated, Any
from fastapi import APIRouter, Depends, Query
from api.trade.schemas import DynamicsQueryParamsSchema, FilterSchema
from db.base import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import desc, distinct, select
from db.models import SpimexTradingResults as Trade


from cache.cache_client import RedisCache
from cache.dependencies import get_redis_cache


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
            examples=[1],
            description="Количество последних торговых дней (от 1 до 30).",
        ),
    ],
    cache: Annotated[RedisCache, Depends(get_redis_cache)],
    session: Annotated[AsyncSession, Depends(get_session)]
) -> list[date]:
    cache_key = f"last-trading-dates:{count}"

    cached_data = await cache.get_cached_data(cache_key)
    if cached_data:
        return json.loads(cached_data)


    query = select(distinct(Trade.date)).order_by(desc(Trade.date)).limit(count)
    result = (await session.scalars(query)).all()
    
    result_data = [str(row) for row in result]
    time_left = await asyncio.to_thread(time_to_cache_clean)
    await cache.set_cached_data(cache_key, time_left, result_data)
    
    return result


@router.get("/dynamics")
async def get_dynamics(
    params: Annotated[DynamicsQueryParamsSchema, Depends()],
    cache: Annotated[RedisCache, Depends(get_redis_cache)],
    session: Annotated[AsyncSession, Depends(get_session)]
):
    cache_key = f"dynamics:{params.start_date}:{params.end_date}:{params.option.oil_id}:{params.option.delivery_type_id}:{params.option.delivery_basis_id}"

    cached_data = await cache.get_cached_data(cache_key)
    if cached_data:
        return json.loads(cached_data)
  

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
    
    time_left = await asyncio.to_thread(time_to_cache_clean)
    result_data = [row.as_dict() for row in result]
    await cache.set_cached_data(cache_key, time_left, result_data)

    return result


async def last_date_of_trade(session: Annotated[AsyncSession, Depends(get_session)]) -> date:
    query = select(distinct(Trade.date)).order_by(desc(Trade.date))
    date = (await session.scalars(query)).first()
    return date


@router.get("/trading-results")
async def get_trading_results(
    option: Annotated[FilterSchema, Depends()],
    cache: Annotated[RedisCache, Depends(get_redis_cache)],
    session: Annotated[AsyncSession, Depends(get_session)],
    date: Annotated[date, Depends(last_date_of_trade)]
):
    cache_key = f"trading-results:{option.oil_id}:{option.delivery_type_id}:{option.delivery_basis_id}"
    cached_data = await cache.get_cached_data(cache_key)
    if cached_data:
        return json.loads(cached_data)

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
    await cache.set_cached_data(cache_key, time_left, result_data)
    
    return result
