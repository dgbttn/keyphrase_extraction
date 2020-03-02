import gensim
import gensim.corpora as corpora
import pyLDAvis
import pyLDAvis.gensim

from reader import *
from preprocessing import *

# if __name__ == '__main__':
folder_path = 'datasets/data_original_files0-9999'
file_list = get_file_list(folder_path)

data = []
for a, c in file_list:
    about_text = read_text_file(a)
    content_text = read_text_file(c)
    doc = get_candidates(about_text) + get_candidates(content_text)
    data.append(doc)

id2word = corpora.Dictionary(data)
