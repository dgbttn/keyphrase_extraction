from vncorenlp import VnCoreNLP
from wordbook import popular_prefix_named_entity, popular_phrase_part, wrong_entity


ORGANIZATION = 'ORG'
PERSON = 'PER'
LOCATION = 'LOC'

NER_TAGS = [ORGANIZATION, PERSON, LOCATION]


class Token:

    def __init__(self, word, nerLabel, posTag):
        self.form = word
        self.nerLabel = nerLabel
        self.posTag = posTag


class Extractor:

    def __init__(self, jarfile='VnCoreNLP-1.1.1.jar'):
        print('Init VnCoreNLP Annotator...')
        self.annotator = VnCoreNLP(jarfile, annotators="wseg,pos,ner,parse", max_heap_size='-Xmx2g')

    def stop(self):
        self.annotator.close()

    def _pos_tagging(self, text):
        pos_tagged_text = self.annotator.pos_tag(text)
        return pos_tagged_text

    def _ner(self, text):
        ner_text = self.annotator.ner(text)
        return ner_text

    def _lemmatize(self, doc, allowed_postags=('N', 'Np', 'V')):
        sentences = []
        ignores = set()
        for sent in doc:
            new_sent = []
            for word, tag in sent:
                new_sent.append(word)
                if tag not in allowed_postags:
                    ignores.add(word)
            sentences.append(new_sent)
        return sentences, ignores

    def _get_named_entities(self, text):
        endline = ('.', 'O')
        old_tag = ''
        entity_segments = []
        entities = []

        for sent in text:
            sent.append(endline)
            for word, tag in sent:
                # not a segment of a named entity
                if len(tag) < 3 or tag[-3:] not in NER_TAGS:
                    if entity_segments:
                        entity = ' '.join(entity_segments)
                        if (entity, old_tag) not in entities and not (old_tag == PERSON and any(p in entity.lower() for p in wrong_entity)):
                            entities.append((entity, old_tag))
                        entity_segments = []
                        old_tag = ''
                    continue

                # is a segment of a named entity
                tag = tag[-3:]
                if tag != old_tag:
                    if entity_segments:
                        entity = ' '.join(entity_segments)
                        if (entity, old_tag) not in entities and not (old_tag == PERSON and any(p in entity.lower() for p in wrong_entity)):
                            entities.append((entity, old_tag))
                        entity_segments = []

                old_tag = tag
                entity_segments.append(word)

        return entities

    def extract(self, text):
        annotated_text = self.annotator.annotate(text)
        ner_text = [[(word['form'], word['nerLabel']) for word in sent] for sent in annotated_text['sentences']]
        pos_tagged_text = [[(word['form'], word['posTag']) for word in sent] for sent in annotated_text['sentences']]
        return self._get_named_entities(ner_text), self._lemmatize(pos_tagged_text)

    def annotate(self, doc):
        annotated_doc = self.annotator.annotate(doc)
        return [[Token(word['form'], word['nerLabel'], word['posTag']) for word in sent] for sent in annotated_doc['sentences']]

    def get_long_tokens(
            self, annotated_doc, pos_tags=('N', 'Ny', 'Np', 'Nc', 'Y', 'Z', 'A'),
            min_word_number=2, max_word_count=6):
        eos = Token('.', '.', '.')  # end of sentence
        long_tokens = []
        tokens = []
        for sent in annotated_doc:
            tokens = []
            sent.append(eos)
            for token in sent:
                if token.posTag in pos_tags:
                    tokens.append(token.form)
                else:
                    new_long_token = ' '.join(tokens).lower()
                    if len(tokens) >= min_word_number and len(tokens) <= max_word_count and not any(
                            p in new_long_token.replace('_', ' ') for p in popular_phrase_part):
                        long_tokens.append(new_long_token)
                    tokens = []
        return long_tokens

    def merge_name_entities(self, annotated_doc):
        remake_doc = [[(token.form, token.nerLabel) for token in sent] for sent in annotated_doc]
        ners = self._get_named_entities(remake_doc)
        new_doc = []
        for sent in annotated_doc:
            raw_sent = ' '.join([token.form for token in sent]).lower()
            pos_tags = [token.posTag for token in sent]
            for ner, _ in ners:
                ner = ner.lower()
                i = raw_sent.find(ner)
                while i > -1 and ner.count(' ') > 0:
                    raw_sent = raw_sent.replace(ner, ner.replace(' ', '_'), 1)
                    i = raw_sent.count(' ', 0, i)
                    pos_tags[i: i+ner.count(' ')+1] = ['N']
                    i = raw_sent.find(ner)

            new_sent = raw_sent.split(' ')
            if len(new_sent) != len(pos_tags):
                raise Exception('Wrong went merge NE')
            new_doc.append([(new_sent[i], pos_tags[i]) for i in range(len(new_sent))])
        return ners, new_doc

    def merge_noun_phrases(self, tokenized_doc, noun_phrases=()):
        new_doc = []
        for sent in tokenized_doc:
            raw_sent = ' '.join([word for word, tag in sent]).lower()
            pos_tags = [tag for word, tag in sent]
            for np in noun_phrases:
                i = raw_sent.replace('_', ' ').find(np.replace('_', ' '))
                while i > -1 and raw_sent[i:i+len(np)].count(' ') > 0:
                    j = raw_sent.count(' ', 0, i)
                    pos_tags[j: j+raw_sent[i:i+len(np)].count(' ')+1] = ['N']
                    raw_sent = raw_sent[:i] + np.replace(' ', '_') + raw_sent[i+len(np):]
                    i = raw_sent.replace('_', ' ').find(np.replace('_', ' '), i+1)

            new_sent = raw_sent.split()
            if len(new_sent) != len(pos_tags):
                raise Exception('Wrong went merge NE')
            new_doc.append([(new_sent[i], pos_tags[i]) for i in range(len(new_sent))])
        return new_doc

    def get_most_noun_phrases(self, noun_phrases, threshold=2):
        appearances = {}
        for np in noun_phrases:
            appearances[np] = appearances.get(np, 0) + 1
        return [np for np, app in appearances.items() if app >= threshold]

    def analyse_about(self, about):
        annotated_doc = self.annotate(about)
        noun_phrases = self.get_long_tokens(annotated_doc, min_word_number=2, max_word_count=3)
        phrases = self.get_long_tokens(
            annotated_doc, pos_tags=('N', 'Np', 'Nc', 'A', 'V'),
            min_word_number=2, max_word_count=5)
        named_entities, _ = self.merge_name_entities(annotated_doc)
        return noun_phrases, phrases, named_entities

    def analyse_content(self, doc, noun_phrases_in_about):
        annotated_doc = self.annotate(doc)
        named_entities, new_doc = self.merge_name_entities(annotated_doc)
        noun_phrases = self.get_long_tokens(annotated_doc, min_word_number=2, max_word_count=4)
        popular_entity_noun_phrases = [p for p in noun_phrases if any(
            p.startswith(popular_prefix) for popular_prefix in popular_prefix_named_entity)]
        most_noun_phrases = self.get_most_noun_phrases(noun_phrases)
        merged_doc = self.merge_noun_phrases(
            new_doc, noun_phrases=popular_entity_noun_phrases + noun_phrases_in_about + most_noun_phrases)
        while len(merged_doc) > 0 and not merged_doc[0]:
            del merged_doc[0]
        return self._lemmatize(merged_doc), noun_phrases, named_entities
