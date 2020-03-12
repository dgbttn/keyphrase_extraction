from reader import get_file_list, read_text_file

class Wordbook(object): 
    def __init__(self, folder_path):
        self.folder_path = folder_path
        self.corpora = []
        self.vocab = {} # number of document that term in 

    def extract_corpora(self, candidate_extractor):
        self.file_list = get_file_list(self.folder_path)

        for a, c in self.file_list:
            about_text = read_text_file(a)
            content_text = read_text_file(c)

            # INSERT NER

            try:
                a_ners, a_candidates = candidate_extractor.extract(about_text)
                c_ners, c_candidates = candidate_extractor.extract(content_text)
                doc = a_candidates + c_candidates
                ners = (a_ners, c_ners)
            except Exception as e:
                doc = []
                ners = []
                print(a, e)
            
            self.corpora.append((ners, doc))
            print(len(self.corpora))

            word_list = set([word for sent in doc for word in sent])
            for word in word_list:
                self.vocab[word] = self.vocab.get(word, 0) + 1

    def set_ignore_words(self, min_df_count=2, max_df=0.50):
        term_document = sorted(self.vocab.items(), key=lambda x: x[1])
        n = len(self.corpora)
        self.ignore_words = [word for word, df in term_document if df<=min_df_count or df/n>=max_df]