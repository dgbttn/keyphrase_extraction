import string
import re

from reader import FileType


def remove_punctuations(text):
    puncs = set(re.sub(r"[/.-]", "", string.punctuation))
    for ch in puncs:
        text = text.replace(ch, " ")
    return re.sub(r"\s+", " ", text).strip()
    # return text


def get_main_text(text):
    return max(text.split('|'), key=len)


def preprocessing(text, file_type=None):
    if file_type == FileType.CONTENT:
        text = get_main_text(text)

    text = remove_punctuations(text)
    return text
