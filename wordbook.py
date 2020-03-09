from collections import OrderedDict
from reader import get_file_list, read_text_file
from preprocessing import get_candidates

class Wordbook(object): 
    def __init__(self, folder_path):
        self.folder_path = folder_path
        self.corpora = []
        self.vocab = OrderedDict()
        self.__read_corpora_from_folder()

    def __read_corpora_from_folder(self):
        self.file_list = get_file_list(self.folder_path)

        i = 0
        for a, c in self.file_list:
            about_text = read_text_file(a)
            content_text = read_text_file(c)

            # INSERT NER

            try:
                doc = get_candidates(about_text) + get_candidates(content_text)
            except Exception as e:
                doc = []
                print(a, e)
            
            self.corpora.append(doc)
            print(len(self.corpora))

            for sent in doc:
                for word in sent:
                    if word not in self.vocab:
                        self.vocab[word] = i
                        i += 1

    def set_ignore_words(self, max_df=0.90):
        
