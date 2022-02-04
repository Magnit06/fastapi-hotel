from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from config import get_config

conf = get_config()

engine = create_async_engine(conf.SQLALCHEMY_DB_URI, echo=True)


async def get_session() -> AsyncSession:
    async_session = sessionmaker(bind=engine,
                                 class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session
