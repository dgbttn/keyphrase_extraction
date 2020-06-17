from main import wb
from finalize import extract_about, extract_content


for i, corpus in enumerate(wb.corpora):
    print(i)
    about, content = corpus
    if not about.text or not content.tokenized_text:
        continue
    about_keyphrases = extract_about(about)
    ne_keyphrases, keywords = extract_content(content)
    print(len(about_keyphrases), len(ne_keyphrases), len(keywords))


# about = read_text_file('datasets/data_original_files0-9999/5612_about.txt')
# # about = 'V/v lắp đặt hệ thống chiếu sáng  công cộng đường Đào Trí, Quận 7. '
# print('about:', about)
# about = preprocessing(about)
# print('noun phrase:', extractor.get_long_tokens(about))
# print('phrases:', extractor.get_long_tokens(about, pos_tags=('N, A, V'), min_word_number=3))
# print('named entities:', extractor._get_named_entities(extractor._ner(about)))
# print('annotated:', extractor._pos_tagging(about))

# text = read_text_file('datasets/data_original_files0-9999/5612_content.txt')
# # text = 'Kính gửi: Khu Quản lý giao thông đô thị số 04'
# text = preprocessing(text)

# print('lt:')
# print(extractor.get_long_tokens(text))
# print('Start...')

# ners, new_text = extractor.merge_name_entities(text)
# print('ners:', ners)
# keywords = tr.get_keywords(new_text, number=50, window_size=3)
# # print(new_text)
# for kw, point in keywords:
#     print(kw, '-', point)

# extractor.stop()
