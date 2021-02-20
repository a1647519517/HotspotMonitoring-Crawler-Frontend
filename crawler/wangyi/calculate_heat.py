import time
import pymongo
import math

def calculate_heat(data, base, hc):
    for idx, i in enumerate(data):
        rcc = i['related_content_count']
        nfcl = i['new_forward_comment_like']
        fcl = i['forward_comment_like']
        d_fcl = nfcl - fcl
        now = time.time()
        generate_time = time.mktime(time.strptime(i['generate_time'], '%Y-%m-%d %H:%M:%S'))
        delta = (now - generate_time) / (-24 * 3600)
        result = int(((d_fcl / rcc - math.log(rcc * 1000, base)) * rcc + (nfcl + rcc * 500)) * math.exp(hc * delta))
        # print('(({} - math.log({}, {})) * {} + {}) * math.exp({})'.format(d_fcl / rcc, rcc * 1000, b, rcc, nfcl + rcc * 500, p * delta))
        # print('关键词: {}\n相关文本数:{} 新点赞数:{}, 旧点赞数: {}\n发布时间:{}\n舆情指数:{}\n'
        #       .format(i['keywords'], rcc, nfcl, fcl, i['generate_time'], result))
        data[idx]['heat'] = result
    heat_col.delete_many({})  # 等之后再让后端进行优化，目前先只保留最新数据
    heat_col.insert_many(data)

    result = heat_col.find().sort('heat', -1)
    # for i in result:
    #     print('关键词: {}\n相关文本数:{} 新点赞数:{}, 旧点赞数: {}\n发布时间:{} 舆情指数:{}\n'
    #           .format(i['keywords'], i['related_content_count'], i['new_forward_comment_like'], i['forward_comment_like'],
    #                   i['generate_time'], i['heat']))

if __name__ == '__main__':
    database_ip = 'localhost'
    database_port = 27017
    database_name = 'crawler'
    base = 1.005
    hc = 0.01  # 热度冷却系数

    client = pymongo.MongoClient(database_ip, database_port)
    db = client[database_name]
    hotspot_col = db['hotspot']
    heat_col = db['heat']

    data = list(hotspot_col.find())
    calculate_heat(data, base, hc)



