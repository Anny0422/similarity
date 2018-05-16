

def lcs(a, b):
    lena = len(a)
    lenb = len(b)
    small_length = min(lena, lenb)
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

a = '''$中牧股份(SH600195)$ 年报：实现营收40.7亿元，同比增长2.41%；净利近4亿元，同比增长19.57%；拟10转4派3.26元。'''
b = '''$合盛硅业(SH603260)$ 年报：实现营收69.5亿元，同比增长51.9%；净利15.17亿元，同比增长132.81%；拟10派4.41元。'''
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