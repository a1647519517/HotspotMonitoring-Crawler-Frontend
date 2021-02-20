import aiohttp
import asyncio
import json
import re
from bs4 import BeautifulSoup


class Crawler:
    data = []
    news = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36'
    }

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
            if len(docid) < 10:
                continue
            source = data['source']
            title = data['title']
            priority = data['priority']
            url = data['url']
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
            items_list.append(item)
            print(item)
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
        a = soup.find(name='div', attrs={'class': 'page js-page on'}).contents
        for i in a:
            if i.string is not None:
                str += i.string
        return str

# 获取新闻内容
    async def get_news(self, item, table):
        async with aiohttp.TCPConnector(limit=10, verify_ssl=False) as tc:
            async with aiohttp.ClientSession(connector=tc) as session:
                html = await self.fetch(session, item['url'])
                result = await self.html_parser(html)
                new = {
                    'docid': item['docid'],
                    'content': result
                }
                table.append(new)

if __name__ == '__main__':
    urls = ['https://3g.163.com/touch/reconstruct/article/list/BBM54PGAwangning/{}-10.html'.format(i*10) for i in range(2)]

    crawler = Crawler()
    loop = asyncio.get_event_loop()
    # 获取url和一些数据
    tasks = [asyncio.ensure_future(crawler.get_urls(url, crawler.data)) for url in urls]
    tasks = asyncio.gather(*tasks)
    loop.run_until_complete(tasks)

    # 获取新闻
    tasks = [asyncio.ensure_future(crawler.get_news(item, crawler.news)) for item in crawler.data]
    tasks = asyncio.gather(*tasks)
    loop.run_until_complete(tasks)

    for i in crawler.news:
        print(i)
