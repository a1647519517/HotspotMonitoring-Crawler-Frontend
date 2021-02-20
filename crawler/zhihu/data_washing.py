import pymongo
from bson import Code


def main():
    mongo_client = pymongo.MongoClient('mongodb://localhost:27017/')
    db = mongo_client['zhihu']
    zhihu_col = db['zhihu']
    vec_col = db['vec']
    # vec_col.delete_many({})

    # 获取数据库内所有键
    map = Code('function() { for (var key in this) { emit(key, null); } }')
    reduce = Code('function(key, stuff) { return null; }')
    result = zhihu_col.map_reduce(map, reduce, 'myresults')
    words_list = result.distinct('_id')

    docs = zhihu_col.find()
    for doc in docs:
        keys = doc.keys()
        print(len(words_list))
        doc_vsm = [0]*len(words_list)
        for key in keys:
            if key == '_id':
                continue
            index = words_list.index(key)
            doc_vsm[index] = doc[key]
        vec_col.insert_one({'vec': doc_vsm})


if __name__ == '__main__':
    main()
