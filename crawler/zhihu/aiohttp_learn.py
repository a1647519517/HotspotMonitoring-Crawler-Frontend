import aiohttp
import asyncio
import pymongo

search_url = 'https://www.zhihu.com/api/v4/search_v3'
# search_url = 'https://www.zhihu.com/api/v4/search_v3?t=general&correction=1&limit=20&offset={}&show_all_topics=0&time_zone=a_week&q=新冠肺炎'
get_answers_by_id_url = 'https://www.zhihu.com/api/v4/questions/{}/answers?include=data[*].comment_count,content,editable_content,voteup_count&limit=5&offset=5&platform=desktop&sort_by=updated'
search_params = {
    # 't': 'general',
    # 'correction': 1,
    # 'limit': 20,
    # 'offset': 0,
    # 'show_all_topics': 0,
    'time_zone': 'a_week',
    'q': '新冠肺炎'
}
headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36',
    ':authority': 'api.zhihu.com',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'referer': 'https://www.zhihu.com/search?q=新冠肺炎&type=content&utm_content=search_history&range=1w'
}

# 获取某个问题的回答
# https://www.zhihu.com/api/v4/questions/369494608/answers?include=data[*].comment_count,content,editable_content,voteup_count&limit=5&offset=5&platform=desktop&sort_by=default

cookies = {
    'capsion_ticket': '2|1:0|10:1586419374|14:capsion_ticket|44:MmI5Mzg5MjA5OThiNDlkOWFiOWYxNWU5YTEzZGJmNmE=|a326677b631638f747ea3aeb9cd4397d1a9718f787fb95276a4a33c759744da0',
    '_xsrf': 'kNbNU4I2tXalaIhDuXiQbqf1ATuABgFZ',
    'z_c0': '2|1:0|10:1586419379|4:z_c0|80:MS4xR2NUakR3QUFBQUFtQUFBQVlBSlZUYk1rZkY4Q1NFMVFKX2hmV0xvRXZpNmdxLUVPcnZ1Z2ZnPT0=|3d209a9dbad2de0a571ddf85e0420385e06ae07072d1d4cc01a935f6112ecf1d',
    '_zap': '36721b44-5fcb-4870-b933-fa7a80897ad5',
    'd_c0': '"AADSu1aRFxGPTjGqEe6uTMhdMNALBBraUQ4=|1586419379"',
    '_ga': 'GA1.2.1562305503.1586419243',
    '_gid': 'GA1.2.1761437258.1586861060',
    'tst': 'r',
    'Hm_lvt_98beee57fd2ef70ccdd5ca52b9740c49': '1586419244,1586861059',
    'Hm_lpvt_98beee57fd2ef70ccdd5ca52b9740c49': '1586938350',
    'KLBRSID': 'b33d76655747159914ef8c32323d16fd|1586419760|1586419374'
}

# https://www.zhihu.com/api/v4/questions/{}/answers?include=data[*].comment_count,content,editable_content,voteup_count&limit=5&offset=5&platform=desktop&sort_by=updated


async def get_urllist():
    async with aiohttp.ClientSession(cookies=cookies) as client:
        async with client.get(search_url, params=search_params) as resp:
            a = await resp.json()
            print(a)
            t = a['paging']['next'].split('&')
            print(t)
            t[3] = 'offset={}'
            return ('&'.join(t).format(offset) for offset in range(0, 60, 20))


async def search(url, client):
    await asyncio.sleep(1)
    resp = await client.get(url)
    return await resp.json()


async def main():
    async with aiohttp.ClientSession(cookies=cookies) as client:
        url_list = await get_urllist()
        tasks_list = (asyncio.create_task(search(url, client)) for url in url_list)
        result = await asyncio.gather(*tasks_list)
        for t in result:
            print(t)
    # print(content)
    # if content['paging']['is_end']:  # 即已无更多结果，应结束本次爬虫
    #     return 0
    # else:
    #     next_url = content['paging']['next']
    #     for
    # print(content['paging']['next'])

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
