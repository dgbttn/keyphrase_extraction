from vncorenlp import VnCoreNLP

ORGANIZATION = 'ORG'
PERSON = 'PER'
LOCATION = 'LOC'

NER_TAGS = [ORGANIZATION, PERSON, LOCATION]

class Annotator:

    anno = VnCoreNLP('VnCoreNLP-1.1.1.jar', annotators="wseg,pos,ner,parse", max_heap_size='-Xmx2g')

    endline = ('.', 'O')

    def pos_tagging(self, text):
        annotated_text = self.anno.annotate(text)
        doc = annotated_text['sentences']
        sentences = []
        for sent in doc:
            new_sent = [(w['form'], w['posTag']) for w in sent]
            sentences.append(new_sent)
        return sentences

    def ner(self, text):
        ner_text = self.anno.ner(text)
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



annotator = Annotator()