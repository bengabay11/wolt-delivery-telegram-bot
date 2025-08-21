import logging

import aiohttp

logger = logging.getLogger(__name__)


async def is_restaurant_delivery_open(slug: str, timeout: float = 8.0) -> bool:
    url = f"https://consumer-api.wolt.com/order-xp/web/v1/venue/slug/{slug}/dynamic/"
    try:
        async with (
            aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout)) as session,
            session.get(url) as response,
        ):
            response.raise_for_status()
            data = await response.json()

            venue = data.get("venue", {})
            delivery_open: bool = venue.get("delivery_open_status", {}).get("is_open")
            online: bool = venue.get("online")

            return delivery_open and online
    except Exception:
        logger.exception("Failed to get delivery status")
        return False
