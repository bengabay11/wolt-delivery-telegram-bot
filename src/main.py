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


async def notify_when_open(
    restaurant_slug: str,
    bot_token: str,
    chat_id: str,
    notification_message: str,
    check_interval_seconds: int = 60 * 15,
    sleep_after_check_seconds: int = 60 * 60 * 2,
    operation_start_hour: int = 11,
    operation_end_hour: int = 23,
) -> None:
    while True:
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
                    time_to_sleep = sleep_after_check_seconds
                else:
                    logger.info("Restaurant is currently not available for delivery")
                    time_to_sleep = check_interval_seconds
            else:
                # Calculate time until next operation window
                next_check = now.replace(hour=operation_start_hour, minute=0, second=0)
                if current_hour > operation_end_hour:
                    # It's after operation hours, sleep until tomorrow's start hour
                    next_check += datetime.timedelta(days=1)

                time_to_sleep = int((next_check - now).total_seconds())
                logger.info(
                    "Outside of operation hours (%02d:00-%02d:00), sleeping until %s",
                    operation_start_hour,
                    operation_end_hour,
                    next_check.strftime("%Y-%m-%d %H:%M:%S"),
                )
        except Exception:
            logger.exception("Error while checking restaurant delivery status")
            time_to_sleep = check_interval_seconds

        logger.info("Going to sleep for %d seconds", time_to_sleep)
        await asyncio.sleep(time_to_sleep)


async def main() -> None:
    settings = AppSettings()  # type: ignore[call-arg]
    setup_logger(
        SetupLoggerParams(
            level=settings.logging.min_log_level,
            handler_types={LoggerHandlerType.STREAM, LoggerHandlerType.FILE},
            file_path=settings.logging.log_file_path,
        )
    )
    logger.info("Starting Restaurant notifier for '%s'", settings.restaurant.slug)
    await notify_when_open(
        settings.restaurant.slug,
        settings.telegram.bot_token,
        settings.telegram.chat_id,
        settings.restaurant.message,
        settings.restaurant.check_interval_seconds,
        settings.restaurant.sleep_after_check_seconds,
        settings.restaurant.operation_start_hour,
        settings.restaurant.operation_end_hour,
    )


if __name__ == "__main__":
    asyncio.run(main())
