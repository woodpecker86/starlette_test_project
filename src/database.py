from sqlalchemy import Column, Integer, String, DATE, ForeignKey, select
from sqlalchemy.orm import declarative_base, sessionmaker, backref
from sqlalchemy.orm import relationship
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.exc import OperationalError

from .config import DATABASE_URL


Base = declarative_base()

engine = create_async_engine(DATABASE_URL)
async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Currency(Base):
    __tablename__ = "currency"

    char_code = Column(String(10), unique=True, primary_key=True)
    name = Column(String(30))

    rate = relationship(
        "CurrencyRate",
        back_populates="currency",
        cascade="all, delete",
        passive_deletes=True,
    )

    def __repr__(self):
        return f"Currency(char_code={self.char_code!r}, name={self.name!r})"


class CurrencyRate(Base):
    __tablename__ = "currency_rate"

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(DATE, nullable=False)
    currency_id = Column(Integer, ForeignKey("currency.char_code", ondelete="CASCADE"))
    nominal = Column(Integer)
    value = Column(Integer)

    currency = relationship("Currency", back_populates="rate")

    def __repr__(self):
        return f"CurrencyRate(date={self.date!r}, currency={self.currency.char_code!r}," \
               f"value='{self.value} for {self.nominal}')"


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
