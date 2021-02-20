import aiohttp
import asyncio
import pymongo
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

class UpdateCrawler:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36'
    }

    def __init__(self):
        self.wangyi_productkey = 0

    @staticmethod
    def wangyi_get_productkey(url):
        # 用于获取爬网易新闻评论所必要的参数
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-gpu')
        prefs = {'profile.managed_default_content_settings.images': 2, 'permissions.default.stylesheet': 2}
        options.add_experimental_option('prefs', prefs)
        options.add_argument(
            'user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36"')

        broswer = webdriver.Chrome(executable_path='C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe', chrome_options=options)
        broswer.get(url)
        product_key = broswer.find_element_by_id('post_productKey').get_attribute('value')
        broswer.close()
        return product_key

    async def wangyi_update(self, item, index):
        """
        :param item: {
            source: '网易新闻',
            docid: docid,
            url: url,
            time: time
        }
        :param index: 要更新数据的话题索引
        :return:
        """
        get_key_url = 'https://3g.163.com/touch/comment.html?docid={}'.format(item['url'].split('/')[-1][:-5])
        if self.wangyi_productkey == 0:
            self.wangyi_productkey = self.wangyi_get_productkey(get_key_url)

        comment_url = 'https://comment.api.163.com/api/v1/products/{product_key}/threads/{docid}?ibc=newswap'.format(
            product_key=self.wangyi_productkey, docid=item['url'].split('/')[-1][:-5])
        async with aiohttp.TCPConnector(limit=10, verify_ssl=False) as tc:
            async with aiohttp.ClientSession(connector=tc) as session:
                async with session.get(comment_url, headers=self.headers) as resp:
                    data = await resp.json()
                    return {'index': index, 'cmtCount': data['tcount'], 'cmtVote': data['cmtCount']}


if __name__ == '__main__':
    database_ip = 'localhost'
    database_port = 27017
    database_name = 'crawler'

    w_cmt = 1  # 网易评论权重
    w_vote = 1  # 网易点赞权重

    client = pymongo.MongoClient(database_ip, database_port)
    db = client[database_name]

    update = UpdateCrawler()
    new_data = []
    data2update = list(db['hotspot'].find())

    loop = asyncio.get_event_loop()
    tasks = []

    for idx, hotspot_item in enumerate(data2update):
        print(data2update[idx]['keywords'])
        print(data2update[idx]['new_forward_comment_like'])
        data2update[idx]['forward_comment_like'] = data2update[idx]['new_forward_comment_like']
        for one_related_data in hotspot_item['related_data']:
            source = one_related_data['source']
            if source == '网易新闻':
                tasks.append(asyncio.ensure_future(update.wangyi_update(one_related_data, idx)))
            if source == '其他':
                pass
    tasks = asyncio.gather(*tasks)
    result = loop.run_until_complete(tasks)
    for i in result:
        data2update[i['index']]['new_forward_comment_like'] += i['cmtCount'] * w_cmt + i['cmtVote'] * w_vote
    for i in data2update:
        print(i['keywords'])
        print(i['new_forward_comment_like'])
        db['hotspot'].update_one(
            {'_id': i['_id']}, {
                '$set': {
                    'forward_comment_like': i['forward_comment_like'],
                    'new_forward_comment_like': i['new_forward_comment_like']
                }
            })
