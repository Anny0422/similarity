import numpy as np
import grpc
import time
from concurrent import futures
#from demo import data_pb2, data_pb2_grpc
import data_pb2
import data_pb2_grpc
from database import Database
import json
import datetime
import jieba.posseg as pseg
import codecs
from gensim import corpora, models, similarities

class CJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, datetime.date):
            return obj.strftime("%Y-%m-%d")
        else:
            return json.JSONEncoder.default(self, obj)

class FormatData(data_pb2_grpc.FormatDataServicer):

    def __init__(self):
        self.db = Database()
        self.db.nsert = 'INSERT INTO finance_news(content,date, id, tags, time,' \
                 ' update_time, url, website) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)'


    #连接数据库,取出用来对照的文本，sql_saved是一个元组；取出刚抓取的内容，放在元组sql_craw内；
    def conn_db(self, craw_file):

        cur_date = datetime.datetime.strptime(craw_file['date'], '%Y-%m-%d')
        preone_time = cur_date + datetime.timedelta(days=-1)
        day = preone_time.strftime('%Y-%m-%d')  # 格式化输出

        sql_saved = "select main_id, content, counts from finance_news where date >= '%s' and date <= '%s'" % (day, cur_date)
        saved_files = self.db.query(sql_saved)

        return saved_files


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

    #生成语料库：返回语料库，以及对应的main_id，counts
    def get_corpus(self, saved_files):
        corpus = []
        main_id = []
        counts = []
        for content_tuple in saved_files:
            content = str(content_tuple[1])
            corpus.append(self.tokenization(content))
            main_id.append(content_tuple[0])
            counts.append(content_tuple[2])
        return corpus, main_id, counts

    #获得模型
    def get_Model(self, corpus):
        #建立词袋模型:寻找整篇语料的词典、所有词
        dictionary = corpora.Dictionary(corpus)

        #分支一、BOW词袋模型：由doc2bow变成词袋
        doc_vectors = [dictionary.doc2bow(text) for text in corpus]
        #分支二、建立TF-IDF模型
        tfidf = models.TfidfModel(doc_vectors)
        tfidf_vectors = tfidf[doc_vectors]

        return dictionary, tfidf_vectors

        # 输入待匹配的文件，计算相似度：结果是一个列表，元素为元组：[(0, 0.0), (1, 0.0)]
    def get_similar(self, craw_file, dictionary, tfidf_vectors):
         content = craw_file['content']
         token = self.tokenization(content)
         token_bow = dictionary.doc2bow(token)

         index = similarities.MatrixSimilarity(tfidf_vectors)
         #index = similarities.Similarity(craw_file, tfidf_vectors, len(dictionary))
         sims = index[token_bow]
         result = list(enumerate(sims))
         return result


    def insert_or_counts(self, result, craw_file, main_id, counts):

         score_list = [] #用来存储相似度分数
         # 遍历数据库中已存数据，若分值大于0.8，默认一样，给数据库数据计数
         for i in range(len(result)):
             score_list.append(result[i][1])

             if result[i][1]> 0.78:
                 id = main_id[i] #数据库中的main_id，用来之后更新数据库
                 count_num = counts[i] +1 #更新计数
                 sql_update = "update finance_news set counts='%s' where main_id='%s'"%(count_num,id)
                 self.db.execute(sql_update)
                 return u'待匹配数据与数据库中相似度大于0.8的数据id为'+ str(id) + u'重复' + u'，'+ u'相似度为' + str(result[i][1])

         # 若分值均小于0.8，则认为不重复，加入到数据库中
         if max(score_list) <0.78:
             max_index = np.argmax(score_list)
             self.db.execute(self.insert, [craw_file['content'], craw_file['date'], craw_file['id'], \
                                  craw_file['tags'], craw_file['time'], craw_file['update_time'], \
                                  craw_file['url'], craw_file['website']])

             return u'待插入数据与数据库中最接近的数据id为'+ str(main_id[max_index]) + u'相似度为：'+ str(max(score_list))


    def DoFormat(self, request):

        craw_file = request.text
        craw_file = json.loads(craw_file)
        if craw_file:
            self.db.connect('crawl_data')
            msg = ''
            if craw_file:
                print(craw_file)
                saved_files = self.conn_db(craw_file)
                corpus, main_id, counts = self.get_corpus(saved_files)

                if corpus:
                    try:
                        dictionary, tfidf_vectors = self.get_Model(corpus)
                        similar = self.get_similar(craw_file, dictionary, tfidf_vectors)
                        msg = self.insert_or_counts(similar, craw_file, main_id, counts)
                    except:
                        self.db.execute(self.insert, [craw_file['content'], craw_file['date'], craw_file['id'], \
                                               craw_file['tags'], craw_file['time'], craw_file['update_time'], \
                                               craw_file['url'], craw_file['website']])
                        msg = u'插入成功'
            self.db.close()
            return data_pb2.Data(text=msg)
        else:
            return data_pb2.Data(text='None')

class Getserver(object):
    def serve(self):
        _ONE_DAY_IN_SECONDS = 60 * 60 * 24
        _HOST = '0'
        _PORT = '2444'
        grpcServer = grpc.server(futures.ThreadPoolExecutor(max_workers=4))
        data_pb2_grpc.add_FormatDataServicer_to_server(FormatData(), grpcServer)
        grpcServer.add_insecure_port(_HOST + ':' + _PORT)
        grpcServer.start()

        try:
            while True:
                time.sleep(_ONE_DAY_IN_SECONDS)
        except KeyboardInterrupt:
            grpcServer.stop(0)

if __name__ == '__main__':

    ser = Getserver()
    ser.serve()





