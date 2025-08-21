import asyncio
import logging

from telegram import Bot

from src.logging_setup import LoggerHandlerType, SetupLoggerParams, setup_logger
from src.restaurant_scraper import is_restaurant_delivery_open
from src.settings import settings

logger = logging.getLogger(__name__)


async def send_telegram_message(token: str, chat_id: str, message: str) -> None:
    bot = Bot(token=token)
    await bot.send_message(chat_id=chat_id, text=message)


async def notify_when_open() -> None:
    notified = False
    while True:
        try:
            logger.info("Checking restaurant delivery availability")
            is_delivery_open = await is_restaurant_delivery_open(settings.restaurant.slug)
            if is_delivery_open and not notified:
                logger.info("Notifying: restaurant is available for delivery")
                await send_telegram_message(
                    settings.telegram.bot_token,
                    settings.telegram.chat_id,
                    settings.restaurant.message,
                )
                notified = True
            elif not is_delivery_open:
                logger.info("Restaurant is currently not available for delivery")
                notified = False
        except Exception:
            logger.exception("Error while checking restaurant delivery status")
        logger.info("Going to sleep for %d seconds", settings.restaurant.check_interval_seconds)
        await asyncio.sleep(settings.restaurant.check_interval_seconds)


async def main() -> None:
    setup_logger(
        SetupLoggerParams(
            level=settings.logging.min_log_level,
            handler_types={LoggerHandlerType.STREAM, LoggerHandlerType.FILE},
            file_path=settings.logging.log_file_path,
        )
    )
    logger.info("Starting Restaurant notifier for '%s'", settings.restaurant.slug)
    await notify_when_open()


if __name__ == "__main__":
    asyncio.run(main())
