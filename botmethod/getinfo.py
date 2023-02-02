import httpx
from config import config


async def get_group_list():
    client = httpx.AsyncClient()
    res = await client.get(f"{config['url']}/get_group_list")
    res = res.json()['data']
    await client.aclose()
    return res
