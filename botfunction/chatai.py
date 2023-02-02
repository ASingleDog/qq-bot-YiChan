import re
import httpx
from config import config


async def xiaoai(msg):
    msg = re.sub(r'\+', '加', msg)
    msg = re.sub(r'=', '等于', msg)
    msg = re.sub(r'-', '减去', msg)
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
