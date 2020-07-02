from os import listdir
from os.path import isfile, isdir, join


def get_file_list(folder_path):
    file_list = []
    deeper_file_list = []
    for f in listdir(folder_path):
        if isdir(join(folder_path, f)):
            print(join(folder_path, f))
            deeper_file_list = deeper_file_list + get_file_list(join(folder_path, f))
        elif isfile(join(folder_path, f)):
            file_list.append(join(folder_path, f))

    files = []
    for f in file_list:
        if 'about' in f:
            c = f.replace('about', 'content', 1)
            if c in file_list:
                files.append((f, c))
    return sorted(deeper_file_list + files, key=lambda x: x[0])


def read_text_file(file_path):
    with open(file_path, "r", encoding='utf8') as f:
        return "".join(f.readlines())
