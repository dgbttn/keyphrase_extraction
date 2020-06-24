from wordbook import Wordbook
from textrank import TextRankModel
from extractor import Extractor

extractor = Extractor()

dataset = 'datasets/data_original_files0-9999'
wb = Wordbook(folder_path=dataset)
wb.extract_corpora(extractor)
wb.set_ignored_words(min_df_count=2, max_df=0.65)

extractor.stop()

tr = TextRankModel()
tr.set_ignored_words(wb.ignored_words)
