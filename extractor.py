from vncorenlp import VnCoreNLP


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

    def _pos_tagging(self, text):
        pos_tagged_text = self.annotator.pos_tag(text)
        return pos_tagged_text

    def _ner(self, text):
        ner_text = self.annotator.ner(text)
        return ner_text

    def _lemmatize(self, doc, allowed_postags=('N', 'Ny', 'Np', 'V', 'M', 'Y')):
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

    def get_long_tokens(self, doc, pos_tags=('N', 'Ny', 'Np', 'Y')):
        annotated_doc = self.annotate(doc)
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
                    if len(tokens) > 1:
                        long_tokens.append(' '.join(tokens))
                    tokens = []
        return long_tokens

    def merge_name_entities(self, doc):
        annotated_doc = self.annotate(doc)
        remake_doc = [[(token.form, token.nerLabel) for token in sent] for sent in annotated_doc]
        ners = self._get_named_entities(remake_doc)
        new_doc = []
        for sent in annotated_doc:
            raw_sent = ' '.join([token.form for token in sent])
            pos_tags = [token.posTag for token in sent]
            for ner, _ in ners:
                i = raw_sent.find(ner)
                while i > -1:
                    raw_sent = raw_sent.replace(ner, ner.replace(' ', '_'), 1)
                    i = raw_sent.count(' ', 0, i)
                    pos_tags[i: i+ner.count(' ')+1] = ['N']
                    i = raw_sent.find(ner)

            new_sent = raw_sent.split(' ')
            if len(new_sent) != len(pos_tags):
                print(len(new_sent))
                print(new_sent)
                print(len(pos_tags))
                print(pos_tags)
                raise Exception('Wrong went merge NE')
            new_doc.append([(new_sent[i], pos_tags[i]) for i in range(len(new_sent))])
        return ners, self._lemmatize(new_doc)
