import re

import httpx


class CvCrawler:
    def __init__(self, proxy: str | None = None):
        self.__proxy = proxy
        self.__header = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) \
                Chrome/109.0.0.0 Safari/537.36 Edg/109.0.1518.70',
            'sec-ch-ua-platform': "Windows",
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua': '"Not_A Brand";v="99", "Microsoft Edge";v="109", "Chromium";v="109"'
        }

    async def __get_text(self, url):
        if self.__proxy:
            client = httpx.AsyncClient(proxies={'all://': self.__proxy}, headers=self.__header)
        else:
            client = httpx.AsyncClient(headers=self.__header)

        res = await client.get(url)
        await client.aclose()
        return res.text

    async def craw_article_images(self, cv_id: int) -> list[str]:
        url = 'https://www.bilibili.com/read/cv'+str(cv_id)

        text = await self.__get_text(url)
        img_lst = re.findall(r'(?<=data-src=")[/a-z0-9.%\-]*', text, re.I)

        for i in range(len(img_lst)):
            img_lst[i] = 'https:' + img_lst[i]

        return img_lst

    async def craw_cv_list_from_readlist(self, readlist_id: int) -> list[int]:
        url = 'https://www.bilibili.com/read/readlist/rl' + str(readlist_id)
        text = await self.__get_text(url)
        cv_list = re.findall(r'(?<=\[).*(?=])', text, re.I)[0].split(',')

        cv_list = list(map(int, cv_list))
        return cv_list

    async def craw_cv_list_from_search(self, question: str) -> list[int]:
        question = re.sub(r'\s+', r'+', question)
        url = 'https://search.bilibili.com/article?keyword=' + question
        text = await self.__get_text(url)
        cv_list = re.findall(r'(?<=cv)[0-9]+', text)
        cv_list = list(map(int, cv_list))
        return cv_list
