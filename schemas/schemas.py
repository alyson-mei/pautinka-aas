from pydantic import BaseModel
from typing import Optional
from enum import Enum

class ContentTypesEnum(str, Enum):
    jpeg = "image/jpeg"
    png = "image/png"
    gif = "image/gif"
    webp = "image/webp"
    
class ImageCreate(BaseModel):
    filename: str
    file_path: str
    content_type: ContentTypesEnum
    file_size: Optional[int] = None
    description: Optional[str] = None


class ImageRead(ImageCreate):
    id: int

    class Config:
        orm_mode = True