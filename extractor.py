import string
import re
from vncorenlp import VnCoreNLP

from preprocessing import preprocessing

ORGANIZATION = 'ORG'
PERSON = 'PER'
LOCATION = 'LOC'

NER_TAGS = [ORGANIZATION, PERSON, LOCATION]

class Extractor:

    def __init__(self):
        print('Init VnCoreNLP Annotator...')
        self.annotator = VnCoreNLP('VnCoreNLP-1.1.1.jar', annotators="wseg,pos,ner,parse", max_heap_size='-Xmx2g')

    def __pos_tagging(self, text):
        pos_tagged_text = self.annotator.pos_tag(text)
        return pos_tagged_text

    def __ner(self, text):
        ner_text = self.annotator.ner(text)
        return ner_text

    def __lemmatize(self, doc, allowed_postags=['N', 'Ny', 'Np', 'V', 'Z']):
        sentences = []
        for sent in doc:
            new_sent = [word.lower() for (word, tag) in sent if tag in allowed_postags]
            sentences.append(new_sent)
        return sentences

    def __get_named_entities(self, text):
        endline = ('.', 'O')
        old_tag = ''
        entity_segments = []
        entities = []

        for sent in text:
            sent.append(endline)
            for word, tag in sent:
                # not a segment of a named entity
                if len(tag)<3 or tag[-3:] not in NER_TAGS:
                    if entity_segments:
                        entity = ' '.join(entity_segments).replace('_', ' ')
                        if (entity, old_tag) not in entities:
                            entities.append((entity, old_tag))
                        entity_segments = []
                        old_tag = ''
                    continue

                # is a segment of a named entity
                tag = tag[-3:]
                if tag != old_tag:
                    if entity_segments:
                        entity = ' '.join(entity_segments).replace('_', ' ')
                        if (entity, old_tag) not in entities:
                            entities.append((entity, old_tag))
                        entity_segments = []
                    
                old_tag = tag 
                entity_segments.append(word)
        
        return entities

    def extract(self, text):
        clear_text = preprocessing(text)
        
        annotated_text = self.annotator.annotate(clear_text)
        ner_text = [[(word['form'], word['nerLabel']) for word in sent] for sent in annotated_text['sentences']]
        pos_tagged_text = [[(word['form'], word['posTag']) for word in sent] for sent in annotated_text['sentences']]

        return self.__get_named_entities(ner_text), self.__lemmatize(pos_tagged_text)