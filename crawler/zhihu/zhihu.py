import requests
import pymysql
from requests.cookies import RequestsCookieJar
from threading import Timer
import time

cookie_jar = RequestsCookieJar()
cookie_jar.set("z_c0","2|1:0|10:1583991262|4:z_c0|92:Mi4xTzIxSEJRQUFBQUFBc05Vc3VXTHpFQ1lBQUFCZ0FsVk4zaGRYWHdBdHV0OFQ0bFBsQjNyVzNpZ3dXSmhYS213V0hB|c2aba3b5b8bd4490fc3e52680e5d8b636323e4a7bf1f497299e862202d20fed7" ,domain="zhihu.com", path="/")
url = 'https://www.zhihu.com/api/v3/feed/topstory/recommend?session_token=061de1a2292e038001be3fa19eb37916&desktop=true&page_number=2&limit=6&action=down&after_id=5&ad_interval=-1'
header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.87 Safari/537.36'}

db = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='wang2013', db='crawler')
cursor = db.cursor()


def zhihu_recommend():
    data = requests.get(url, cookies=cookie_jar, headers=header).json()['data']
    print(data)
    for i in data:
        if i['target']['type'] == 'answer':
            question_id = i['target']['question']['id']
            question_title = i['target']['question']['title']
            answer_count = i['target']['question']['answer_count']
            follower_count = i['target']['question']['follower_count']
        else:
            question_id = i['target']['id']
            question_title = i['target']['title']
            answer_count = i['target']['comment_count']
            follower_count = -1
        tag = ''
        for j in i['uninterest_reasons']:
            if j['reason_type'] != 'creator':
                tag += j['reason_text'] + '/'
        sql = 'insert into zhihu_recommend(question_id, question_title, follower_count, answer_count, tag) values(%s, %s, %s, %s, %s)'
        try:
            cursor.execute(sql, [question_id, question_title, follower_count, answer_count, tag])
        except pymysql.Error as e:
            print(e.args[0], e.args[1])
            if e.args[0] == '1062':
                err1062_sql = 'update zhihu_recommend set question_title=%s, follower_count=%s, answer_count=%s, tag=%s where question_id=%s'
                cursor.execute(err1062_sql, [question_title, follower_count, answer_count, tag, question_id])
        db.commit()


class RepeatingTimer(Timer):
    def run(self):
        while not self.finished.is_set():
            self.function(*self.args, **self.kwargs)
            self.finished.wait(self.interval)


t = RepeatingTimer(10.0, zhihu_recommend)
t.start()
time.sleep(20)
t.cancel()
cursor.close()
db.close()
