# -*- coding:utf-8 -*-

import numpy as np
import jieba
import jieba.analyse
from gensim import corpora, models, matutils
from textrank4zh import TextRank4Sentence  # 关键词和关键句提取
import pymongo
import time
import datetime
import difflib
import re

class Single_Pass_Cluster(object):
    def __init__(self,
                 origin_data,
                 stop_words_file,
                 generate_time):
        self.origin_data = origin_data
        self.stop_words_file = stop_words_file
        self.result = []
        self.generate_time = generate_time

    def loadData(self):
        # 以列表的形式读取文档
        texts = []
        i = 0
        for i in self.origin_data:
            texts.append({
                'text': i['content'].strip(),
                'data': i
            })
        return texts

    def word_segment(self, tocut_data):
        # 对语句进行分词，并去掉停用词
        stopwords = [line.strip() for line in open(self.stop_words_file, encoding='utf-8').readlines()]
        segmentation = []
        for i in range(0, len(tocut_data)):
            cut_word = []
            tocut = tocut_data[i]
            for j in tocut.pop('text'):
                words = jieba.cut(j)
                for word in words:
                    if word == ' ':
                        continue
                    if word not in stopwords:
                        cut_word.append(word)
            tocut['word_segmentation'] = cut_word
            segmentation.append(tocut)
        return segmentation

    def get_Tfidf_vector_representation(self, word_segmentation, pivot=10, slope=0.1):
        # 得到文档的空间向量
        word_segmentation = [i['word_segmentation'] for i in word_segmentation]
        dictionary = corpora.Dictionary(word_segmentation)  # 获取分词后词汇和词汇id的映射关系，形成字典
        corpus = [dictionary.doc2bow(text) for text in word_segmentation]   # 得到语句的向量表示
        tfidf = models.TfidfModel(corpus, pivot=pivot, slope=slope)      # 进一步获取语句的TF-IDF向量表示
        corpus_tfidf = tfidf[corpus]
        return corpus_tfidf

    def getMaxSimilarity(self, dictTopic, vector):
        # 计算新进入文档和已有文档的文本相似度，这里的相似度采用的是cosine余弦相似度
        maxValue = 0
        maxIndex = -1
        for k, cluster in dictTopic.items():
            oneSimilarity = np.mean([matutils.cossim(vector, v) for v in cluster])
            if oneSimilarity > maxValue:
                maxValue = oneSimilarity
                maxIndex = k
        return maxIndex, maxValue

    def single_pass(self, corpus, texts, theta):
        dictTopic = {}
        clusterTopic = {}
        numTopic = 0
        cnt = 0
        for vector, text in zip(corpus, texts):
            if numTopic == 0:
                dictTopic[numTopic] = []
                dictTopic[numTopic].append(vector)
                clusterTopic[numTopic] = []
                clusterTopic[numTopic].append(text)
                numTopic += 1
            else:
                maxIndex, maxValue = self.getMaxSimilarity(dictTopic, vector)
                # 以第一篇文档为种子，建立一个主题，将给定语句分配到现有的、最相似的主题中
                if maxValue > theta:
                    dictTopic[maxIndex].append(vector)
                    clusterTopic[maxIndex].append(text)
                # 或创建一个新的主题
                else:
                    dictTopic[numTopic] = []
                    dictTopic[numTopic].append(vector)
                    clusterTopic[numTopic] = []
                    clusterTopic[numTopic].append(text)
                    numTopic += 1
            cnt += 1
            if cnt % 1000 == 0:
                print("processing {}...".format(cnt))
        return dictTopic, clusterTopic

    def fit_transform(self, theta):
        # 得出最终的聚类结果：包括聚类的标号、每个聚类的数量、关键主题词和关键语句
        datMat = self.loadData()
        word_segmentation = []
        word_segmentation = self.word_segment(datMat)  # 分词完毕
        print("............................................................................................")
        print('文本已经分词完毕 !')

        # 得到文本数据的空间向量表示
        corpus_tfidf = self.get_Tfidf_vector_representation(word_segmentation)
        dictTopic, clusterTopic = self.single_pass(corpus_tfidf, datMat, theta)
        print("............................................................................................")
        print("得到的主题数量有: {} 个 ...".format(len(dictTopic)))
        print("............................................................................................\n")

        # 按聚类语句数量对聚类结果进行降序排列，找到重要的聚类群
        clusterTopic_list = sorted(clusterTopic.items(), key=lambda x: len(x[1]), reverse=True)
        print(clusterTopic_list)
        for k in clusterTopic_list:
            cluster_title = ''
            total_forward_comment_like = 0
            urls_to_print = ''
            related_data = []
            for item in k[1]:
                cluster_title += item['data']['content']
                # total_forward_comment_like += item['data']['hotspot_data']['forward_comment_like']
                urls_to_print += '\n' + item['data']['hotspot_data']['url']
                related_data.append(item['data']['hotspot_data'])

            # 得到每个聚类中的主题关键词
            jieba.analyse.set_stop_words(self.stop_words_file)
            w_list = jieba.analyse.extract_tags(cluster_title, topK=15)

            # 得到每个聚类中的关键主题句TOP3
            sentence = TextRank4Sentence(stop_words_file=self.stop_words_file)
            sentence.analyze(text=cluster_title, lower=True)
            s_list = sentence.get_key_sentences(num=3, sentence_min_len=3)

            keywords = '/'.join([i for i in w_list])
            keysentences = '\n'.join([i.sentence for i in s_list])
            keysentences_to_save = [i.sentence for i in s_list]
            # print(
            #     "主题文档数】：{} \n【主题关键词】：{} \n【主题中心句】 ：\n{} \n【转评赞总数】 ：\n{} \n【链接】 ：\n{}".format(len(k[1]), keywords, keysentences, total_forward_comment_like, urls_to_print))
            # print("-------------------------------------------------------------------------")
            if len(k[1]) > 2:
                self.result.append({
                    'related_content_count': len(k[1]),
                    'keywords': keywords,
                    'keysentences': keysentences_to_save,
                    'forward_comment_like': -1,
                    'new_forward_comment_like': -1,
                    'related_data': related_data,
                    'generate_time': self.generate_time
                })
        return self.result

    def check_similarity(self, original, latest, delta):
        """
        :param original: 旧热点话题 [ hotspot ...]
        :param latest: 新热点话题 [ hotspot ...]
        :return: intersection: 二者的结合 [ hotspot ...]
        """
        intersection = []
        old = original[:]  # 这里进行列表复制是防止下面对数据的修改影响到元数据，因此取交并集的部分用索引定位元数据
        new = latest[:]
        for i_idx, i in enumerate(new):
            for j_idx, j in enumerate(old):
                similarity = difflib.SequenceMatcher(None, i['keywords'], j['keywords']).quick_ratio()  # 统计相似度
                if similarity >= delta:
                    print(i['keywords'] + '\n' + j['keywords'] + '\n')
                    print(similarity)
                    # 如果50%相似，则取交集
                    intersection.append({
                        '_id': old[j_idx]['_id'],  # id为旧id
                        'related_content_count': old[j_idx]['related_content_count'] + new[i_idx]['related_content_count'],  # 相关内容数求和
                        'keywords': new[i_idx]['keywords'],  # 关键词更新
                        'keysentences': new[i_idx]['keysentences'],  # 关键句更新
                        'forward_comment_like': old[j_idx]['new_forward_comment_like'],  # 将旧数据的转评赞保留到这
                        'new_forward_comment_like': -1,  # 新的转评赞会在聚类之后更新
                        'related_data': old[j_idx]['related_data'] + new[i_idx]['related_data'],  # 相关内容数据取并集
                        'generate_time': old[j_idx]['generate_time']  # 生成时间不变
                    })
                    # 把原数据删除，防止列表拼接时出现重复数据
                    original.remove(original[j_idx])
                    latest.remove(latest[i_idx])
        intersection += original + latest
        return intersection



