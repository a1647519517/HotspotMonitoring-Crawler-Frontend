from wangyi_update import UpdateCrawler
from selenium.webdriver import Chrome
from selenium.webdriver import ChromeOptions
import pymongo
import asyncio
import random
from lxml import etree

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

    header_list = [
        'user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36"',
        'user-agent="Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50"',
        'user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36"'
    ]

    # 头条部分的设置
    option = ChromeOptions()
    prefs = {"profile.managed_default_content_settings.images": 2, 'permissions.default.stylesheet': 2}
    option.add_experimental_option("prefs", prefs)
    option.add_experimental_option('excludeSwitches', ['enable-automation'])
    header = random.choice(header_list)
    option.add_argument(header)
    option.add_argument('--headless')
    option.add_argument('--disable-gpu')  # 无头浏览器
    driver = Chrome(options=option)
    num = 0

    loop = asyncio.get_event_loop()
    tasks = []
    toutiao_urls = []

    for idx, hotspot_item in enumerate(data2update):
        # print(data2update[idx]['keywords'])
        # print(data2update[idx]['new_forward_comment_like'])
        data2update[idx]['forward_comment_like'] = data2update[idx]['new_forward_comment_like']
        for one_related_data in hotspot_item['related_data']:
            source = one_related_data['source']
            # 分类更新
            if source == '网易新闻':
                tasks.append(asyncio.ensure_future(update.wangyi_update(one_related_data, idx)))
            if source == '今日头条':
                toutiao_urls.append({'url': one_related_data['url'], 'index': idx})
            else:
                pass

    # 下面两行仅能获取到网易评论，其他爬虫与网易新闻形式不一样
    tasks = asyncio.gather(*tasks)
    result = loop.run_until_complete(tasks)
    result2 = []

    # 下面是头条的
    for i in toutiao_urls:
        sum = 0
        driver.get(i['url'])
        tree = etree.HTML(driver.page_source)
        comment_num = tree.xpath('//div[@id="comment"]/@comments_count')
        # print("评论数", comment_num)
        sum = sum + int(comment_num[0])
        result2.append({'index': i['index'], 'cmtCount': sum, 'cmtVote': 0})
        # print('总的为',sum)

    # 结果加到原列表中
    for i in result:
        data2update[i['index']]['new_forward_comment_like'] += i['cmtCount'] * w_cmt + i['cmtVote'] * w_vote
    for i in result2:
        data2update[i['index']]['new_forward_comment_like'] += i['cmtCount'] * w_cmt + i['cmtVote'] * w_vote

    for i in data2update:
        # print(i['keywords'])
        # print(i['new_forward_comment_like'])
        db['hotspot'].update_one(
            {'_id': i['_id']}, {
                '$set': {
                    'forward_comment_like': i['forward_comment_like'],
                    'new_forward_comment_like': i['new_forward_comment_like']
                }
            })
