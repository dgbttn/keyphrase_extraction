from os import mkdir
from os.path import isdir, join
from main import tr, wb
from finalize import get_keyphrases_decision

output_path = 'tr_raw'
if not isdir(output_path):
    mkdir(output_path)
print(output_path)

input_path = 'datasets/data_original_files0-9999'

input = ['107_content.txt', '6968_content.txt', '6979_content.txt', '7067_content.txt', '7974_content.txt',
         '9666_content.txt', '9676_content.txt', '9689_content.txt', '9741_content.txt', '9839_content.txt',
         '9878_content.txt', '9898_content.txt', '9921_content.txt', '107_content.txt', '6605_content.txt',
         '7830_content.txt', '7837_content.txt', '7861_content.txt', '2772_content.txt', '2955_content.txt',
         '2973_content.txt', '2992_content.txt', '3021_content.txt', '4516_content.txt', '4869_content.txt',
         '5937_content.txt', '5988_content.txt', '6032_content.txt', '6040_content.txt', '6054_content.txt',
         '6066_content.txt', '6075_content.txt', '6084_content.txt', '6112_content.txt', '6128_content.txt',
         '6164_content.txt', '6208_content.txt', '6217_content.txt', '6244_content.txt', '3495_content.txt',
         '3508_content.txt', '3537_content.txt', '3560_content.txt', '3576_content.txt', '3673_content.txt',
         '3710_content.txt', '3751_content.txt', '3754_content.txt', '3925_content.txt', '3945_content.txt']
# input = ['107_content.txt']

for file_name in input:
    index, about, content = wb.get(file_name)
    if not about.text or not content.tokenized_text or not content.tokenized_text[0]:
        continue
    print(file_name)
    keywords = tr.get_keywords(index, content.tokenized_text, content.ignores)
    with open(join(output_path, content.file_name), 'w', encoding='utf8') as f:
        for kp, score in keywords:
            f.write(kp + ' - ' + str(score) + '\n')

# for i, corpus in enumerate(wb.corpora):
#     about, content = corpus
#     # if not any(name in content.file_name for name in input):
#     #     continue
#     if not about.text or not content.tokenized_text or not content.tokenized_text[0]:
#         continue
#     print(content.file_name)
#     keyphrases = get_keyphrases_decision(tpr, i, about, content, topn=10)
#     with open(join(output_path, content.file_name), 'w', encoding='utf8') as f:
#         for kp in keyphrases:
#             f.write(kp + '\n')
