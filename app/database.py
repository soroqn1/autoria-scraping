import datetime
from sqlalchemy import String, BigInteger, Float, DateTime, select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
import os
from dotenv import load_dotenv

load_dotenv()

engine = create_async_engine(os.getenv("DATABASE_URL"))
async_session = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass

class Car(Base):
    __tablename__ = "cars"

    url: Mapped[str] = mapped_column(String, primary_key=True)
    title: Mapped[str] = mapped_column(String)
    price_usd: Mapped[float] = mapped_column(Float)
    odometer: Mapped[int] = mapped_column(BigInteger)
    username: Mapped[str] = mapped_column(String)
    phone_number: Mapped[int] = mapped_column(BigInteger)
    image_url: Mapped[str] = mapped_column(String)
    images_count: Mapped[int] = mapped_column(BigInteger)
    car_number: Mapped[str] = mapped_column(String, nullable=True)
    car_vin: Mapped[str] = mapped_column(String, nullable=True)
    datetime_found: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)

async def init_db():
    print("Initializing database...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Database initialized.")

async def save_car(session: AsyncSession, car_data: dict) -> bool:
    stmt = select(Car).where(Car.url == car_data['url'])
    result = await session.execute(stmt)
    if result.scalar_one_or_none():
        return False
    
    new_car = Car(**car_data)
    session.add(new_car)
    return True
