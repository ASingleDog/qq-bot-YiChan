import random
import re
import asyncio
import time

from botmethod import *
from botfunction import *
from config import config


async def msg_router(data: dict):
    if data['message_type'] == 'group':
        return await group_msg_handler(data['raw_message'], data['group_id'], data['sender'])
    else:
        return await private_msg_handler(data['raw_message'], data['sender'])


async def private_msg_handler(msg: str, sender: dict):
    if re.findall('备忘录', msg):
        return {'reply': '备忘录功能升级维护中，预计将会迁移至伊酱姐妹bot，之后再来看看吧~'}
    return {'reply': await xiaoai(msg)}


async def group_msg_handler(msg: str, gid: int, sender: dict):
    # super Function with #
    if re.findall(r'#', msg):
        msg = re.sub(r'#', '', msg)
        if re.findall(r'ai', msg, re.I) and re.findall(r'画', msg):
            asyncio.create_task(novelai_handler(msg, gid, sender))
            return {'reply': f"[CQ:at,qq={sender['user_id']}]魔法之书正在解析，绘图魔法尝试构建……"}

    # normal Function
    if re.findall(r'kun', msg, re.I) or re.findall(r'我家哥哥', msg) or \
            re.findall(r'你干嘛', msg) or re.findall(r'小黑子', msg) or re.findall(r'只因', msg)\
            or re.findall(r'鸡', msg) or re.findall(r'唱? *跳? *rap *篮球', msg):
        asyncio.create_task(cxkimg_handler(msg, gid, sender))
        return {}

    if re.findall(r'^w{3,}$', msg) or re.findall(r'沙雕', msg) or msg == '草' \
            or msg == '艹' or re.findall(r'^哈{2,}$', msg) or re.findall(r'^h{2,}$', msg):
        asyncio.create_task(funnyimg_handler(msg, gid, sender))
        return {'reply': f"草元素被不经意间生成了……(草图抓取中)"}

    if re.findall(r'((?<=(?:没有|有无|来份|来张)).*(?=的?(?:图|表情)))|((?<=有).*?(?=的?图(?:[吗嘛])))', msg, re.I):
        asyncio.create_task(searchimg_handler(msg, gid, sender))
        return {'reply': f"[CQ:at,qq={sender['user_id']}]我来帮你找一份吧~(搜索抓取中)"}

    # greeting
    if re.findall(r'早安', msg) or (len(msg) < 6 and re.findall(r'早', msg)):
        return {'reply': "再睡会儿吧~"}

    if re.findall(r'晚安', msg):
        return {'reply': "还早呢,再玩会儿~"}

    # Function with wake words
    if re.findall(r'#', msg) or re.findall(str(config['self-addressing']), msg) \
            or re.findall(rf"\[CQ:at,qq={config['qq']}", msg):
        msg = re.sub(r'#', '', msg)
        msg = re.sub(rf"\[CQ:at,qq={config['qq']}]", '', msg)
        msg = re.sub(str(config['self-addressing']) + ',?', '', msg)
        # go chatting
        return {'reply': await chat_handler(msg, gid, sender)}

    # uncaught message
    return {'reply': await uncaughtmsg_handler(msg, gid, sender)}


async def novelai_handler(msg: str, gid: int, sender: dict):
    res = await novel_image(msg, sender)
    if res:
        await send_group_forward_msg(gid, [
            f"[CQ:at,qq={sender['user_id']},name={sender['nickname']}]绘图魔法构建完成~",
            f"[CQ:image,file={res}]"
        ], virt_sender={
            'nickname': '伊酱 绘图魔导',
            'user_id': config['qq']
        })
    else:
        await send_group_msg(gid, f'欸，你…你确定绘图魔法的术语吟唱没错嘛？……或者图片太大啦？')


async def funnyimg_handler(msg: str, gid: int, sender: dict):
    url = await funny_image()
    await send_group_msg(gid, f'[CQ:image,file={url}]')


async def cxkimg_handler(msg: str, gid: int, sender: dict):
    url = await cxk_img()
    await send_group_msg(gid, f'[CQ:image,file={url}]')


async def searchimg_handler(msg: str, gid: int, sender: dict):
    question = re.findall(r'((?<=(?:没有|有无|来份|来张)).*(?=的?(?:图|表情)))|((?<=有).*?(?=的?图(?:[吗嘛])))', msg)
    if question[0][0]:
        question = question[0][0]
    else:
        question = question[0][1]
    res = await search_img(question)
    if not res:
        await send_group_msg(gid, f"[CQ:at,qq={sender['user_id']}]寻图魔法查找失败……(不过你可以再试几次)")
    else:
        await send_group_msg(gid, f"[CQ:image,file={res}]")


# 用来+1起哄带动气氛的, Key为gid, Value为消息内容
latest_words = {}
# 判断刚刚有没有闲聊
chat_is_on = {}


async def uncaughtmsg_handler(msg: str, gid: int, sender: dict) -> str:
    if gid in latest_words:
        if latest_words[gid] == msg:
            if random.randint(0, 100) >= 30:
                return msg

    latest_words[gid] = msg

    global chat_is_on

    # 判断是否在聊。第三个条件为判断是否超时五分钟
    if gid not in chat_is_on or not chat_is_on[gid] or time.time() - chat_is_on[gid] > 300:
        if random.randint(0, 100) >= 3:
            return ''

    # 防止每个问题都回
    if random.randint(0, 100) < 20:
        return ''

    ret_msg = await chat_handler(msg, gid, sender)
    # 不是@的话不明白意思就不要回答
    if re.findall(r'(听[清懂])|(不支持)|(知识盲区)|(其他)|(再说)|(慢点说)|(听到了?一点)', ret_msg):
        return ''

    return ret_msg


async def chat_handler(msg: str, gid: int, sender: dict) -> str:
    latest_words[gid] = msg
    global chat_is_on
    msg = re.sub(r'\[CQ.*]', '', msg)

    # 判断是否被手动退出聊天
    if re.findall(r'(不是[和跟叫说]你)|(没[和跟叫说]你)|(滚)|(爬)|(一边(呆着)?去)|(别掺和)|(退出聊天)|((不是|没)谈论你)', msg):
        exit_words = [f"对不起，{config['self-addressing']}这就走，伊酱下次会做个听话的乖孩子的……",
                      f"对不起，{config['self-addressing']}这就离开，请不要讨厌伊酱……"]
        chat_is_on[gid] = False
        return random.choice(exit_words)

    chat_is_on[gid] = time.time()
    # 小概率关掉，不能一直聊
    if random.randint(0, 100) < 10:
        chat_is_on[gid] = False
    return await xiaoai(msg)


