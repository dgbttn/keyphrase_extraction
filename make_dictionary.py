from main import *


with open('dictionary.txt', 'w', encoding='utf8') as f:
    for word, count in sorted(wb.vocab.items(), key=lambda x: x[1]):
        f.write('{}.{}\n'.format(word, count))
