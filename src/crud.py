from typing import List, Dict, Union
from datetime import datetime

from sqlalchemy import select, insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from .database import async_session_maker, Currency, CurrencyRate
from .cbr_data import get_cbr_data


async def get_date_rate(date: datetime) -> List[Dict[str, str]]:
    async with async_session_maker() as session:
        stmt = select(CurrencyRate, Currency).join(CurrencyRate.currency_id).where(CurrencyRate.date == date.date())
        response = await session.execute(stmt)
    if not list(response):
        data = await get_cbr_data(date)
        await insert_data_into_database(data, date)
    return list(data)


async def insert_data_into_database(data: List[Dict[str, str]], date: datetime) -> None:
    async with async_session_maker() as session:
        for item in data:
            currency_params = {k: v for k, v in item.items() if k in ('num_code', 'char_code', 'name')}
            await execute_insert_statement(session, Currency, currency_params)
            rate_params = {k: v for k, v in item.items() if k not in ('num_code', 'char_code', 'name')}
            rate_params['currency_id'] = item['num_code']
            rate_params['date'] = date
            await execute_insert_statement(session, CurrencyRate, rate_params)
        await session.commit()


async def execute_insert_statement(session: AsyncSession,
                            table: Union[Currency, CurrencyRate],
                            params: Dict[str, str]) -> None:
    try:
        await session.execute(insert(table).values(params))
    except IntegrityError:
        pass
