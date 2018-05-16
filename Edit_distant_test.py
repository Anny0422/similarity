def minimumEditDistance(str_a, str_b):
    '''
    最小编辑距离，只有三种操作方式 替换、插入、删除
    '''
    lensum = float(len(str_a) + len(str_b))
    if len(str_a) > len(str_b):  # 得到最短长度的字符串
        str_a, str_b = str_b, str_a
    distances = range(len(str_a) + 1)  # 设置默认值
    for index2, char2 in enumerate(str_b):  # str_b > str_a
        newDistances = [index2 + 1]  # 设置新的距离，用来标记
        for index1, char1 in enumerate(str_a):
            if char1 == char2:  # 如果相等，证明在下标index1出不用进行操作变换，最小距离跟前一个保持不变，
                newDistances.append(distances[index1])
            else:  # 得到最小的变化数，
                newDistances.append(1 + min((distances[index1],  # 删除
                                             distances[index1 + 1],  # 插入
                                             newDistances[-1])))  # 变换
        distances = newDistances  # 更新最小编辑距离

    mindist = distances[-1]
    ratio = (lensum - mindist) / lensum
    # return {'distance':mindist, 'ratio':ratio}
    return ratio

str1 = '$中牧股份(SH600195)$ 年报：实现营收40.7亿元，同比增长2.41%；净利近4亿元，同比增长19.57%；拟10转4派3.26元。'
str2 = '$合盛硅业(SH603260)$ 年报：实现营收69.5亿元，同比增长51.9%；净利15.17亿元，同比增长132.81%；拟10派4.41元。'
ratio = minimumEditDistance(str1, str2)
print(ratio)