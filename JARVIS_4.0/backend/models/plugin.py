"""
Plugin model for JARVIS 4.0
"""
from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime
from sqlalchemy.sql import func

from core.database import Base

class Plugin(Base):
    __tablename__ = "plugins"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(Text)
    version = Column(String)
    is_enabled = Column(Boolean, default=False)
    config = Column(Text)  # JSON string
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())