from lxml import etree
import time
from selenium.webdriver import Chrome
from selenium.webdriver import ChromeOptions
import pymongo
import random
header_list = [
        'user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36"',
        'user-agent="Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50"',
        'user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36"'
          ]

# def getData():
#     client = pymongo.MongoClient('mongodb://localhost:27017/')
#     db = client['toutiao']
#     col = db['hotspot']
#     data = col.find({}, {"related_data": 1,"forward_comment_like":1,"new_forward_comment_like":1,"_id":0})
#     print(data)
#     return data
def main():
    client = pymongo.MongoClient('mongodb://localhost:27017/')
    db = client['crawler']
    col = db['hotspot']
    data = col.find({}, {"related_data": 1, "forward_comment_like": 1, "new_forward_comment_like": 1, "_id": 1})
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'
    }
    option = ChromeOptions()
    prefs = {"profile.managed_default_content_settings.images": 2, 'permissions.default.stylesheet': 2}
    option.add_experimental_option("prefs", prefs)
    # option.add_argument("--proxy-server=http://58.253.153.50")
    option.add_experimental_option('excludeSwitches', ['enable-automation'])
    header = random.choice(header_list)
    option.add_argument(header)
    option.add_argument('--headless')
    option.add_argument('--disable-gpu')  # 无头浏览器
    driver = Chrome(options=option)
    num = 0
    comment = []
    for i in data:
        sum = 0
        print('正在下载第', num+1, '类:')
        forward_comment_like = i["new_forward_comment_like"]
        for j in range(len(i["related_data"])):
            driver.get(i["related_data"][j]["url"])
            tree = etree.HTML(driver.page_source)
            comment_num = tree.xpath('//div[@id="comment"]/@comments_count')
            print("评论数",comment_num)
            sum = sum + int(comment_num[0])
        num = num + 1
        db['hotspot'].update_one(
            {'_id': i['_id']}, {
                '$set': {
                    'forward_comment_like': forward_comment_like,
                    'new_forward_comment_like': sum
                }
            })
        print('总的为',sum)
    # test = col.find({}, {"related_data": 1, "forward_comment_like": 1, "new_forward_comment_like": 1, "_id": 1})
    # for a in test:
    #     print(a)
if __name__ == '__main__':
    main()
