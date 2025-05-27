from TelegramBot.Bot import start_bot
from API.main import start_server
import DB
import API
import asyncio
async def main():
    await asyncio.gather(start_bot(), start_server())

if __name__ == "__main__":
    asyncio.run(main())