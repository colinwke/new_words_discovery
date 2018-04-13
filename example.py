"""
分词示例
"""
import pandas as pd
from _core.freq_calculator import WordCut, read_file

# 读取语料
corpus = read_file(r'./corpus/Swordsman.txt')
# 去除多余的空格
corpus = [''.join(x.split()) for x in corpus]

# 切词
word_cut = WordCut(min_freq=4)  # 最小词频为4, 越小越慢
result = word_cut.cut(corpus)  # 计算词语信息

# 保存结果
result = pd.DataFrame(result, columns=word_cut.get_columns_name())
print(result.describe())
result.to_csv('result.csv', index=False, encoding='utf-8')
