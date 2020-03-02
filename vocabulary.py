from collections import OrderedDict
from reader import *

class Vocabulary: 
    def __init__(self, folder_path):
        self.folder_path = folder_path
        self.__read_corpora_from_folder()

    def __read_corpora_from_folder(self):
        self.file_list = get_file_list(self.folder_path)

        data = []
        vocab = OrderedDict()
        i = 0
        doc_num = 0
        for a, c in self.file_list:
            about_text = read_text_file(a)