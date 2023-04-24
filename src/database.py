from typing import AsyncGenerator

from sqlalchemy import Column, Integer, String, DATE, ForeignKey, select
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.orm import relationship
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.exc import OperationalError

from .config import DATABASE_URL


Base = declarative_base()

engine = create_async_engine(DATABASE_URL)
async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Currency(Base):
    __tablename__ = "currency"

    num_code = Column(Integer, primary_key=True)
    char_code = Column(String(10))
    name = Column(String(30))

    daily_rate = relationship("CurrencyRate", back_populates="currency")

    def __repr__(self):
        return f"Currency(num_code={self.num_code!r}, char_code={self.char_code!r})"


class CurrencyRate(Base):
    __tablename__ = "currency_rate"

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(DATE, nullable=False)
    currency_id = Column(Integer, ForeignKey("currency.num_code"))
    nominal = Column(Integer)
    value = Column(Integer)

    currency = relationship("Currency", back_populates="daily_rate")

    def __repr__(self):
        return f"{self.C}(id={self.id!r}, email_address={self.email_address!r})"


async def connect_to_database():
    async with async_session_maker() as conn:
        await create_tables_if_nessessary(conn)


async def create_tables_if_nessessary(connection: AsyncSession):
    try:
        await connection.execute(select(Currency))
    except OperationalError:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)


async def disconnect_from_database():
    await engine.dispose()
