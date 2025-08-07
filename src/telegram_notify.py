from telegram import Bot


async def send_telegram_message(token: str, chat_id: str, message: str) -> None:
    bot = Bot(token=token)
    await bot.send_message(chat_id=chat_id, text=message)
