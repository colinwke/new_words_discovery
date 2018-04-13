import re
from math import log
from collections import Counter


def read_file(file_path):
    """ 读取文件内容 """
    pieces = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            pieces.append(line.strip())

    return pieces


class WordInfo(object):
    def __init__(self, freq):
        self.freq = freq

        self.neighbors_left = []
        self.neighbors_right = []

        self.neighbor_left_entropy = -1
        self.neighbor_right_entropy = -1
        self.solid_degree = -1

    def __str__(self):
        return ','.join(
            ['%d' % self.freq,
             '%.4f' % self.neighbor_left_entropy, '%.4f' % self.neighbor_right_entropy, '%.6f' % self.solid_degree]
        )

    def to_list(self):
        return [self.freq,
                self.neighbor_left_entropy, self.neighbor_right_entropy, self.solid_degree]

    def calc_degree(self, solid):
        self.solid_degree = solid
        if self.solid_degree < 1: return
        self.neighbor_left_entropy = WordCut.get_entropy(self.neighbors_left)
        if self.neighbor_left_entropy < 0.1: return
        self.neighbor_right_entropy = WordCut.get_entropy(self.neighbors_right)


class WordCut(object):
    def __init__(self, min_freq=4, max_=11):
        self.min_freq = min_freq
        self.min_ = 1
        self.max_ = max_
        self.len_ = -1
        self.d_words_freq = {}
        print('WordCut information:\nmin_freq: %d\nword_max_len: %d' % (self.min_freq, self.max_))

    def _split_with_chs(self):
        self.data = [s for l in self.data for s in re.split(u'[^\u4e00-\u9fa5]+', l) if s]

    def _get_split_sub(self, s):
        """ 获取字符串的所有连续子串
            min_: 最小词语字数; max_: 最大词语字数 - 1
        """
        len_ = len(s)
        return [s[i:j] for i in range(len_) for j in range(self.min_ + i, min(self.max_ + i, len_ + 1))]

    def _get_split_index(self, len_):
        """ 获取字符串的所有连续子串
            min_: 最小词语字数; max_: 最大词语字数 - 1
        """
        return [(i, j) for i in range(len_) for j in range(self.min_ + i, min(self.max_ + i, len_ + 1))]

    def _get_d_words_freq(self):
        pieces = []
        for i in self.data:
            pieces += self._get_split_sub(i)
        counter = Counter(pieces)

        self.d_words_freq = counter

    def _get_word_neighbor_info(self):
        blank_terminal_replacer = 0
        for sentence in self.data:
            sentence_len = len(sentence)
            indices = self._get_split_index(sentence_len)
            for idx_left, idx_right in indices:
                word = sentence[idx_left:idx_right]
                word_info = self.d_words_freq.get(word, None)
                if word_info is not None:
                    blank_terminal_replacer += 1
                    terminal = sentence[idx_left - 1] if idx_left != 0 else str(blank_terminal_replacer)
                    word_info.neighbors_left.append(terminal)
                    terminal = sentence[idx_right] if idx_right != sentence_len else str(blank_terminal_replacer)
                    word_info.neighbors_right.append(terminal)

    def _get_solid_degree(self, word):
        """ 计算词语的凝固度 """
        if len(word) == 1: return 1
        freq_ = self.d_words_freq[word].freq
        solid_degree = min(map(
            lambda x: freq_ / self.d_words_freq[x[0]].freq / self.d_words_freq[x[1]].freq * self.len_,
            [(word[:i], word[i:]) for i in range(1, len(word))]
        ))

        return solid_degree

    @staticmethod
    def get_entropy(x):
        """ 计算熵 """
        len_ = len(x)
        if len_ == 0: return 9.9
        counts = Counter(x).values()
        if len(counts) == 1: return 0
        entropy = 0
        for i in counts:
            p = i / len_
            entropy -= p * log(p, 2)  # 2.71828
        return entropy

    def _calc_degree(self):
        for k in self.d_words_freq:
            word_info = self.d_words_freq[k]
            word_info.calc_degree(self._get_solid_degree(k))

    def get_columns_name(self):
        return ['word', 'length', 'frequent', 'entropy_left', 'entropy_right', 'solid_degree']

    def cut(self, data, save_path=None):
        if isinstance(data, str):
            data = read_file(data)

        # 初始化
        self.data = data
        # step1. 对句子进行切分
        self._split_with_chs()
        # step2. 计算词频
        self._get_d_words_freq()
        count_bin_unique = 0
        count_bin_total = 0
        update_d_words_freq = {}
        for k, v in self.d_words_freq.items():
            if len(k) == 2:
                count_bin_unique += 1
                count_bin_total += v

            if v > self.min_freq:
                update_d_words_freq[k] = WordInfo(v)
        self.d_words_freq = update_d_words_freq
        self.len_ = count_bin_total
        print('count bin_word total : %d' % count_bin_total)
        print('count bin_word unique: %d' % count_bin_unique)
        print('corpus solid degree  : %f' % ((count_bin_total - count_bin_unique) / count_bin_total))

        # step4. 获取邻词信息
        self._get_word_neighbor_info()
        # step5. 计算凝固度和自由度
        self._calc_degree()

        # step5. 结果保存
        d_words_freq = [[x[0], len(x[0])] + x[1].to_list()
                        for x in self.d_words_freq.items()
                        if (len(x[0]) > 1) & (x[1].neighbor_right_entropy >= 0.1)]
        d_words_freq = list(sorted(d_words_freq, key=lambda x: x[2], reverse=True))

        if save_path is not None:
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(','.join(self.get_columns_name()) + '\n')
                f.write('\n'.join([','.join([str(xx) for xx in x]) for x in d_words_freq]))

        return d_words_freq