if __name__ == '__main__':
    database_ip = 'localhost'
    database_port = 27017
    database_name = 'toutiao'

    client = pymongo.MongoClient(database_ip, database_port)
    db = client[database_name]
    crawler_col = db['red_news']
    hotspot_col = db['hotspot']
    hotspot2_col = db['hotspot_2']

    end = datetime.datetime.now()
    delta = datetime.timedelta(days=2)
    # delta2 = datetime.timedelta(days=5)
    start = end - delta
    # end = start + delta
    result = crawler_col.find({
        'hotspot_data.time': {
            '$gt': start.strftime('%Y-%m-%d %H:%M:%S'),
            '$lt': end.strftime('%Y-%m-%d %H:%M:%S')
        }
    })

    time_start = time.time()

    a = Single_Pass_Cluster(origin_data=result, stop_words_file='stop_words.txt', generate_time=end.strftime('%Y-%m-%d %H:%M:%S'))
    result = a.fit_transform(theta=0.25)

    # 备份下旧数据，出错了可以用来分析
    hotspot2_col.delete_many({})
    hotspot2_col.insert_many(result)

    time_end = time.time()
    print('聚类用时:', time_end - time_start)

    # 检查相似度，进行合并
    previous_result = list(hotspot_col.find())
    intersection = []
    if len(previous_result) == 0:
        intersection = result
    else:
        intersection = a.check_similarity(previous_result, result, 0.65)
        hotspot_col.delete_many({})

    hotspot_col.insert_many(intersection)

    # 网易新闻评论页：url: https://3g.163.com/touch/comment.html?docid= id
    # 在此页html中获取productKey，在数据库中获取ID，使用下面的页面获取所有评论及点赞
    # 获取所有评论及点赞：https://comment.api.163.com/api/v1/products/ proructKey /threads/ ID ?ibc=newswap
