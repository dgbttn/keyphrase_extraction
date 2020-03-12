from wordbook import Wordbook
from textrank import TextRankModel
from extractor import Extractor
import os

if __name__=='__main__':

    # init
    output_path = 'output'
    wb = Wordbook('datasets/data_original_files0-9999')
    extractor = Extractor()

    # load corpora
    wb.extract_corpora(extractor)
    wb.set_ignore_words()

    # init textrank model
    tr = TextRankModel()
    tr.init_wordbook(wb)

    exit()

    for i, doc in enumerate(wb.corpora):
        if len(doc)==0:
            continue
    keywords = tr.get_keywords(doc, number=20, window_size=4)
    file_name = wb.file_list[i][1].split('/')[-1]
    print(file_name)
    with open(os.path.join(output_path, file_name), 'w', encoding='utf8') as f:
        f.writelines(keywords)