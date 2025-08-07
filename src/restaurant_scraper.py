import aiohttp
from bs4 import BeautifulSoup


async def is_restaurant_open(
    url: str, closed_texts: list[str], order_button_texts: list[str]
) -> bool:
    """Scrape the restaurant page and return True if the restaurant is open,
    False otherwise.
    """
    async with aiohttp.ClientSession() as session, session.get(url) as resp:
        html = await resp.text()
    soup = BeautifulSoup(html, "html.parser")
    # Heuristic: look for a button or text indicating closed/open
    for text in closed_texts:
        if soup.find(string=lambda s, t=text: s and t in s):
            return False
    # If there's an order button, it's open
    order_btn = soup.find("button", string=lambda text: text and (text in order_button_texts))
    return order_btn is not None
