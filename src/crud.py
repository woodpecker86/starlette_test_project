from typing import List, Dict, Union
from datetime import datetime

from sqlalchemy import select, insert, delete, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql.selectable import Select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.engine.result import ChunkedIteratorResult


from .database import async_session_maker, Currency, CurrencyRate
from .cbr_data import get_cbr_data


async def get_date_rates(date: datetime) -> List[Dict[str, str]]:
    stmt = (select(CurrencyRate).join(CurrencyRate.currency)
            .filter(CurrencyRate.date == date.date()))
    rates = await execute_statement(stmt)
    list_of_rates = [row[0].to_dict_without_date() for row in rates]
    if not list_of_rates:
        rates = await get_cbr_data(date)
        await insert_data_into_database(rates, date)
        return rates
    return list_of_rates


async def execute_statement(statement) -> ChunkedIteratorResult:
    async with async_session_maker() as session:
        response = await session.execute(statement)
        await session.commit()
        return response


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
    currencies = await execute_statement(stmt)
    return [item[0] for item in currencies]


async def delete_currency_data(char_code: str) -> int:
    row_nums = await _get_row_count(select(func.count("*"))
                                    .select_from(CurrencyRate)
                                    .where(CurrencyRate.currency_id == char_code))
    delete_stmt = delete(CurrencyRate).where(CurrencyRate.currency_id == char_code)
    await execute_statement(delete_stmt)
    return row_nums


async def get_all_rates(limit: int, offset: int) -> List[Dict[str, str]]:
    row_nums = await _get_row_count(select(func.count("*")).select_from(CurrencyRate))
    stmt = select(CurrencyRate).join(CurrencyRate.currency).order_by(CurrencyRate.date)
    if limit:
        pages = row_nums//limit
        start = min(offset, pages) * limit
        stmt = stmt.slice(start, start+limit)
    rates = await execute_statement(stmt)
    return [row[0].to_dict() for row in rates]


async def _get_row_count(stmt: Select) -> int:
    result = await execute_statement(stmt)
    return next(result)[0]
