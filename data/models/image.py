import enum
from sqlalchemy import Column, Integer, String, DateTime, Enum, Text
from sqlalchemy.sql import func
from data.database import Base

class ContentTypesEnum(str, enum.Enum):
    jpeg = "image/jpeg"
    png = "image/png"
    gif = "image/gif"
    webp = "image/webp"

class Image(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, autoincrement=True)
    filename = Column(String(255), unique=True, nullable=False)
    file_path = Column(String(500), unique=True, nullable=False)
    content_type = Column(Enum(ContentTypesEnum), nullable=False)
    file_size = Column(Integer, nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), onupdate=func.now())
