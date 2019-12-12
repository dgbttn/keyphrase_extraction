import string
import re
from vncorenlp import VnCoreNLP

from reader import FileType

annotator = VnCoreNLP("VnCoreNLP-1.1.1.jar", annotators="wseg,pos,ner,parse", max_heap_size='-Xmx2g')

def remove_punctuations(text):
    puncs = set(re.sub(r"[/.-]", "", string.punctuation))
    for ch in puncs:
        text = text.replace(ch, " ")
    return re.sub(r"\s+", " ", text).strip()
    # return text


def get_main_text(text):
    return max(text.split('|'), key=len)


def lemmatize(tags, allowed_postags=['A', 'N', 'Ny', 'Np', 'V', 'Z']):
    return [word for (word, tag) in tags if tag in allowed_postags]


def pos_tagging(text):
    annotated_text = annotator.annotate(text)
    sentences = annotated_text['sentences']
    text_out = []
    for sen in sentences:
        new_sen = [(w['form'], w['posTag']) for w in sen]
        text_out = text_out + new_sen
    return text_out


def preprocessing(text, file_type=None):
    text = text.strip()
    if file_type == FileType.CONTENT:
        text = get_main_text(text)

    if file_type == FileType.ABOUT:
        vv = ['V/v', 'v/v', 'Về', 'về', 'Về việc', 'về việc']
        for v in vv:
            if text.find(v)>-1:
                text = text.replace(v, '', 1)
                break
        
    text = remove_punctuations(text)
    return text


def get_candidates(text):
    text = preprocessing(text)
    text = lemmatize(pos_tagging(text))
    # text = list(set(text))
    return text