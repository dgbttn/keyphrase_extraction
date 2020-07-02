import re


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
    vv = ['V/v', 'v/v', 'Vv', 'vv', 'Về việc', 'về việc', 'Về', 'về']
    for v in vv:
        if text.startswith(v):
            text = text.replace(v, '', 1)
            break

    text = standardize(text)
    text = sentence_segmenting(text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text
