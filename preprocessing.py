import string
import re
from annotator import annotator


def remove_punctuations(text):
    puncs = set(re.sub(r"[/.-]", "", string.punctuation))
    for ch in puncs:
        text = text.replace(ch, " ")
    return re.sub(r"\s+", " ", text).strip()


def get_main_text(text):
    text = re.sub(r"\|[^\n]*\|", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def lemmatize(doc, allowed_postags=['A', 'N', 'Ny', 'Np', 'V', 'Z']):
    sentences = []
    for sent in doc:
        new_sent = [word.lower() for (word, tag) in sent if tag in allowed_postags]
        sentences.append(new_sent)
    return sentences

def preprocessing(text):
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
    pos_tagged_text = annotator.pos_tagging(text)
    text = lemmatize(pos_tagged_text)
    # text = list(set(text))
    return text