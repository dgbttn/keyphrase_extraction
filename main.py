import os
from wordbook import Wordbook
from textrank import TextRankModel
from extractor import Extractor

dataset = 'datasets/data_original_files0-9999'
extractor = Extractor()
wb = Wordbook(folder_path=dataset)
wb.extract_corpora(extractor)
wb.set_ignored_words(min_df_count=2, max_df=0.65)
tr = TextRankModel()
tr.set_ignored_words(wb.ignored_words)

output_path = 'output'
if not os.path.isdir(output_path):
    os.mkdir(output_path)
