import asyncio
import logging

from src.logging_setup import LoggerHandlerType, SetupLoggerParams, setup_logger
from src.restaurant_scraper import is_restaurant_open
from src.settings import settings
from src.telegram_notify import send_telegram_message

logger = logging.getLogger(__name__)


async def notify_when_open() -> None:
    notified = False
    while True:
        try:
            logger.info("Checking if restaurant is open")
            is_open = await is_restaurant_open(
                settings.restaurant.url,
                settings.restaurant.closed_texts,
                settings.restaurant.order_button_texts,
            )
            if is_open and not notified:
                logger.info("Notifying that the restaurant is open")
                await send_telegram_message(
                    settings.telegram.bot_token,
                    settings.telegram.chat_id,
                    settings.restaurant.message,
                )
                notified = True
            elif not is_open:
                logger.info("Restaurant is not open")
                notified = False
        except Exception:
            logger.exception("Error checking restaurant status")
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
    logger.info("Starting Restaurant notifier for '%s'", settings.restaurant.name)
    await notify_when_open()


if __name__ == "__main__":
    asyncio.run(main())
