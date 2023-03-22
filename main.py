import asyncio

from fastapi import FastAPI, Request
from bothandler import *
app = FastAPI()


@app.post("/")
async def root(req: Request):
    data = await req.json()
    res = await req_router(data)
    if res:
        return res
    else:
        return {}


async def req_router(data: dict):
    if data['post_type'] == 'message':
        return await msg_router(data)
    elif data['post_type'] == 'request':
        return {'approve': True}


# asyncio.create_task(routine_route())
