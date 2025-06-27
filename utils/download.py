import asyncio
import logging
from telethon import TelegramClient
from config import settings
import os

logger = logging.getLogger("download")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

api_id = settings.TELEGRAM_API_ID
api_hash = settings.TELEGRAM_API_HASH
channel_username = settings.CHANNEL_USERNAME
download_path = settings.DOWNLOAD_PATH
limit = settings.DOWNLOAD_LIMIT

client = TelegramClient("sessions/pautinka", api_id, api_hash)

async def download_images(limit=limit):
    logger.info("Starting download...")

    try:
        await client.start()
        if not os.path.exists(download_path):
            os.makedirs(download_path)

        count = 0
        async for message in client.iter_messages(channel_username, limit=limit):
            if message.photo:
                file_path = await client.download_media(message.photo, file=download_path)
                if file_path and os.path.exists(file_path):
                    os.remove(file_path)
                    await client.download_media(message.photo, file=file_path)
                count += 1
                await asyncio.sleep(1) 
    except Exception as e:
        logger.error(f"Failed to download images: {e}")        
    
    logger.info(f"Downloaded {count} images")

async def main(ask_on_start=True):
    if ask_on_start:
        user_input = input("Do you want to start downloading images? (yes/no): ").strip().lower()
        if user_input != 'yes':
            logger.info("Download cancelled by user.")
            return
    with client:
        await download_images()

if __name__ == '__main__':
    asyncio.run(main())
