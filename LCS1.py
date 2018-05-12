class LCS:
    def __init__(self):
        self.counter = 0

    def lcs(self, a, b):
        lena = len(a)
        lenb = len(b)
        if lena > lenb:
            small_length = lenb
        else:
            small_length = lena
        #print('最小字符串长度为：' ,small_length)

        c = [[0 for i in range(lenb + 1)] for j in range(lena + 1)]
        flag = [[0 for i in range(lenb + 1)] for j in range(lena + 1)]
        for i in range(lena):
            for j in range(lenb):
                if a[i] == b[j]:
                    c[i + 1][j + 1] = c[i][j] + 1
                    flag[i + 1][j + 1] = 'ok'
                elif c[i + 1][j] > c[i][j + 1]:
                    c[i + 1][j + 1] = c[i + 1][j]
                    flag[i + 1][j + 1] = 'left'
                else:
                    c[i + 1][j + 1] = c[i][j + 1]
                    flag[i + 1][j + 1] = 'up'
        return c, flag, small_length


    def printLcs(self, flag, a, i, j):
        if i == 0 or j == 0:
            return
        if flag[i][j] == 'ok':
            self.printLcs(flag, a, i - 1, j - 1)
            #print(a[i - 1], end='')
            self.counter = self.counter + 1
        elif flag[i][j] == 'left':
            self.printLcs(flag, a, i, j - 1)
        else:
            self.printLcs(flag, a, i - 1, j)

    def LCS_score(self, a, b):

    #a = '''【证监会、住建部联合发文推进住房租赁资产证券化相关工作】近日中国证监会、住房城乡建设部在总结前期工作的基础上，联合发布了《关于推进住房租赁资产证券化相关工作的通知》(以下简称《通知》)。推进住房租赁资产证券化，将有助于盘活住房租赁存量资产，提高资金使用效率，促进住房租赁市场发展。（证监会网站）'''
    #b = '''【证监会住建部联合发文，推进住房租赁资产证券化相关工作】证监会、住建部联合发布《关于推进住房租赁资产证券化相关工作的通知》，明确优先支持大中城市、雄安新区等国家政策重点支持区域和利用集体建设用地建设租赁住房试点城市的住房租赁项目开展资产证券化。'''
        c, flag, small_length = self.lcs(a, b)


        xxx = self.printLcs(flag, a, len(a), len(b))
        #print('最大公共子序列的长度为：', self.counter)
        similarities = self.counter / small_length
        return similarities


# for i in c:
#     print(i)
# print('')
# for j in flag:
#     print(j)
# print('')
# xxx = printLcs(flag, a, len(a), len(b))
# print('')