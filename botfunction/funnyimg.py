from bili_cv_crawler import CvCrawler
import random
import math


async def funny_image():
    crawler = CvCrawler()
    cv_list = await crawler.craw_cv_list_from_readlist(285503)
    imgs_from_one = await crawler.craw_article_images(random.choice(cv_list))
    return random.choice(imgs_from_one)


async def cxk_img():
    crawler = CvCrawler()
    cv_list = await crawler.craw_cv_list_from_readlist(608787)
    imgs_from_one = await crawler.craw_article_images(random.choice(cv_list))
    return random.choice(imgs_from_one)


async def search_img(question: str):
    crawler = CvCrawler()
    cv_list = await crawler.craw_cv_list_from_search(question+'+图')
    if cv_list:
        imgs_from_one = await crawler.craw_article_images(
            random.choice(cv_list[0: len(cv_list) // 3])
        )
        if imgs_from_one:
            return random.choice(imgs_from_one)
        else:
            return None
    else:
        return None

