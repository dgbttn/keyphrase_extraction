from wordbook import Wordbook
from extractor import Extractor
from tpr import LDAModel, TopicalPageRank
from textrank import TextRankModel

# extractor = Extractor()

# dataset = 'datasets/data_original_files0-9999'
# wb = Wordbook(folder_path=dataset)
# wb.extract_corpora(extractor)
# wb.set_ignored_words(min_df_count=2, max_df=0.65)

# extractor.stop()

# tr = TextRankModel(min_diff=1e-6, steps=20)
# tr.set_ignored_words(wb.ignored_words)


extractor = Extractor()
print('Extracting...')

dataset = 'datasets'
wb = Wordbook(folder_path=dataset)
wb.extract_corpora(extractor)
wb.set_ignored_words(min_df_count=2, max_df=0.65)

extractor.stop()

tr = TextRankModel(
    damping=0.4,
    min_diff=1e-8,
    steps=25,
    window_size=5
)

# corpora = [content.tokenized_text for about, content in wb.corpora]
# print('Setup LDA...')
# lda_model = LDAModel(corpora)
# lda_model.init_model(num_topics=100)

# print('setup TPR...')
# tpr = TopicalPageRank(
#     window_size=5,
#     damping=0.4,
#     min_diff=1e-8,
#     steps=25
# )
# tpr.set_extensions(lda_model=lda_model, ignored_words=wb.ignored_words)
