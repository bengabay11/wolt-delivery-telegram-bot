import asyncio
import datetime
import logging

from telegram import Bot

from src.logging_setup import LoggerHandlerType, SetupLoggerParams, setup_logger
from src.restaurant_scraper import is_restaurant_delivery_open
from src.settings import AppSettings

logger = logging.getLogger(__name__)


async def send_telegram_message(token: str, chat_id: str, message: str) -> None:
    bot = Bot(token=token)
    await bot.send_message(chat_id=chat_id, text=message)


async def check_and_notify(
    restaurant_slug: str,
    bot_token: str,
    chat_id: str,
    notification_message: str,
    operation_start_hour: int = 11,
    operation_end_hour: int = 23,
) -> None:
    try:
        now = datetime.datetime.now()
        current_hour = now.hour

        if operation_start_hour <= current_hour < operation_end_hour:
            logger.info("Checking restaurant delivery availability")
            is_delivery_open = await is_restaurant_delivery_open(restaurant_slug)
            if is_delivery_open:
                logger.info("Notifying: restaurant is available for delivery")
                await send_telegram_message(
                    bot_token,
                    chat_id,
                    notification_message,
                )
            else:
                logger.info("Restaurant is currently not available for delivery")
        else:
            logger.info(
                "Outside of operation hours (%02d:00-%02d:00), skipping check",
                operation_start_hour,
                operation_end_hour,
            )
    except Exception:
        logger.exception("Error while checking restaurant delivery status")


async def main() -> None:
    settings = AppSettings()  # type: ignore[call-arg]
    setup_logger(
        SetupLoggerParams(
            level=settings.logging.min_log_level,
            handler_types={LoggerHandlerType.STREAM, LoggerHandlerType.FILE},
            file_path=settings.logging.log_file_path,
        )
    )
    logger.info("Checking restaurant delivery status for '%s'", settings.restaurant.slug)
    await check_and_notify(
        settings.restaurant.slug,
        settings.telegram.bot_token,
        settings.telegram.chat_id,
        settings.restaurant.message,
        settings.restaurant.operation_start_hour,
        settings.restaurant.operation_end_hour,
    )


if __name__ == "__main__":
    asyncio.run(main())
