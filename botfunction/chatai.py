import math
import random
import re
import time

import httpx
from config import config
import json
from botmethod import send_private_msg, send_group_msg, send_group_forward_msg
import bili_cv_crawler as blcv


async def emoji(msg):
    crawler = blcv.CvCrawler()
    cv_list = await crawler.craw_cv_list_from_readlist(528104)
    return random.choice(await crawler.craw_article_images(random.choice(cv_list)))


async def xiaoai(msg):
    msg = re.sub(r'\+', '加', msg)
    msg = re.sub(r'=', '等于', msg)
    msg = re.sub(r'-', '减去', msg)
    msg = re.sub('小爱', 'siri', msg)
    msg = re.sub(config['self-addressing'], '小爱', msg)

    # 空消息
    if re.findall(r'^\s*$', msg):
        return ''

    url = 'https://v.api.aa1.cn/api/api-xiaoai/talk.php'
    client = httpx.AsyncClient()
    try:
        res = await client.get(url, params={'msg': msg})
        res = res.text
        res = re.sub(r'小爱(同学)?', config['self-addressing'], res)
        res = re.sub(r'小米(公司)?', '', res)
    except:
        res = '咦，怎么说不出话了？\n(AI Chat Connection Error)'

    if re.findall(r'^\s*$', res):
        res = await client.get(url, params={'msg': msg, 'type': 'json'})
        try:
            res = res.json()
            assert re.findall(r'http.*', res['meta']['music']['musicUrl'])
            res = "[CQ:record,file="+res['meta']['music']['musicUrl']+']'
        except:
            res = ''

    await client.aclose()
    return res


chat_sid = {}
# (session_id, time)
chat_gid = {}

# 计算签证
def uuid() ->str:
    s = []
    hexDigits = "0123456789abcdef"
    for i in range(0, 36):
        s.append(hexDigits[math.floor(random.random() * 0x10)])
    s[14] = "4"
    s[19] = hexDigits[ord(s[19]) & 0x3 | 0x8]
    s[8] = s[13] = s[18] = s[23] = "-"
    print("".join(s))
    return "".join(s)

async def get_kamiya_token(client=httpx.AsyncClient()):
    header = {
        'accept': '*/*',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'content-type': 'application/x-www-form-urlencoded',
        'origin': 'https://www.kamiya.dev',
        'referer': 'https://www.kamiya.dev/',
        'sec-ch-ua': '"Not_A Brand";v="99", "Microsoft Edge";v="109", "Chromium";v="109"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': "Windows",
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36\
                          (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36 Edg/109.0.1518.78"
    }
    session_token = await client.get(f"https://v1.kamiya.dev/api/user_login?token=RbdStfW5YHPQFZ5E", headers=header)
    session_token = session_token.text
    return session_token


async def chatgpt(msg, *, sid=None, gid=None):
    if re.findall(r'^\s$', msg):
        return
    if not sid and not gid:
        return

    header = {
        'accept': 'text/event-stream',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'content-type': 'application/json',
        'origin': 'https://www.kamiya.dev',
        'referer': 'https://www.kamiya.dev/',
        'sec-ch-ua': '"Microsoft Edge";v="111", "Not(A:Brand";v="8", "Chromium";v="111"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': "Windows",
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36\
                      (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36 Edg/109.0.1518.78"
    }
    header['if-none-match'] = r'W/"10-oV4hJxRVSENxc/wX8+mA4/Pe4tA"'

    header2 = {
        'accept': '*/*',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'content-type': 'application/x-www-form-urlencoded',
        'Host': 'v1.kamiya.dev',
        'origin': 'https://www.kamiya.dev',
        'referer': 'https://www.kamiya.dev/',
        'sec-ch-ua': '"Microsoft Edge";v="111", "Not(A:Brand";v="8", "Chromium";v="111"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': "Windows",
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36\
                          (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36 Edg/109.0.1518.78"
    }
    header2['if-none-match'] = r'W/"10-oV4hJxRVSENxc/wX8+mA4/Pe4tA"'

    client = httpx.AsyncClient()

    if sid:
        if sid not in chat_sid:
            chat_sid[sid] = (await get_kamiya_token(), uuid())
        elif httpx.get(f'https://v1.kamiya.dev/api/pass_check?pass={chat_sid[sid][0]}', headers=header2).status_code >= 400:
            chat_sid[sid] = (await get_kamiya_token(), chat_sid[sid][1])
        session_token = chat_sid[sid][0]
        auth = chat_sid[sid][1]

    else:
        if gid not in chat_gid:
            chat_gid[gid] = (await get_kamiya_token(), uuid())
        elif httpx.get(f'https://v1.kamiya.dev/api/pass_check?pass={chat_gid[gid][0]}', headers=header2).status_code > 400:
            chat_gid[gid] = (await get_kamiya_token(), chat_gid[gid][1])
        session_token = chat_gid[gid][0]
        auth = chat_gid[gid][1]

    async with client.stream('POST', 'https://v1.kamiya.dev/api/openai/conversation', json={
        'pass': session_token,
        'prompt': msg,
        # 'conversation_id': auth
    }, headers=header, timeout=1000, cookies={"conversation_id": auth}) as r:
        async for line in r.aiter_lines():
            try:
                # print(line[6:])
                res_text = json.loads(line[6:])
                res_text = res_text['full_content']
            except Exception as e:
                print(e)

    await client.aclose()
    if sid:
        pre_len = 0
        while pre_len < len(res_text):
            await send_private_msg(sid, res_text[pre_len:min(len(res_text), pre_len+200)])
            pre_len = min(len(res_text), pre_len + 200)

    else:
        pre_len = 0
        txt = []
        while pre_len < len(res_text):
            txt.append(res_text[pre_len:min(len(res_text), pre_len + 200)])
            pre_len = min(len(res_text), pre_len + 200)

        await send_group_forward_msg(gid, txt, virt_sender={
            'nickname': '伊酱 智慧魔导',
            'user_id': config['qq']
        })

