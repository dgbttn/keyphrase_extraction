from vncorenlp import VnCoreNLP
from wordbook import popular_prefix_named_entity


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

    def _lemmatize(self, doc, allowed_postags=('N', 'Ny', 'Np', 'V', 'M', 'Y', 'A')):
        sentences = []
        for sent in doc:
            new_sent = [word.lower() for (word, tag) in sent if tag in allowed_postags]
            sentences.append(new_sent)
        return sentences

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
                        if (entity, old_tag) not in entities:
                            entities.append((entity, old_tag))
                        entity_segments = []
                        old_tag = ''
                    continue

                # is a segment of a named entity
                tag = tag[-3:]
                if tag != old_tag:
                    if entity_segments:
                        entity = ' '.join(entity_segments)
                        if (entity, old_tag) not in entities:
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
            self, annotated_doc, pos_tags=('N', 'Ny', 'Np', 'Y', 'M', 'Z', 'A'),
            min_word_number=2, max_word_count=20):
        eos = Token('.', '.', '.')  # end of sentence
        long_tokens = []
        tokens = []
        for sent in annotated_doc:
            tokens = []
            sent += [eos]
            for token in sent:
                if token.posTag in pos_tags:
                    tokens.append(token.form)
                else:
                    if len(tokens) > min_word_number and len(tokens) < max_word_count:
                        long_tokens.append(' '.join(tokens))
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
        return ners, self._lemmatize(new_doc)

    def merge_popular_noun_phrases(self, tokenized_doc, noun_phrases=()):
        new_doc = []
        for sent in tokenized_doc:
            raw_sent = ' '.join(sent).lower()
            for np in noun_phrases:
                np = np.lower()
                raw_sent = raw_sent.replace(np, np.replace(' ', '_'))
            new_sent = raw_sent.split(' ')
            new_doc.append(new_sent)
        return new_doc

    def analyse_about(self, about):
        annotated_doc = self.annotate(about)
        noun_phrases = self.get_long_tokens(annotated_doc)
        phrases = self.get_long_tokens(annotated_doc, pos_tags=('N, A, V'), min_word_number=3)
        named_entities, _ = self.merge_name_entities(annotated_doc)
        return noun_phrases, phrases, named_entities

    def analyse_content(self, doc):
        annotated_doc = self.annotate(doc)
        noun_phrases = self.get_long_tokens(annotated_doc)
        named_entities, tokenized_doc = self.merge_name_entities(annotated_doc)
        popular_noun_phrases = {p for p in noun_phrases if any(
            popular_prefix in p for popular_prefix in popular_prefix_named_entity)}
        merged_doc = self.merge_popular_noun_phrases(tokenized_doc, noun_phrases=popular_noun_phrases)
        return merged_doc, noun_phrases, named_entities
