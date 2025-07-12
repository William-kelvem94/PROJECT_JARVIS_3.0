"""
JARVIS 4.0 Database Configuration
SQLAlchemy async setup with SQLite
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import aiosqlite

from core.config import settings

# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL.replace("sqlite://", "sqlite+aiosqlite://"),
    echo=settings.DEBUG,
    future=True
)

# Create async session factory
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Base model class
Base = declarative_base()

async def init_db():
    """Initialize database tables"""
    async with engine.begin() as conn:
        # Import all models to ensure they're registered
        from models import user, conversation, plugin
        
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)

async def get_db() -> AsyncSession:
    """Get database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()