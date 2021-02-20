from lxml import etree
import time
from selenium.webdriver import Chrome
from selenium.webdriver import ChromeOptions
#导入期望场景类
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
desired_capabilities = DesiredCapabilities.CHROME
import pymongo
import re
import random
import requests
url = 'https://www.toutiao.com/'
base_url = 'https://www.toutiao.com/i'
header_list = [
        'user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36"',
        'user-agent="Mozilla/5.0 (Windows NT 6.1; WOW64; rv:6.0) Gecko/20100101 Firefox/6.0"',
        'user-agent="Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/14.0.835.163 Safari/535.1"',
        'user-agent="Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50"',
        'user-agent="Mac OS X on Intel x86 or x86_64 Mozilla/5.0 (Macintosh; Intel Mac OS X x.y; rv:10.0) Gecko/20100101 Firefox/10.0"'
          ]
#请求数据
def getdata(url, base_url):
    option = ChromeOptions()
    option.add_experimental_option('excludeSwitches', ['enable-automation'])
    option.add_argument(
        'user-agent="Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Mobile Safari/537.36"')
    option.add_argument('--headless')
    option.add_argument('--disable-gpu') #无头浏览器
    driver = Chrome(options=option)
    driver.get(url)
    driver.implicitly_wait(3)
    driver.find_element_by_xpath('//*[@id="promoBannerIndex"]/a[2]').click()
    time.sleep(3)
    driver.find_element_by_xpath('//*[@id="indexContainer"]/div/div[1]/div[2]/a[3]').click()
    time.sleep(3)
    # time.sleep(3000)
    for i in range(2):
        driver.execute_script('window.scrollTo(0, document.body.scrollHeight)')
        # print("下滑",i+1,"页")
        driver.implicitly_wait(3)
    tree = etree.HTML(driver.page_source)
    #获取相应链接
    gid_lists = tree.xpath('//div[@class="list_content"]/section/@data-item-id')
    #获取文章内容
    # print("新闻数为",len(gid_lists))
    driver.quit()
    return gid_lists
# 破解反爬
def addCookie(url):
    ua = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36'
    headers = {
        "User-Agent": ua,
    }
    s = requests.Session()
    resp = s.get(url, headers=headers)
    resp_cookie = resp.cookies.get_dict()
    if resp_cookie.get('__ac_nonce','none') == 'none':
        return 'error'
    x = resp_cookie['__ac_nonce']
    data = {
        "cookie": x
    }
    r = requests.post('http://121.40.96.182:4006/get_sign', data=data)
    __ac_signature = r.json()['signature']
    Cookie = '__ac_nonce=' + x + '; ' + '__ac_signature=' + __ac_signature
    headers.update(
        {
            "Cookie": Cookie
        }
    )
    resp = s.get(url=url, headers=headers).text
    return resp
def saveData(data):
    client = pymongo.MongoClient('mongodb://localhost:27017/')
    db = client['toutiao']
    col = db['red_news']
    for index in range(len(data)):
        col.insert_one(data[index])
        # print(index,"已经加入到数据库")

#主函数
def main(url, base_url):
    data = []
    s_url = []
    gid_lists = getdata(url, base_url)
    #合成手机端新闻内容链接
    for j in range(len(gid_lists)):
        source_url = base_url + gid_lists[j] + '/'
        s_url.append(source_url)
    #selenuim配置
    option = ChromeOptions()
    prefs = {"profile.managed_default_content_settings.images": 2, 'permissions.default.stylesheet': 2}
    option.add_argument(
        'user-agent="Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Mobile Safari/537.36"')
    option.add_experimental_option("prefs", prefs)
    option.add_experimental_option('excludeSwitches', ['enable-automation'])
    header = random.choice(header_list)
    option.add_argument(header)
    # 无头浏览器
    option.add_argument('--headless')
    option.add_argument('--disable-gpu')
    driver = Chrome(options=option)
    j = 0
    last_content = ""
    i = 0
    repeat_num = 0
    #循环遍历链接获取文章内容及时间
    while i < len(s_url):
        # print('正在下载第', i + 1, '个题目:')
        # print(s_url[i])
        driver.get(s_url[i])
        # 隐性等待，最长等5秒
        driver.implicitly_wait(5)
        tree = etree.HTML(driver.page_source)
        page_list = ''
        #文章p列表
        page_list = tree.xpath('//article//p//text()')
        #新闻时间列表
        ttime = tree.xpath('//div[@class="article-sub"]/span[last()]/text()')
        #过滤视频内容
        if ttime:
            # print("时间",ttime)
            content = ''
            for p in page_list:
                content = content + p
            # print(content)
            # 防止重复，重复次数最大不能超过5
            if last_content==content:
                # print("重复")
                repeat_num = repeat_num+1
                if repeat_num > 5:
                    i=i+1
                    repeat_num = 0
                continue
            if last_content!=content:
                repeat_num = 0
            # 判断文章内容是否为空，如果为空则不加入数据库
            if content.strip()== '':
                i=i+1
                continue
            new = {
                'hotspot_data': {
                    'source': '今日头条',
                    'docid': gid_lists[i],
                    'url': s_url[i],
                    'time': ttime[0]
                },
                'content': content
            }
            data.append(new)
            # print('下载成功', content)
            data[j]['content'] = content
            last_content = content
            j = j + 1
        i=i+1
    # print(data)
    driver.quit()
    # print("finish")
    saveData(data)
if __name__ == '__main__':
    main(url, base_url)
