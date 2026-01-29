import asyncio
from sqlalchemy import select, func
from app.database import async_session, Car, init_db


async def check_database():
    print("="*60)
    print("Checking database contents...")
    print("="*60)
    
    await init_db()
    
    async with async_session() as session:
        result = await session.execute(select(func.count(Car.url)))
        total = result.scalar()
        print(f"\nTotal cars in database: {total}")
        
        if total > 0:
            # Останні 5 записів
            result = await session.execute(
                select(Car).order_by(Car.datetime_found.desc()).limit(5)
            )
            cars = result.scalars().all()
            
        
        if total > 0:
            result = await session.execute(
                select(Car).order_by(Car.datetime_found.desc()).limit(5)
            )
            cars = result.scalars().all()
            
            print(f"\nLast {len(cars)} cars added:")
            print("-"*60)
            for i, car in enumerate(cars, 1):
                print(f"\n{i}. {car.title}")
                print(f"   URL: {car.url}")
                print(f"   Price: ${car.price_usd}")
                print(f"   Odometer: {car.odometer} km")
                print(f"   Username: {car.username}")
                print(f"   Phone: {car.phone_number}")
                print(f"   Car number: {car.car_number}")
                print(f"   VIN: {car.car_vin}")
                print(f"   Added: {car.datetime_found}")
        
        print("\n" + "="*60)


if __name__ == "__main__":
    asyncio.run(check_database())
