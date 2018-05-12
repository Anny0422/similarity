

def lcs(a, b):
    lena = len(a)
    lenb = len(b)
    if lena > lenb:
        small_length = lenb
    else:
        small_length = lena
    print('最小字符串长度为：' ,small_length)

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


def printLcs(flag, a, i, j):
    global counter
    if i == 0 or j == 0:
        return
    if flag[i][j] == 'ok':
        printLcs(flag, a, i - 1, j - 1)
        #print(a[i - 1], end='')
        counter = counter + 1
    elif flag[i][j] == 'left':
        printLcs(flag, a, i, j - 1)
    else:
        printLcs(flag, a, i - 1, j)

a = '''中国央行：截至3月末，全国共有小额贷款公司8471家；贷款余额9630亿元，一季度减少111亿元。'''
b = '''央行：小额贷款公司的贷款余额一季度减少111亿元人民币。'''
c, flag, small_length = lcs(a, b)

counter = 0
xxx = printLcs(flag, a, len(a), len(b))
print('最大公共子序列的长度为：', counter)

similarities = counter / small_length
print(similarities)


# for i in c:
#     print(i)
# print('')
# for j in flag:
#     print(j)
# print('')
# xxx = printLcs(flag, a, len(a), len(b))
# print('')