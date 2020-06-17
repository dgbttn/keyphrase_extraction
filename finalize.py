from extractor import ORGANIZATION
from main import tr


def longest_common_substring(string1, string2):
    string1 = string1.lower()
    string2 = string2.lower()
    answer = ""
    len1, len2 = len(string1), len(string2)
    for i in range(len1):
        match = ""
        for j in range(len2):
            if (i + j < len1 and string1[i + j] == string2[j]):
                match += string2[j]
            else:
                if len(match) > len(answer):
                    answer = match
                match = ""
    return answer, len(answer)/min(len(string1), len(string2))


def merge_2_phrases(phrase1, phrase2, substring):

    if substring == phrase1:
        return phrase2
    if substring == phrase2:
        return phrase1

    substr_segments = substring.strip().split(' ')
    p1_segments = phrase1.strip().lower().split(' ')
    p2_segments = phrase2.strip().lower().split(' ')

    for word in substr_segments:
        if word not in p1_segments or word not in p2_segments:
            return phrase1 if len(phrase1) > len(phrase2) else phrase2

    b1 = phrase1.lower().find(substring)
    b2 = phrase2.lower().find(substring)
    e1 = b1 + len(substring)
    e2 = b2 + len(substring)

    if b1 > 0 and b2 > 0:
        return phrase1 if len(phrase1) > len(phrase2) else phrase2

    if b1 > 0:
        begin = phrase1[:b1]
    elif b2 > 0:
        begin = phrase2[:b2]
    else:
        begin = ''

    if e1 < len(phrase1):
        end = phrase1[e1:]
    elif e2 < len(phrase2):
        end = phrase2[e2:]
    else:
        end = ''

    return begin + substring + end


def merge_phrase_list(phrases=()):
    for p1 in phrases:
        for p2 in phrases:
            if p1 != p2:
                substr, ratio = longest_common_substring(p1, p2)
                if ratio >= 0.40:
                    phrases.remove(p1)
                    phrases.remove(p2)
                    phrases.add(merge_2_phrases(p1, p2, substr))
                    return merge_phrase_list(phrases)
    return phrases


def _in(bounder, substr):
    return substr.lower() in bounder.lower()


def _in_list(array, substr):
    return substr.lower() in [word.lower() for word in array]


def _in_any_item_of_list(array, substr):
    return any(_in(bounder, substr) for bounder in array)


def extract_about(about):
    about.noun_phrases = merge_phrase_list(about.noun_phrases)
    about.phrases = merge_phrase_list(about.phrases)
    phrases = merge_phrase_list(set(about.noun_phrases + about.phrases))
    organizations = {word for word, tag in about.named_entities if tag == ORGANIZATION}

    keyphrases = []
    # keyphrases contain organization
    for org in organizations:
        for phrase in phrases:
            if _in(phrase, org) and not _in_list(keyphrases, phrase):
                keyphrases.append(phrase)
    # keyphrases is organization
    for org in organizations:
        if not _in_any_item_of_list(keyphrases, org):
            keyphrases.append(org)
    # keyphrase contain other type named entities
    for ne, _ in about.named_entities:
        for phrase in phrases:
            if _in(phrase, ne) and not _in_list(keyphrases, phrase):
                keyphrases.append(phrase)
    # remain
    for phrase in phrases:
        if not _in_list(keyphrases, phrase):
            keyphrases.append(phrase)
    return keyphrases


def extract_content(content):
    phrases = merge_phrase_list(content.noun_phrases)
    organizations = {word for word, tag in content.named_entities if tag == ORGANIZATION}

    named_entity_keyphrases = []
    # keyphrases contain organization
    for org in organizations:
        for phrase in phrases:
            if _in(phrase, org) and not _in_list(named_entity_keyphrases, phrase):
                named_entity_keyphrases.append(phrase)
    # keyphrases is organization
    for org in organizations:
        if not _in_any_item_of_list(named_entity_keyphrases, org):
            named_entity_keyphrases.append(org)
    # keyphrase contain other type named entities
    for ne, _ in content.named_entities:
        for phrase in phrases:
            if _in(phrase, ne) and not _in_list(named_entity_keyphrases, phrase):
                named_entity_keyphrases.append(phrase)

    keywords = tr.get_keywords(content.tokenized_text, number=50, window_size=3)

    return named_entity_keyphrases, keywords
