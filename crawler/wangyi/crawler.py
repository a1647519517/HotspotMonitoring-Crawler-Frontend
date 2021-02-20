from wangyi import WangyiCrawler
import asyncio
import pymongo
import redis

if __name__ == '__main__':
    database_ip = 'localhost'
    database_port = 27017
    database_name = 'crawler'

    client = pymongo.MongoClient(database_ip, database_port)
    db = client[database_name]

    pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
    rdb = redis.StrictRedis(connection_pool=pool)

    # 爬网易新闻
    crawler = WangyiCrawler(db, rdb)
    loop = asyncio.get_event_loop()
    urls = ['https://3g.163.com/touch/reconstruct/article/list/BBM54PGAwangning/{}-10.html'.format(i * 10) for i in range(30)]
    tasks = [asyncio.ensure_future(crawler.get_urls(url, crawler.data)) for url in urls]  # 爬url
    tasks = asyncio.gather(*tasks)
    loop.run_until_complete(tasks)
    tasks = [asyncio.ensure_future(crawler.get_news(item, crawler.news)) for item in crawler.data]  # 爬新闻
    tasks = asyncio.gather(*tasks)
    loop.run_until_complete(tasks)

    client.close()