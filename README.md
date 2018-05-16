# similarity
## LCS1.py文件：
定义了一个类函数LCS：获得最大公共子序列，相似度=最大公共子序列/最小字符串的长度。
相当于一个模块，加载到主程序里。
## lcs_test.py文件：
内有两个函数，用来计算最大公共子序列、相似度，用来临时测试两个字符串的相似度。
## Edit_distant_test.py文件：
内有一个函数，用来计算最小编辑距离、相似度，用来临时测试两个字符串的相似度。
## stop_words_ch.txt文件：
停用词
## database,py文件:
定义了一个类函数Database：有几个函数：
getconf()：连接数据库，获取数据。要用到database.cfg.py文件里的东西
connect()：连接数据库
close()：关闭数据库
execute()：执行操作
executemany()：
query():查询操作
## similarity_new_lcs.py文件
定义了一个类CacuSimil：下有几个函数：
get_craw()：通过grpc获取一条数据，转换成json形式输出craw_file
conn_db(craw_file)：利用爬下来的那条数据，用database.py文件的类中的连接数据库函数connect()去连接database.cfg配置文件里的数据库。
          取出的是craw_file前一天到目前的所有数据saved_files
tokenization(content)：对一片文档content分词
get_idcorpus( saved_files)：获取语料库；返回的结果是contents，corpus，main_id，counts
gen_Model(corpus)：建立TF-IDF模型；返回的结果是字典，tfidf_vectors
get_similar(craw_file, dictionary, tfidf_vectors)：计算相似度。传入的craw_file是一个json形式。输出的是result
insert_or_counts(result, craw_file, contents, main_id, counts)：
