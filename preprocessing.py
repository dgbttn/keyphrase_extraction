import string
import re
from vncorenlp import VnCoreNLP

annotator = VnCoreNLP('VnCoreNLP-1.1.1.jar', annotators="wseg,pos,ner,parse", max_heap_size='-Xmx2g')

def remove_punctuations(text):
    puncs = set(re.sub(r"[/.-]", "", string.punctuation))
    for ch in puncs:
        text = text.replace(ch, " ")
    return re.sub(r"\s+", " ", text).strip()
    # return text


def get_main_text(text):
    return re.sub(r"\|[^\n]*\|", "", text)
    # return max(text.split('|'), key=len)


def lemmatize(doc, allowed_postags=['A', 'N', 'Ny', 'Np', 'V', 'Z']):
    sentences = []
    for sent in doc:
        new_sent = [word.lower() for (word, tag) in sent if tag in allowed_postags]
        sentences.append(new_sent)
    return sentences


def pos_tagging(text):
    annotated_text = annotator.annotate(text)
    doc = annotated_text['sentences']
    sentences = []
    for sent in doc:
        new_sent = [(w['form'], w['posTag']) for w in sent]
        sentences.append(new_sent)
    return sentences


def preprocessing(text):
    text = text.strip()
    text = get_main_text(text)
    vv = ['V/v', 'v/v', 'Về việc', 'về việc', 'Về', 'về']
    for v in vv:
        if text.startswith(v):
            text = text.replace(v, '', 1)
            break
        
    text = remove_punctuations(text)
    return text


def get_candidates(text):
    text = preprocessing(text)
    text = lemmatize(pos_tagging(text))
    # text = list(set(text))
    return text