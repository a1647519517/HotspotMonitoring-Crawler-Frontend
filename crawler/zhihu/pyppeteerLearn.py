import asyncio
from pyppeteer import launch
import aiohttp
import pymongo
import jieba
import jieba.analyse as analyse
import collections
import time
from textrank4zh import TextRank4Keyword, TextRank4Sentence
import re

search_url = 'https://www.zhihu.com/search?range=1w&type=content&q='
get_answers_by_id_url = 'https://www.zhihu.com/api/v4/questions/{id}/answers?include=data[*].comment_count,content,editable_content,voteup_count&limit=20&offset={offset}&platform=desktop&sort_by=updated'
cookies = {
    'z_c0': '2|1:0|10:1586419379|4:z_c0|80:MS4xR2NUakR3QUFBQUFtQUFBQVlBSlZUYk1rZkY4Q1NFMVFKX2hmV0xvRXZpNmdxLUVPcnZ1Z2ZnPT0=|3d209a9dbad2de0a571ddf85e0420385e06ae07072d1d4cc01a935f6112ecf1d',
    # 'domain': '.zhihu.com',
    # 'path': '/'
}
mongo_client = pymongo.MongoClient('mongodb://localhost:27017/')
db = mongo_client['zhihu']
col = db['zhihu']


async def intercept_request(req):
    if req.resourceType in ["image", "media", "websocket", "stylesheet", "font"]:
        await req.abort()
    else:
        await req.continue_()


async def get_answers(url, client):
    print(url)
    await asyncio.sleep(2)
    resp = await client.get(url)
    a = await resp.json()
    if a['paging']['is_end'] is False:
        return a['data']
    else:
        return 0


def html_wash(txt):
    # string = re.findall('[\u3002\uff1b\uff0c\uff1a\u201c\u201d\uff08\uff09\u3001\uff1f\u300a\u300b\u4e00-\u9fa5]',txt)
    return re.sub(r'</?\w+[^>]*>', '', txt)


async def search():
    browser = await launch({
        'headless': False,
        'executablePath': 'C:\\Users\\16475\\AppData\\Local\\pyppeteer\\pyppeteer\\local_chromium\\575458\\chrome-win32\\chrome.exe'
    })
    page = await browser.newPage()
    await page.setViewport(viewport={'width': 1280, 'height': 800})
    await page.setJavaScriptEnabled(enabled=True)
    await page.setUserAgent(
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36'
    )
    await page.setCookie({
        "name": 'z_c0',
        'value': '2|1:0|10:1586419379|4:z_c0|80:MS4xR2NUakR3QUFBQUFtQUFBQVlBSlZUYk1rZkY4Q1NFMVFKX2hmV0xvRXZpNmdxLUVPcnZ1Z2ZnPT0=|3d209a9dbad2de0a571ddf85e0420385e06ae07072d1d4cc01a935f6112ecf1d',
        'domain': '.zhihu.com',
        'path': '/'
    })
    await page.setRequestInterception(True)
    page.on('request', intercept_request)

    question_id_list = []
    question_content = []
    n = 0
    while n < 1:
        await page.goto(search_url + '世界卫生组织')
        time.sleep(0.5)
        elements = await page.querySelectorAll('.ContentItem-title a')

        for item in elements:
            link = await(await item.getProperty('href')).jsonValue()
            print(link)
            t_url = link.split('/')
            t_question_id = t_url[4]
            if len(t_url) > 5:
                if t_url[4] in question_id_list:  # 如果此问题已经爬过了就跳过 这里冗余了，因为每次底部刷新必会出现爬过的链接，有待改良
                    print('------------------------一个爬过的问题--------------------------------')
                    continue
                else:
                    question_id_list.append(t_question_id)  # 写入历史链接
            else:
                continue

        # await page.evaluate('window.scrollBy(0, document.body.scrollHeight)')
        await page.reload()
        n += 1
        time.sleep(0.5)

    print(question_id_list)
    await browser.close()
    async with aiohttp.ClientSession(cookies=cookies) as client:
        url_list = (get_answers_by_id_url.format(id=question_id, offset=offset) for question_id in question_id_list for offset in range(0, 81, 20))
        tasks_list = (asyncio.create_task(get_answers(url, client)) for url in url_list)
        result = await asyncio.gather(*tasks_list)
        # tags_list = []
        contents = ''
        tr4s = TextRank4Sentence()
        tr4w = TextRank4Keyword()
        # print(result)

        q_id = ''
        text = ''
        for i in result:
            if i == 0:
                continue
            elif q_id == '':
                q_id = i[0]['question']['id']
            elif i[0]['question']['id'] != q_id:
                q_id = i[0]['question']['id']
                # tr4w.analyze(text=text, lower=True, window=2)
                # for phrase in tr4w.get_keyphrases(keywords_num=10, min_occur_num=2):
                #     print(phrase)
                tr4s.analyze(text=text, lower=True, source='no_stop_words')
                for item in tr4s.get_key_sentences(num=5):
                    print(item.weight, item.sentence)
                text = ''
            else:
                for j in i:
                    content = html_wash(j['content'])
                    text += content
                    print('id:{id}, question_id:{question_id}, title:{title}, content:{content}'.format(id=j['id'], question_id=j['question']['id'], title=j['question']['title'], content=content))
                        # print(item.index, item.weight, item.sentence)  # index是语句在文本中位置，weight是权重
                    # tags = jieba.analyse.extract_tags(j['content'], topK=10, withWeight=True, allowPOS=('n', 'nr','ns', 'nt', 'v'))

        #             tags_list.append(dict(tags))
        # col.insert_many(tags_list)
    # words_count = collections.Counter(keywords)
    # print(words_count)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(search())


