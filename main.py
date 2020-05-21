import os
import sys
from wordbook import Wordbook
from textrank import TextRankModel
from extractor import Extractor

if __name__=='__main__':

    # init
    output_path = 'output'
    wb = Wordbook(folder_path='datasets/data_original_files0-9999')
    extr = Extractor(jarfile='VnCoreNLP-1.1.1.jar')

    # load corpora
    wb.extract_corpora(candidate_extractor=extr)
    wb.set_ignore_words()

    # init textrank model
    tr = TextRankModel()
    tr.init_wordbook(wordbook=wb)

    sys.exit()

    for i, doc in enumerate(wb.corpora):
        if len(doc)==0:
            continue
        keywords = tr.get_keywords(doc, number=20, window_size=4)
        file_name = wb.file_list[i][1].split('/')[-1]
        print(file_name)
        with open(os.path.join(output_path, file_name), 'w', encoding='utf8') as f:
            f.writelines(keywords)