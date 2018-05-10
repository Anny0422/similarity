# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import jieba.posseg as pseg
import codecs
from gensim import corpora, models, similarities
from .database import Database
import grpc
import data_pb2
import data_pb2_grpc
import datetime

class CacuSimil(object):
    insert = 'INSERT INTO finance_new_news(content,date, id, tags, time,' \
             ' update_time, url, website) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)'

    #def __init__(self):
        # self.db = Database()
        # self.db.connect('crawl_data')

    #计算对比日期
    def date(self):
        today = datetime.date.today()
        preone_time = today + datetime.timedelta(days=-1)
        self.preone_time_nyr = preone_time.strftime('%Y-%m-%d')  # 格式化输出
        return self.preone_time_nyr


    #连接数据库,取出用来对照的文本，sql_saved是一个元组；取出刚抓取的内容，放在元组sql_craw内；
    def conn_db(self, day):
        db = Database()
        db.connect('crawl_data')
        sql_saved = "select content from finance_new_news where date >= '%s'" % (day)
        saved_files = db.query(sql_saved)
        #sql_craw = "select * from finance_old_news where date >= '%s'" % (day)
        #craw_file = list(db.query(sql_craw))
        #craw_file = db.query(sql_craw)
        db.close()
        return saved_files


    #对一个文本分词、去停用词
    def tokenization(self, content):
        # 构建停用词
        stop_words = 'stop_words_ch.txt'
        stopwords = codecs.open(stop_words, 'rb', encoding='utf-8').readlines()
        stop_words = [w.strip() for w in stopwords]
        # 结巴分词后的停用词性【标点符号、连词、助词、副词、介词、时语素、'的'、数词、方位词、代词】
        stop_flag = ['x', 'c', 'u', 'd', 'p', 't', 'uj', 'm', 'f', 'r']
        result = []
        words = pseg.cut(content)
        for word, flag in words:
            if flag not in stop_flag and word not in stopwords:
                result.append(word)
        return result

    #生成语料库
    def gen_corpus(self, saved_files):
        corpus = []
        for content_tuple in saved_files:
            content = str(content_tuple)
            corpus.append(self.tokenization(content))

        return corpus

    def gen_Model(self, corpus):
        #建立词袋模型:寻找整篇语料的词典、所有词
        dictionary = corpora.Dictionary(corpus)

        #分支一、BOW词袋模型：由doc2bow变成词袋
        doc_vectors = [dictionary.doc2bow(text) for text in corpus]

        #分支二、建立TF-IDF模型
        tfidf = models.TfidfModel(doc_vectors)
        tfidf_vectors = tfidf[doc_vectors]

        return dictionary, tfidf_vectors


    #输入待匹配的文件(元组形式)，利用词袋模型的字典将其映射到向量空间；计算相似度
    def get_similar(self, craw_file, dictionary, tfidf_vectors):
         content = craw_file['content']
         token = self.tokenization(content)
         token_bow = dictionary.doc2bow(token)

         index = similarities.MatrixSimilarity(tfidf_vectors)
         sims = index[token_bow]
         result = list(enumerate(sims))

         similar = []
         for i in range(len(result)):
             similar.append(result[i][1])
         return max(similar)

    def insert_or_not(self, score, craw_file):
        db = Database()
        db.connect('crawl_data')
        if score<0.9:
            db.execute(self.insert, craw_file)
        db.close()

    def get_craw(self):
        conn = grpc.insecure_channel('192.168.1.100' + ':' + '2333')
        client = data_pb2_grpc.FormatDataStub(channel=conn)
        response = client.DoFormat(data_pb2.Data(text='getData'))
        return response.text


def run(self):
    CS=CacuSimil()
    craw_data = CS.get_craw()
    saved_files = CS.conn_db()


# if __name__ == '__main__':
#         run()
#





