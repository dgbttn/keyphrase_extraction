from wordbook import Wordbook
from textrank import TextRankModel
from selector import Selector
import os

if __name__=='__main__':

    # init
    output_path = 'output'
    wb = Wordbook('datasets/data_original_files0-9999')
    tr = TextRankModel(wb.vocab)
    selector = Selector()

    # load corpora
    wb.read_corpora_from_folder(selector)
    wb.set_ignore_words()

    exit()

    for i, doc in enumerate(wb.corpora):
        if len(doc)==0:
            continue
    keywords = tr.get_keywords(doc, number=20, window_size=4)
    file_name = wb.file_list[i][1].split('/')[-1]
    print(file_name)
    with open(os.path.join(output_path, file_name), 'w', encoding='utf8') as f:
        f.writelines(keywords)