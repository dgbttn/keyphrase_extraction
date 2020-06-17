import string
import re


def remove_punctuations(text):
    puncs = set(re.sub(r'[,/.-]', '', string.punctuation))
    for ch in puncs:
        text = text.replace(ch, ', ')
    return re.sub(r'\s+', ' ', text).strip()


def standardize(text):
    text = text.replace('–', '-')
    text = text.replace('-', ' - ')
    return re.sub(r'\s+', ' ', text).strip()


def get_main_text(text):
    text = re.sub(r'\|[^\n]*\|', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
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
    return text
