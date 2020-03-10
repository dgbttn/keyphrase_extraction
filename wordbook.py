from reader import get_file_list, read_text_file

class Wordbook(object): 
    def __init__(self, folder_path):
        self.folder_path = folder_path
        self.corpora = []
        self.vocab = {} # number of document that term in 

    def read_corpora_from_folder(self, candidate_selector):
        self.file_list = get_file_list(self.folder_path)

        for a, c in self.file_list:
            about_text = read_text_file(a)
            content_text = read_text_file(c)

            # INSERT NER

            try:
                about_candidates = candidate_selector.get_candidates(about_text)
                content_candidates = candidate_selector.get_candidates(content_text)
                doc = about_candidates + content_candidates
            except Exception as e:
                doc = []
                print(a, e)
            
            self.corpora.append(doc)
            print(len(self.corpora))

            word_list = set([word for sent in doc for word in sent])
            for word in word_list:
                self.vocab[word] = self.vocab.get(word, 0) + 1

    def set_ignore_words(self, min_df_count=0.05, max_df=0.50):
        term_document = sorted(self.vocab.items(), key=lambda x: x[1])
        n = len(self.corpora)
        self.ignore_words = [word for word, df in term_document if df<min_df_count or df/n>max_df]