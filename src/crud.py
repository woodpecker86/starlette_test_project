from typing import List, Dict, Union
from datetime import datetime

from sqlalchemy import select, insert, delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from .database import async_session_maker, Currency, CurrencyRate
from .cbr_data import get_cbr_data


async def get_date_rates(date: datetime) -> List[Dict[str, str]]:
    stmt = (select(CurrencyRate, Currency).join(CurrencyRate.currency)
            .where(CurrencyRate.date == date.date()))
    list_of_rates = await execute_select(stmt)
    # print(list_of_rates)
    if not list_of_rates:
        data = await get_cbr_data(date)
        await insert_data_into_database(data, date)
    return list(data)


async def execute_select(statement) -> list:
    async with async_session_maker() as session:
        response = await session.execute(statement)
        return list(response)


async def insert_data_into_database(data: List[Dict[str, str]], date: datetime) -> None:
    async with async_session_maker() as session:
        for item in data:
            currency_params = {k: v for k, v in item.items() if k in ('char_code', 'name')}
            currency = Currency(**currency_params)
            await execute_insert_statement(session, currency, currency_params)
            rate_params = {k: v for k, v in item.items() if k not in ('num_code', 'char_code', 'name')}
            rate_params['currency_id'] = currency.char_code
            rate_params['date'] = date
            rate = CurrencyRate(**rate_params)
            await execute_insert_statement(session, rate, rate_params)
        await session.commit()


async def execute_insert_statement(session: AsyncSession,
                                   table: Union[Currency, CurrencyRate],
                                   params: Dict[str, str]) -> None:
    try:
        await session.execute(insert(table.__class__).values(params))
    except IntegrityError:
        pass


async def get_currencies() -> List[str]:
    stmt = select(Currency.char_code)
    currencies = await execute_select(stmt)
    return [item[0] for item in currencies]


async def delete_currency_data(char_code: str) -> None:
    async with async_session_maker() as session:
        stmt = delete(Currency).where(Currency.char_code == char_code)
        await session.execute(stmt)
        await session.commit()


async def get_all_rates(limit: int, offset: int) -> list:
    pass

