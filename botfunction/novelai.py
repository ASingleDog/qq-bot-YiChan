import os

import jieba

from config import config
import re
import httpx
import random
import math
import jieba.posseg as pseg
import asyncio

template_pos_tags = ",best quality,highly detailed,\
    ultra-detailed,illustration,camel_toe,full_body,stockings, {{{masterpiece}}},{extremely detailed CG \
    unity 8k,outdoors, \
    {wallpaper},Amazing,finely detail,cinematic lighting,close-up,{{floating hair}},\
    sky,{{wind}},detailed background,beautiful detailed eyes,bright pupils,{{full body}}, dynamic pose,dynamic angle,\
    looking at viewer,detailed clothes"

template_neg_tags = ''',missing fngers,extra digt ,fewer digits,low quality,watermark, bad feet,extra fingers,
mutated hands,poorly drawn hands,fused fingers,too many fingers,bad anatomy, cropped, wort quality, low quality, normal,
quality, jpeg artifacts,signature,watermark, bad feet,mutilated,too many fingers,malformed limbs,more than 2 knee,
mutated hands,vore,pregnant,mutilated,morbid,bad proportions,missing legs,extra limbs,multiple breasts,
(mutated hands and fingers:1.5 ), (long body :1.3), (mutation, poorly drawn :1.2) , black-white, bad anatomy,
liquid tongue, disfigured, error, malformed hands, long neck, blurred, lowres, bad proportions, bad shadow,
 uncoordinated body, unnatural body, fused breasts, bad breasts, huge breasts, poorly drawn breasts, extra breasts,
 liquid breasts, heavy breasts, missing breasts, huge haunch, huge thighs, huge calf, bad hands, fused hand,
 missing hands'''


async def generate_image(pos_tag: str = "", neg_tag: str = "", width: int = 512, height: int = 768) ->str|None:
    if width * height > 512 * 768:
        return None
    header = {
        'accept': 'application/json, text/javascript',
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
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) \
                      Chrome/109.0.0.0 Safari/537.36 Edg/109.0.1518.70'
    }

    client = httpx.AsyncClient()
    session_token = await client.get(
        f"https://v1.kamiya.dev/api/user_login?token={config['kamiya.dev-token']}", headers=header)
    session_token = session_token.text
    ai_setting = {
        "pass": session_token,
        "prompt": pos_tag + template_pos_tags,
        "nprompt": neg_tag + template_neg_tags,
        "step": 28,
        "scale": 12,
        "seed": math.floor(random.random() * 1000000000),
        "sampler": "k_euler_ancestral",
        "wh": "custom",
        "resolution": f"{width}x{height}"
    }

    header['content-type'] = 'application/json'
    res = await client.post('https://v1.kamiya.dev/api/generate-image', json=ai_setting, headers=header, timeout=10)
    b64 = res.json()['output']
    # 去除冗余
    await client.aclose()
    b64 = b64[27:]
    b64 = re.sub(r'\n', '', b64)
    return 'base64://' + b64


async def novel_image(text: str, sender: dict):
    text = re.sub('，', ',', text)
    text = re.sub('（', '(', text)
    text = re.sub('）', ')', text)
    text = re.sub('【', '[', text)
    text = re.sub('】', ']', text)

    pos_tag = re.findall(r'(?<=正向标签)[a-zA-Z0-9,，{}()\[\]:\-\s]*', text)
    text = re.sub(r'正向标签[a-zA-Z0-9,，{}()\[\]:\-\s]*', '', text)
    if pos_tag:
        pos_tag = pos_tag[0]
    else:
        pos_tag = ""

    neg_tag = re.findall(r'(?<=反向标签)[a-zA-Z0-9,，{}()\[\]:\-\s]*', text)
    text = re.sub(r'反向标签[a-zA-Z0-9,，{}()\[\]:\-\s]*', '', text)
    if neg_tag:
        neg_tag = neg_tag[0]
    else:
        neg_tag = ""

    width = re.findall(r'(?<=[宽])[0-9]*', text)
    text = re.sub(r'(?<=[宽])[0-9]*', '', text)
    try:
        width = int(width[0])
    except:
        width = 512

    height = re.findall(r'(?<=[高长])[0-9]*', text)
    text = re.sub(r'(?<=[高长])[0-9]*', '', text)
    try:
        height = int(height[0])
    except:
        height = 768

    # jieba.load_userdict(re.sub(r'\\', r'/', os.getcwd()) + '/assets/dict.txt')

    nlp_res = pseg.cut(text)

    tag_list = []
    for nlp_single in nlp_res:
        tp = tuple(nlp_single)
        if tp[0] != '帮' and not re.findall('画', tp[0]) and not re.findall('ai', tp[0], re.I) \
                and tp[0] != '请' and tp[0] != '让' and tp[0] != '令' and not re.findall('名', tp[0])\
                and tp[0] != '使' and not re.findall('充', tp[0], re.I):
            if re.findall(r'n', tp[1]) or tp[1] == 'i' \
                    or tp[1] == 't' or re.findall(r'a', tp[1]) or tp[1] == 'i' or re.findall(r'v', tp[1])\
                    or tp[1] == 'f' or tp[1] == 's' or tp[1] == 'PER' or tp[1] == 'LOC' or tp[1] == 'eng':
                tag_list.append(tp[0])

    tags = ","
    client = httpx.AsyncClient()
    task_list = []
    for tag in tag_list:
        if not re.findall(r'[a-z]', tag):
            task_list.append(asyncio.create_task(
                client.get('https://v.api.aa1.cn/api/api-fanyi-yd/index.php', params={'msg': tag, 'type': 1}))
            )
        else:
            tags += tag + ','

    en_tag_list = await asyncio.gather(*task_list)

    for tag_res in en_tag_list:
        try:
            res_dic = tag_res.json()
            tags += res_dic['text'] + ','
        except:
            pass

    await client.aclose()

    print(tags + pos_tag)
    res = await generate_image(tags + pos_tag, neg_tag, width, height)
    return res
