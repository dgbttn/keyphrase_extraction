import string
import re
from vncorenlp import VnCoreNLP

from preprocessing import preprocessing

ORGANIZATION = 'ORG'
PERSON = 'PER'
LOCATION = 'LOC'

NER_TAGS = [ORGANIZATION, PERSON, LOCATION]

class Selector:

    def __init__(self):
        self.annotator = VnCoreNLP('VnCoreNLP-1.1.1.jar', annotators="wseg,pos,ner,parse", max_heap_size='-Xmx2g')
        self.endline = ('.', 'O')

    def pos_tagging(self, text):
        pos_tagged_text = self.annotator.pos_tag(text)
        return pos_tagged_text

    def ner(self, text):
        ner_text = self.annotator.ner(text)
        old_tag = ''
        entity_segments = []
        entities = []
        for sent in ner_text:
            sent.append(self.endline)
            for word, tag in sent:
                # not a segment of a named entity
                if len(tag)<3 or tag[-3:] not in NER_TAGS:
                    if entity_segments:
                        entity = ' '.join(entity_segments).replace('_', ' ')
                        entities.append((entity, old_tag))
                        entity_segments = []
                        old_tag = ''
                    continue

                # is a segment of a named entity
                tag = tag[-3:]
                if tag != old_tag:
                    if entity_segments:
                        entity = ' '.join(entity_segments).replace('_', ' ')
                        entities.append((entity, old_tag))
                        entity_segments = []
                    
                old_tag = tag 
                entity_segments.append(word)
        
        return list(set(entities))

    @staticmethod
    def lemmatize(doc, allowed_postags=['N', 'Ny', 'Np', 'V', 'Z']):
        sentences = []
        for sent in doc:
            new_sent = [word.lower() for (word, tag) in sent if tag in allowed_postags]
            sentences.append(new_sent)
        return sentences

    def get_candidates(self, text):
        clear_text = preprocessing(text)

        pos_tagged_text = self.pos_tagging(clear_text)
        candidates = self.lemmatize(pos_tagged_text)

        return candidates