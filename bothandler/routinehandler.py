import random
import time
import asyncio
import httpx
import json
import re
import datetime
from config import config
from botmethod import *


async def get_news():
    client = httpx.AsyncClient(timeout=60)
    res = await client.get('https://v.api.aa1.cn/api/zhihu-news/index.php?aa1=xiarou')
    if not res:
        return
    res = re.findall(r'{.*}', res.text)[0]
    res = json.loads(res)
    group_list = await get_group_list()
    small_talk = await client.get('https://hub.onmicrosoft.cn/public/news?index=0&origin=zhihu')
    small_talk = small_talk.json()['data']['weiyu']
    await client.aclose()

    for group in group_list:
        await send_group_msg(group['group_id'],
                             f"早上好~ \n(˶ᵔ ᵕ ᵔ˶) \n"+small_talk)
        news = random.choice(res['news'])
        news['share_url'] = re.sub(r'\\', '', news['share_url'])
        news['thumbnail'] = re.sub(r'\\', '', news['thumbnail'])

        cq_code = f"[CQ:share,url={news['share_url']},title='{news['title']}',image={news['thumbnail']}]"
        cq_code = re.sub(r'&', '&amp;', cq_code)
        await send_group_msg(group['group_id'], cq_code)


# ( 秒数 自当日0:00点起 最高24*60*59, func, *args)
routine_list = [
    (7 * 60 * 60, get_news, ())
]

# key: task id in the list, value: day
list_latest_done = {}


async def routine_route():
    async def asc_timer(sec_in_day: float, func, *args):
        tm = int(time.time() + 8 * 60 * 60) % (24 * 60 * 60)

        if tm < sec_in_day:
            aw_time = tm - sec_in_day
        else:
            aw_time = 24 * 60 * 60 - tm + sec_in_day

        await asyncio.sleep(aw_time)
        await func(*args)

    tasklist = []
    for i in range(len(routine_list)):
        rt = routine_list[i]
        today = datetime.date.today()
        if i in list_latest_done and list_latest_done[i] == today:
            continue
        else:
            tasklist.append(asyncio.create_task(asc_timer(rt[0], rt[1], *rt[2])))
            list_latest_done[i] = today

    await asyncio.gather(*tasklist)

    if not tasklist:
        await asyncio.sleep(24 * 60 * 60 - int(time.time() + 8 * 60 * 60) % (24 * 60 * 60))

    asyncio.create_task(routine_route())
    del tasklist
