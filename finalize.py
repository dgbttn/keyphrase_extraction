from extractor import ORGANIZATION, LOCATION


def longest_common_substring(string1, string2):
    S = string1.lower()
    T = string2.lower()
    m = len(S)
    n = len(T)
    counter = [[0]*(n+1) for x in range(m+1)]
    longest = 0
    result = ""
    for i in range(m):
        for j in range(n):
            if S[i] == T[j]:
                c = counter[i][j] + 1
                counter[i+1][j+1] = c
                if c > longest:
                    longest = c
                    result = S[i-c+1:i+1]
    return result, len(result)/min(len(S), len(T))


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
    phrases = list(phrases)
    n = len(phrases)
    i = 0
    while i < n:
        j = i + 1
        while j < n:
            p1 = phrases[i]
            p2 = phrases[j]
            substr, ratio = longest_common_substring(p1, p2)
            if ratio >= 0.40:
                phrases[i] = merge_2_phrases(p1, p2, substr)
                del phrases[j]
                j -= 1
                n -= 1
            j += 1
        i += 1
    return phrases


def _in(bounder, substr):
    return substr.lower() in bounder.lower()


def _in_list(array, string, ratio=0.99):
    string = string.replace('_', ' ').strip().lower()
    for array_item in array:
        if array_item.replace('_', ' ').strip().lower() == string:
            return True
    return False


def _in_any_item_of_list(array, substr, ratio=0.99):
    substr = substr.replace('_', ' ').strip().lower()
    for array_item in array:
        _, common_ratio = longest_common_substring(substr, array_item)
        if common_ratio > ratio:
            return True
    return False


def extract_about(about):
    about.noun_phrases = merge_phrase_list(about.noun_phrases)
    about.phrases = merge_phrase_list(about.phrases)
    phrases = merge_phrase_list({*about.noun_phrases, *about.phrases})
    organizations = {word for word, tag in about.named_entities if tag == ORGANIZATION}
    locations = {word for word, tag in about.named_entities if tag == LOCATION}

    keyphrases = []
    # keyphrases is organization & location
    for org in organizations | locations:
        if not _in_list(keyphrases, org):
            keyphrases.append(org)
    # remain
    for phrase in phrases:
        if not _in_list(keyphrases, phrase) and not _in_any_item_of_list(keyphrases, phrase):
            keyphrases.append(phrase)

    return keyphrases


def extract_content(kw_extractor, index, content):
    organizations = {word for word, tag in content.named_entities if tag == ORGANIZATION}

    keyphrases = []
    # keyphrases is organization
    for org in organizations:
        if not _in_list(keyphrases, org):
            keyphrases.append(org)

    keywords = kw_extractor.get_keywords(index, content.tokenized_text, doc_ignores=content.ignores, number=1000)

    return keyphrases, keywords


def get_keyphrases_decision(kw_extractor, index, about, content, topn=10):
    about_kps = extract_about(about)
    content_kps, keywords = extract_content(kw_extractor, index, content)

    keyphrases = []

    for kp in about_kps:
        kp = kp.replace('_', ' ')
        if not _in_list(keyphrases, kp):
            keyphrases.append(kp)

    for kp in content_kps[:int(topn*0.7)-len(keyphrases)]:
        kp = kp.replace('_', ' ')
        if not _in_list(keyphrases, kp):
            keyphrases.append(kp)

    sub = []
    for word, score in keywords:
        if score < 0.02:
            break
        if len(keyphrases) == topn:
            break
        word = word.replace('_', ' ')
        if not _in_list(keyphrases, word):
            keyphrases.append(word)
        else:
            sub.append(word)

    while len(keyphrases) < topn and len(sub) > 0:
        keyphrases.append(sub[0])
        del sub[0]

    return keyphrases
