import httpx
from config import config


async def send_group_msg(gid: int, msg: str):
    client = httpx.AsyncClient(timeout=30)
    res = await client.get(f"{config['url']}/send_group_msg", params={
        'group_id': gid,
        'message': msg
    })
    await client.aclose()
    return res


async def send_private_msg(uid: int, msg: str):
    client = httpx.AsyncClient(timeout=30)
    res = await client.get(f"{config['url']}/send_private_msg", params={
        'user_id': uid,
        'message': msg
    })
    await client.aclose()
    return res


# 发送群转发消息
async def send_group_forward_msg(gid: int, msgs: list[str], virt_sender: dict | None = None):
    client = httpx.AsyncClient(timeout=30)
    res = await client.post(f"{config['url']}/send_group_forward_msg", json={
        'group_id': gid,
        'messages': [
            {
                "type": "node",
                "data": {
                    "name": virt_sender['nickname'],
                    "uin": virt_sender['user_id'],
                    "content": msg
                }
            } for msg in msgs
        ]
    })
    await client.aclose()
