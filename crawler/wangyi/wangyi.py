import aiohttp
# import asyncio
import json
import re
from bs4 import BeautifulSoup
# from new_singlepass import Single_Pass_Cluster
# import time
# import pymongo
# import redis

class WangyiCrawler:
    data = []
    news = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36'
    }

    def __init__(self, database, redis):
        self.db = database
        self.wangyi_news = self.db['wangyi']
        self.rdb = redis

# 获取源码
    async def fetch(self, session, url):
        async with session.get(url, headers=self.headers) as resp:
            return await resp.text(encoding='utf-8')

# 解析
    @staticmethod  # 静态方法，无需实例化即可调用
    async def parser(html):
        items_list = []
        # 正则过滤数据
        data_list = json.loads(re.findall(r'artiList\((.*)\)', html)[0])['BBM54PGAwangning']
        for data in data_list:
            docid = data['docid']
            source = data['source']
            title = data['title']
            priority = data['priority']
            url = data['url']
            if len(url) < 30:
                continue
            comment_count = data['commentCount']
            ptime = data['ptime']

            item = {
                'docid': docid,
                'source': source,
                'title': title,
                'priority': priority,
                'url': url,
                'comment_count': comment_count,
                'ptime': ptime
            }
            print(item)
            items_list.append(item)
        return items_list

# 爬取url
    async def get_urls(self, url, table):
        async with aiohttp.TCPConnector(limit=10, verify_ssl=False) as tc:
            async with aiohttp.ClientSession(connector=tc) as session:
                html = await self.fetch(session, url)
                result = await self.parser(html)
                table.extend(result)

# 解析HTML
    @staticmethod
    async def html_parser(html):
        str = ''
        soup = BeautifulSoup(html)
        try:
            a = soup.find(name='div', attrs={'class': 'page js-page on'}).contents
        except:
            return -1
        for i in a:
            if i.string is not None:
                str += i.string
        return str

# 获取新闻内容
    async def get_news(self, item, table):
        async with aiohttp.TCPConnector(limit=10, verify_ssl=False) as tc:
            async with aiohttp.ClientSession(connector=tc) as session:
                if self.rdb.exists(item['url']):
                    print('数据重复， code: 0')
                    return 0
                else:
                    html = await self.fetch(session, item['url'])
                    result = await self.html_parser(html)
                if result == -1:
                    print('数据错误，code: -1\n')
                    self.rdb.set(item['url'], -1)
                    self.rdb.expire(item['url'], 604800)
                    return -1
                elif len(result) < 120:
                    print('内容过少，code: 0\n')
                    self.rdb.set(item['url'], 0)
                    self.rdb.expire(item['url'], 604800)
                    return 0
                else:
                    new = {
                        'hotspot_data': {
                            'source': '网易新闻',
                            'docid': item['docid'],
                            'url': item['url'],
                            'time': item['ptime']
                        },
                        'content': result
                    }
                    self.wangyi_news.insert_one(new)
                    table.append(new)
                    self.rdb.set(item['url'], 1)
                    self.rdb.expire(item['url'], 604800)

# if __name__ == '__main__':
#     database_ip = 'localhost'
#     database_port = 27017
#     database_name = 'crawler'
#
#     client = pymongo.MongoClient(database_ip, database_port)
#     db = client[database_name]
#
#     pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
#     rdb = redis.StrictRedis(connection_pool=pool)
#
#     # 爬网易新闻
#     crawler = WangyiCrawler(db, rdb)
#     loop = asyncio.get_event_loop()
#     urls = ['https://3g.163.com/touch/reconstruct/article/list/BBM54PGAwangning/{}-10.html'.format(i * 10) for i in range(30)]
#     tasks = [asyncio.ensure_future(crawler.get_urls(url, crawler.data)) for url in urls]  # 爬url
#     tasks = asyncio.gather(*tasks)
#     loop.run_until_complete(tasks)
#     tasks = [asyncio.ensure_future(crawler.get_news(item, crawler.news)) for item in crawler.data]  # 爬新闻
#     tasks = asyncio.gather(*tasks)
#     loop.run_until_complete(tasks)
#
#     client.close()


