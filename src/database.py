from typing import Dict

from sqlalchemy import Column, Integer, Float, String, DATE, ForeignKey, select
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

    char_code = Column(String(5), unique=True, primary_key=True)
    name = Column(String(30))

    rate = relationship(
        "CurrencyRate",
        back_populates="currency",
        cascade='all, delete',
        passive_deletes=True,
    )

    def __repr__(self):
        return f"Currency(char_code={self.char_code!r}, name={self.name!r})"


class CurrencyRate(Base):
    __tablename__ = "currency_rate"

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(DATE, nullable=False)
    currency_id = Column(String(5), ForeignKey("currency.char_code", ondelete="CASCADE"))
    nominal = Column(Integer)
    value = Column(Float)

    currency = relationship("Currency", back_populates="rate", lazy=False)

    def __repr__(self):
        return f"CurrencyRate(date={self.date!r}, currency={self.currency.char_code!r}," \
               f"value='{self.value} for {self.nominal}')"

    def to_dict_without_date(self) -> Dict[str, str]:
        return {'char_code': self.currency.char_code,
                'nominal': f'{self.nominal!r}',
                'name': self.currency.name,
                'value': f'{self.value!r}'
                }

    def to_dict(self):
        temp = {'date': self.date.strftime('%Y-%m-%d')}
        temp.update(self.to_dict_without_date())
        return temp


async def connect_to_database():
    async with async_session_maker() as conn:
        await create_tables_if_necessary(conn)


async def create_tables_if_necessary(connection: AsyncSession):
    try:
        await connection.execute(select(Currency))
    except OperationalError:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)


async def disconnect_from_database():
    await engine.dispose()
