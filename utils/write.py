import asyncio
import logging
from pathlib import Path
from mimetypes import guess_type

from data.repository import RepositoryFactory
from data.models.image import Image, ContentTypesEnum
from data.database import get_db
from data.db_init import init_db
from config import settings

logger = logging.getLogger("write")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def add_images(repo, folder: str = settings.DOWNLOAD_PATH):
    logger.info("Adding images to database")
    
    folder_path = Path(folder)
    image_dicts = []

    try:

        for file in folder_path.iterdir():
            if file.is_file():
                content_type, _ = guess_type(file)
                stat = file.stat()

                try:
                    content_type_enum = ContentTypesEnum(content_type)
                except ValueError:
                    logger.warning(f"Unsupported content type: {content_type} for file {file.name}")
                    continue

                image_dicts.append({
                    "filename": file.name,
                    "file_path": str(file),
                    "content_type": content_type_enum,
                    "file_size": file.stat().st_size,
                    "description": None,
                })

    except Exception as e:
        logger.error(f"Failed to add images: {e}")
        
    await repo.create(image_dicts)

async def main():
    await init_db()
    async for session in get_db():
        repo = RepositoryFactory(session).get_repository(Image)
        await add_images(repo)

if __name__ == "__main__":
    asyncio.run(main())