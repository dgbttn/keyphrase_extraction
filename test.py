from extractor import Extractor
from reader import read_text_file
from preprocessing import preprocessing
from finalize import merge_phrase_list


ext = Extractor()
a = 'datasets/data_original_files0-9999/107_about.txt'
c = 'datasets/data_original_files0-9999/107_content.txt'
about = preprocessing(read_text_file(a))
content = preprocessing(read_text_file(c))
a_nps, a_ps, _ = ext.analyse_about(about)
doc, nps, nes = ext.analyse_content(content, merge_phrase_list(a_nps + a_ps) + a_nps)

print(ext.annotator.ner(content))

# print(ext.annotator.pos_tag(about))
# print(a_nps)
# print(a_ps)
# print(merge_phrase_list(a_nps + a_ps) + a_nps)
# print()
# print(nps)
# print(nes)
# print()
# merged_doc, ignores = doc
# for sent in merged_doc:
#     print(sent)
# print(ignores)

ext.stop()
