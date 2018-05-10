# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import jieba.posseg as pseg
import codecs
from gensim import corpora, models, similarities
from database import Database
from demo import Demo
import datetime



demo = Demo()
today = datetime.date.today()
print(today)
preone_time = today + datetime.timedelta(days=-1)
preone_time_nyr = preone_time.strftime('%Y-%m-%d') #格式化输出
print(preone_time_nyr)



#连接数据库
db = Database()
db.connect('crawl_data')
sql_saved = "select content from finance_news where date >= '%s'" % (preone_time_nyr)
saved_files = list(db.query(sql_saved))
print(saved_files)

sql_craw = "select * from finance_old_news where date >= '%s'" % (preone_time_nyr)
#craw_file = list(db.query(sql_craw))
craw_file = db.query(sql_craw)
print(len(craw_file))
db.close()


#构建停用词
stop_words = 'stop_words_ch.txt'

stopwords = codecs.open(stop_words, 'rb', encoding='utf-8').readlines()

stop_words = [w.strip() for w in stopwords]

#结巴分词后的停用词性【标点符号、连词、助词、副词、介词、时语素、'的'、数词、方位词、代词】
stop_flag = ['x', 'c', 'u', 'd', 'p', 't', 'uj', 'f', 'r']

#对一个文本（元组形式）分词、去停用词
def tokenization(content):
    result = []
    content = str(content)
    words = pseg.cut(content)
    for word, flag in words:
        if flag not in stop_flag and word not in stopwords:
            result.append(word)
    return result

#生成语料库
corpus = []
for content in saved_files:
    corpus.append(tokenization(content))
#print(corpus[0],corpus[1])
print(corpus)
print(len(corpus))


#建立词袋模型:寻找整篇语料的词典、所有词
dictionary = corpora.Dictionary(corpus)
print(dictionary)

#分支一、BOW词袋模型：由doc2bow变成词袋
doc_vectors = [dictionary.doc2bow(text) for text in corpus]
print(len(doc_vectors))
print(doc_vectors)

#分支二、建立TF-IDF模型
tfidf = models.TfidfModel(doc_vectors)
tfidf_vectors = tfidf[doc_vectors]
print(len(tfidf_vectors))
#print(len(tfidf_vectors[0]))


#输入一个待匹配的文件，利用词袋模型的字典将其映射到向量空间
for item in craw_file:
    #print(item)
    content = item[0]
    #print(content)
    token = tokenization(content)
    #print(token)
    token_bow = dictionary.doc2bow(token)
    #print(len(query_bow))
    print(token_bow)
    index = similarities.MatrixSimilarity(tfidf_vectors)
    sims = index[token_bow]
    result = list(enumerate(sims))
    print(result)
    #print(len(result))
    similar = []
    for i in range(len(result)):
        similar.append(result[i][1])
    print(max(similar))




    '''
    
    insert = 'INSERT INTO finance_new_news(content,date, id, tags, time,' \
         ' update_time, url, website) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)'


    def __init__(self):
        self.db = Database()
        self.db.connect('crawl_data')

    def process(self, valueList):
        self.db.execute(self.insert, item)

        self.db.close()





    flag = True
    for i in range(len(result)):
        if result[i][1] > 0.9:
            flag = False
            break
    if flag:
        print(str(item)+'1111111111111')
        demo.process(list(item))
'''







