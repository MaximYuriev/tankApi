from db.config import settings
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from schemas.user import Base

ur_a = settings.POSTGRES_DATABASE_URL
engine_a = create_async_engine(ur_a,echo=True)
async_session = sessionmaker(
    engine_a, class_=AsyncSession, expire_on_commit=False
)
def create_tables():
    Base.metadata.drop_all(bind=engine_a)
    Base.metadata.create_all(bind=engine_a)



async def get_session() -> AsyncSession:
    async with async_session() as session:
        try:
            yield session
        finally:
            session.close