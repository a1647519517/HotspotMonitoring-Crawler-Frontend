d = {
    'against': 0, 'audit': False,
    'auditStatus': {'needcheck': False, 'web': False, 'app': False},
    'boardId': 'news2_bbs',
    'businessId': 'FE15AT740001899O',
    'businessType': 1, 'channelId': '0001',
    'cmtAgainst': 1,
    'cmtCount': 278,
    'cmtVote': 256,
    'createTime': '2020-06-01 07:26:56',
    'docId': 'FE15AT740001899O',
    'isAudit': False,
    'modifyTime': '2020-06-01 07:33:18',
    'pdocId': 'FE15AT740001899O',
    'rcount': 28,
    'sDK_VERSION': 0,
    'status': {'against': 'on', 'app': 'on', 'audio': 'off', 'joincount': 'on', 'web': 'on', 'label': 'on'},
    'tcount': 21,
    'title': '美圣地亚哥示威者与警察发生冲突 向警方投掷石块',
    'updateTime': '',
    'url': 'https://news.163.com/20/0601/07/FE15AT740001899O.html',
    'vote': 5
}

print(d.get('tcount'))
