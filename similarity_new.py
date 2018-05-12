# -*- coding: utf-8 -*-
import json
#import pandas as pd
import numpy as np
import jieba.posseg as pseg
import codecs
from gensim import corpora, models, similarities
from database import Database
import grpc
import data_pb2
import data_pb2_grpc
import datetime


class CacuSimil(object):


    def __init__(self):
         self.db = Database()
         self.db.connect('crawl_data')

    #获取待匹配数据，json形式
    def get_craw(self):
        conn = grpc.insecure_channel('192.168.1.100' + ':' + '2333')
        client = data_pb2_grpc.FormatDataStub(channel=conn)
        response = client.DoFormat(data_pb2.Data(text='getData'))
        craw_file = json.loads(response.text)
        return craw_file


    #连接数据库,取出用来对照的文本，sql_saved是一个元组；取出刚抓取的内容，放在元组sql_craw内；
    def conn_db(self, craw_file):
        db = Database()
        db.connect('crawl_data')

        cur_date = datetime.datetime.strptime(craw_file['date'], '%Y-%m-%d')
        preone_time = cur_date + datetime.timedelta(days=-1)
        day = preone_time.strftime('%Y-%m-%d')  # 格式化输出

        sql_saved = "select main_id, content, counts from finance_news where date >= '%s' and date <= '%s'" % (day, cur_date)
        saved_files = db.query(sql_saved)

        db.close()
        return saved_files #元组，元素也为元组（包含main_id，content，counts）。


    #对一个文本分词、去停用词
    def tokenization(self, content):
        # 构建停用词
        stop_words = 'stop_words_ch.txt'
        stopwords = codecs.open(stop_words, 'rb', encoding='utf-8').readlines()
        stopwords = [w.strip() for w in stopwords]
        # 结巴分词后的停用词性【标点符号、连词、助词、副词、介词、时语素、'的'、数词、方位词、代词】
        stop_flag = ['x', 'c', 'u', 'd', 'p', 't', 'uj', 'm', 'f', 'r']
        result = []
        words = pseg.cut(content)
        for word, flag in words:
            if flag not in stop_flag and word not in stopwords:
                result.append(word)
        return result


    #生成语料库,返回语料库，对应的main_id，counts
    def get_idcorpus(self, saved_files):
        corpus = []
        main_id = []
        counts = []
        for content_tuple in saved_files:
            content = str(content_tuple[1])
            corpus.append(self.tokenization(content))
            main_id.append(content_tuple[0])
            counts.append(content_tuple[2])
        return corpus, main_id, counts


    def gen_Model(self, corpus):

        #建立词袋模型:寻找整篇语料的词典、所有词
        dictionary = corpora.Dictionary(corpus)

        #分支一、BOW词袋模型：由doc2bow变成词袋
        doc_vectors = [dictionary.doc2bow(text) for text in corpus]

        #分支二、建立TF-IDF模型
        tfidf = models.TfidfModel(doc_vectors)
        tfidf_vectors = tfidf[doc_vectors]

        return dictionary, tfidf_vectors


    #输入待匹配的文件，计算相似度：结果是一个列表，元素为元组：[(0, 0.0), (1, 0.0)]
    def get_similar(self, craw_file, dictionary, tfidf_vectors):
         print(craw_file)
         content = craw_file['content']
         token = self.tokenization(content)
         token_bow = dictionary.doc2bow(token)
         index = similarities.MatrixSimilarity(tfidf_vectors)
         #index = similarities.Similarity(craw_file, tfidf_vectors, len(dictionary))
         sims = index[token_bow]
         result = list(enumerate(sims))
         return result

    def insert_or_counts(self, result, craw_file, main_id, counts):
         db = Database()
         db.connect('crawl_data')

         score_list = []
         # 遍历数据库中已存数据，若分值大于0.8，默认一样，给数据库数据计数
         for i in range(len(result)):
             score_list.append(result[i][1])
             if result[i][1]> 0.78:
                 id = main_id[i] #数据库中的main_id，用来之后更新数据库
                 num = counts[i] +1 #更新计数
                 sql_update = "update finance_news set counts='%s' where main_id='%s'"%(num,id)
                 db.execute(sql_update)
                 print('待匹配数据与数据库中相似度大于0.8的数据id为', id, '重复', '，','相似度为', result[i][1])

         # 若分值均小于0.8，则认为不重复，加入到数据库中
         if max(score_list) <0.78:
             max_index = np.argmax(score_list)
             print('待插入数据与数据库中最接近的数据id为', main_id[max_index], '相似度为：', max(score_list))
             #print(max(score_list))

             self.insert = 'INSERT INTO finance_news(content,date, id, tags, time,' \
                      ' update_time, url, website) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)'
             db.execute(self.insert, [craw_file['content'], craw_file['date'], craw_file['id'], \
                                  craw_file['tags'], craw_file['time'], craw_file['update_time'], \
                                  craw_file['url'], craw_file['website']])
         db.close()

if __name__ == '__main__':
    CS = CacuSimil()
    db = Database()
    db.connect('crawl_data')
    craw_file = CS.get_craw()  # 获取待匹配数据
    if craw_file:
        saved_files = CS.conn_db(craw_file)
        print(len(saved_files))
        corpus, main_id, counts = CS.get_idcorpus(saved_files)
        dictionary, tfidf_vectors = CS.gen_Model(corpus)
        result = CS.get_similar(craw_file, dictionary, tfidf_vectors)
        #print(result)
        CS.insert_or_counts(result, craw_file, main_id, counts)

    # #获得模型，获得两个字典，健为main_id，值为对应的
    # def get_Model(self, id_corpus):
    #     #建立词袋模型:寻找整篇语料的词典、所有词
    #     corpus = []
    #     for key, value in id_corpus.items():
    #         corpus.append(value)
    #     dictionary = corpora.Dictionary(corpus)
    #
    #     keys = []
    #     for key in id_corpus.items():
    #         keys.append(key)
    #     print(keys)
    #
    #     doc_vectors = [dictionary.doc2bow(text) for text in corpus]
    #
    #     #建立TF-IDF模型
    #     tfidf = models.TfidfModel(doc_vectors)
    #     tfidf_vectors = tfidf[doc_vectors]
    #
    #     return dictionary, tfidf_vectors, keys


    # #判断是否插入数据库
    # def insert_or_not(self, score, craw_file):
    #     db = Database()
    #     db.connect('crawl_data')
    #
    #     if score<0.6:
    #         db.execute(self.insert, [craw_file['content'], craw_file['date'], craw_file['id'], \
    #                             craw_file['tags'], craw_file['time'], craw_file['update_time'],\
    #                             craw_file['url'], craw_file['website']])
    #         print(craw_file)
    #     else:
    #         print('1')
    #     db.close()



# def run():
#     CS=CacuSimil()
#
#     while True:
#         db = Database()
#         db.connect('crawl_data')
#         craw_file = CS.get_craw()
#         print(craw_file)
#         if craw_file:
#             saved_files = CS.conn_db(craw_file)
#             corpus = CS.get_idcorpus(saved_files)
#             print(corpus)
#             if corpus:
#                 try:
#                     dictionary, tfidf_vectors = CS.get_Model(corpus)
#                     similar = CS.get_similar(craw_file, dictionary, tfidf_vectors)
#                     CS.insert_or_not(similar, craw_file)
#                 except:
#                     db.execute(CS.insert, [craw_file['content'], craw_file['date'], craw_file['id'], \
#                                            craw_file['tags'], craw_file['time'], craw_file['update_time'], \
#                                            craw_file['url'], craw_file['website']])
#         db.close()
#         time.sleep(2)






