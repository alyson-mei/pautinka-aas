import asyncio
import logging
import os
from telethon import TelegramClient
from telethon.tl.types import DocumentAttributeAnimated
from config import settings

logger = logging.getLogger("download")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

api_id = settings.TELEGRAM_API_ID
api_hash = settings.TELEGRAM_API_HASH
channel_username = settings.CHANNEL_USERNAME
images_path = settings.IMAGE_PATH
texts_path = settings.TEXT_PATH
session_path = settings.SESSION_PATH
limit = settings.DOWNLOAD_LIMIT

client = TelegramClient(session_path, api_id, api_hash,
                        device_model = "iPhone 13 Pro Max",
                        system_version = "14.8.1",
                        app_version = "8.4",
                        lang_code = "en",
                        system_lang_code = "en-US")

def is_telegram_gif(document):
    if document is None:
        return False
    return any(isinstance(attr, DocumentAttributeAnimated) for attr in document.attributes)

async def download_images(limit=limit):
    logger.info("Starting download...")

    os.makedirs(images_path, exist_ok=True)
    count = 0

    async for message in client.iter_messages(channel_username, limit=limit):
        file_path = None
        filename = None

        if message.photo:
            filename = f"{message.id}.jpg"
            file_path = os.path.join(images_path, filename)

        elif is_telegram_gif(message.document):
            filename = f"{message.id}.mp4"  # Telegram GIF-as-video
            file_path = os.path.join(images_path, filename)

        if file_path:
            if os.path.exists(file_path):
                logger.info(f"Skipping {filename}, already exists.")
                continue

            try:
                await client.download_media(message, file=file_path)
                logger.info(f"Downloaded {filename}")
                count += 1
                await asyncio.sleep(2)
            except Exception as e:
                logger.warning(f"Failed to download {filename}: {e}")

    logger.info(f"Downloaded {count} media files")

async def download_texts(limit=limit):
    logger.info("Starting message download...")

    os.makedirs(texts_path, exist_ok=True)
    messages_file = os.path.join(texts_path, "messages.txt")
    count = 0

    # Keep track of already saved message IDs to avoid duplicates
    existing_ids = set()
    if os.path.exists(messages_file):
        try:
            with open(messages_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip() and ':' in line:
                        # Extract message ID from existing entries if needed
                        pass
        except Exception as e:
            logger.warning(f"Could not read existing messages file: {e}")

    with open(messages_file, 'a', encoding='utf-8') as f:
        async for message in client.iter_messages(channel_username, limit=limit):
            if message.text and message.id not in existing_ids:
                try:
                    # Simple format: timestamp + text
                    content = f"{message.date}: {message.text}\n"
                    f.write(content)
                    f.flush()  # Ensure it's written immediately
                    
                    existing_ids.add(message.id)
                    logger.info(f"Saved message {message.id}")
                    count += 1
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    logger.warning(f"Failed to save message {message.id}: {e}")

    logger.info(f"Saved {count} messages to messages.txt")

async def main(limit=limit, ask_on_start=True):
    if ask_on_start:
        print("What would you like to download?")
        print("1. Images and GIFs only")
        print("2. Texts only")
        print("3. Both images and texts")
        
        choice = input("Enter your choice (1-3): ").strip()
        
        if choice not in ['1', '2', '3']:
            logger.info("Invalid choice. Download cancelled.")
            return
        
        user_input = input("Do you want to start downloading? (yes/no): ").strip().lower()
        if user_input not in ['yes', 'y']:
            logger.info("Download cancelled by user.")
            return

    async with client:
        if not ask_on_start or choice == '1':
            await download_images(limit=limit)
        elif choice == '2':
            await download_texts(limit=limit)
        elif choice == '3':
            await download_images(limit=limit)
            await download_texts(limit=limit)

if __name__ == '__main__':
    asyncio.run(main())