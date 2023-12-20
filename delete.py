import asyncio
from dotenv import load_dotenv
import os
from telegram import Bot
from constant import *

load_dotenv()
BOTTOKEN = os.getenv("BOTTOKEN")
print(BOTTOKEN)
bot = Bot(BOTTOKEN)

chat_id = 587166435


async def delete():
    result = await bot.send_message(chat_id=chat_id, text=REJECTED)
    print('chat_id', chat_id)
    print(result.message_id)
    await bot.delete_message(chat_id=chat_id, message_id=result.message_id)
    for i in range(result.message_id, 0, -1):
        try:
            await bot.delete_message(chat_id=chat_id, message_id=i)
        except:
            print(f'{i}')

if __name__ == "__main__":
    asyncio.run(delete())
# async bot.delete_message(chat_id, message_id, *, read_timeout=None, write_timeout=None, connect_timeout=None, pool_timeout=None, api_kwargs=None)
