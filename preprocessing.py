import string
import re


def remove_punctuations(text):
    puncs = set(re.sub(r'[,/.-]', '', string.punctuation))
    for ch in puncs:
        text = text.replace(ch, ', ')
    return re.sub(r'\s+', ' ', text).strip()


def sentence_segmenting(text):
    text = re.sub(r'\n{2,}', '. ', text)
    return text


def standardize(text):
    text = text.replace('–', '-')
    text = text.replace('-', ' - ')
    return text


def get_main_text(text):
    text = re.sub(r'\|[^\n]*\|', '', text)
    return text


def preprocessing(text):
    text = get_main_text(text)
    vv = ['V/v', 'v/v', 'Về việc', 'về việc', 'Về', 'về']
    for v in vv:
        if text.startswith(v):
            text = text.replace(v, '', 1)
            break

    text = remove_punctuations(text)
    text = standardize(text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text
