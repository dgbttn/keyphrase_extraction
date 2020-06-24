from reader import get_file_list, read_text_file
from preprocessing import preprocessing


popular_prefix_named_entity = {
    'sở',
    'uỷ_ban_nhân_dân',
    'ủy_ban_nhân_dân',
    'uỷ ban_nhân_dân',
    'ủy ban_nhân_dân',
    'ubnd'
}
popular_phrase_part = {
    'khẩn',
    'kính',
    'ngày',
    'cộng hòa',
    'xã hội chủ nghĩa việt nam',
    'độc lập',
    ' tự do',
    'hạnh phúc'
}


class About:
    def __init__(self, file_name='', text='', noun_phrases=(), phrases=(), named_entities=()):
        self.file_name = file_name
        self.text = text
        self.noun_phrases = noun_phrases
        self.phrases = phrases
        self.named_entities = named_entities


class Content:
    def __init__(self, file_name='', tokenized_text=(), noun_phrases=(), named_entities=()):
        self.file_name = file_name
        self.tokenized_text = tokenized_text
        self.noun_phrases = noun_phrases
        self.named_entities = named_entities


class Wordbook:
    def __init__(self, folder_path):
        self.folder_path = folder_path
        self.corpora = []
        self.vocab = {}  # number of document that term in
        self.file_list = get_file_list(self.folder_path)
        self.ignored_words = ()

    def make_about(self, file_path, extractor):
        about_text = read_text_file(file_path=file_path)
        about_text = preprocessing(about_text)
        noun_phrases, phrases, named_entities = extractor.analyse_about(about_text)
        file_name = file_path.split('/')[-1]
        return About(
            file_name=file_name,
            text=about_text,
            noun_phrases=noun_phrases,
            phrases=phrases,
            named_entities=named_entities
        )

    def make_content(self, file_path, extractor):
        content_text = read_text_file(file_path=file_path)
        content_text = preprocessing(content_text)
        tokenized_text, noun_phrases, named_entities = extractor.analyse_content(content_text)
        file_name = file_path.split('/')[-1]
        return Content(
            file_name=file_name,
            tokenized_text=tokenized_text,
            noun_phrases=noun_phrases,
            named_entities=named_entities
        )

    def extract_corpora(self, candidate_extractor):
        for a, c in self.file_list:
            try:
                about = self.make_about(a, candidate_extractor)
                content = self.make_content(c, candidate_extractor)
            except Exception as e:
                about = About(file_name=a.split('/')[-1])
                content = Content(file_name=c.split('/')[-1])
                print(a, e)

            self.corpora.append((about, content))
            print(len(self.corpora))

            if content.tokenized_text:
                word_list = {word for sent in content.tokenized_text for word in sent}
                for word in word_list:
                    self.vocab[word] = self.vocab.get(word, 0) + 1

    def set_ignored_words(self, min_df_count=2, max_df=0.50):
        term_document = sorted(self.vocab.items(), key=lambda x: x[1])
        n = len(self.corpora)
        self.ignored_words = {word for word, df in term_document if df < min_df_count or df/n >= max_df}
