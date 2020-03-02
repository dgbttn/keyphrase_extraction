from os import listdir
from os.path import isfile, join
from enum import Enum


def get_file_list(folder_path):
    fileList = [join(folder_path, f)
                for f in listdir(folder_path) if isfile(join(folder_path, f))]
    files = []
    for f in fileList:
        if 'about' in f:
            c = f.replace('about', 'content', 1)
            if c in fileList:
                files.append((f, c))
    return sorted(files, key=lambda x: x[0])


def read_text_file(file_path):
    with open(file_path, "r", encoding='utf8') as f:
        return "".join(f.readlines())
