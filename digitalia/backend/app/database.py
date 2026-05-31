import os
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError(
        "CRÍTICO: A variável de ambiente DATABASE_URL não está definida. "
        "Defina-a no arquivo .env antes de iniciar a aplicação."
    )

# Assegurar uso do driver asyncpg
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

# Criação do engine assíncrono
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True
)

# Criador de sessões assíncronas
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async_session = AsyncSessionLocal

# Dependency generator para injeção de dependência no FastAPI
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
