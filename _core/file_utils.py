"""
文件读写工具
---
read_file(file_path): 读取单个文件数据
read_folder(folder_path, file_suffix={'txt', 'csv', 'dat'}): 读取文件夹指定后缀文件
"""

from os import listdir
from os.path import isfile, join


def read_file(file_path):
    """ 读取文件内容 """
    pieces = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            pieces.append(line.strip())

    return pieces


def write_file(data, file_path):
    """ 保存文件内容 """
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(data))


def get_folder_files(folder_path, file_suffix={'txt', 'csv', 'dat'}):
    """ 获取目录下的所有文件 """
    if isinstance(file_suffix, set):
        files = [f for f in listdir(folder_path) if isfile(join(folder_path, f))]
        files = [join(folder_path, f) for f in files if f.split('.')[-1] in file_suffix]
    else:
        raise Exception("""file suffix error, do like file_suffix={'txt', 'csv', 'dat'}""")

    print('\n'.join(['corpus folder files:'] + [' |%s' % x for x in files]))
    return files


def read_folder(folder_path, file_suffix={'txt', 'csv', 'dat'}):
    """ 读取所有的数据 """
    files = get_folder_files(folder_path, file_suffix)
    pieces = []
    for file in files:
        pieces += read_file(file)

    return pieces
