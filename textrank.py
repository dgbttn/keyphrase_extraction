import numpy as np 
from collections import OrderedDict

class TextRankModel(object):
    def __init__(self, damping=0.85, min_diff=1e-5, steps=10):
        self.damping = damping # damping coefficient
        self.min_diff = min_diff # convergence threshold
        self.steps = steps # iteration steps
        self.vocab = None
        self.ignore_words = None

    def init_wordbook(self, wordbook):
        if wordbook and wordbook.ignore_words:
            self.ignore_words = wordbook.ignore_words


    def __generate_vocab(self, doc):
        vocab = {}
        cnt = 0
        for sent in doc:
            for word in sent:
                if word not in vocab:
                    vocab[word] = cnt 
                    cnt += 1
        return vocab


    def __get_token_pairs(self, sentences, window_size=4):
        token_pairs = []
        for sent in sentences:
            for i, word in enumerate(sent):
                for j in range(i+1, i+window_size):
                    if j >= len(sent):
                        break
                    pair = (word, sent[j])
                    if pair not in token_pairs:
                        token_pairs.append(pair)
        return token_pairs


    def __symmetrize(self, a):
        return a + a.T - np.diag(a.diagonal())


    def __get_matrix(self, vocab, token_pairs):        
        vocab_size = len(vocab)
        g = np.zeros((vocab_size, vocab_size), dtype='float')

        for w1, w2 in token_pairs:
            i, j = vocab[w1], vocab[w2]
            g[i][j] = 1

        g = self.__symmetrize(g)

        norm = np.sum(g, axis=0)
        g_norm = np.divide(g, norm, where=norm!=0)
    
        return g_norm


    def __analyze(self, doc, window_size=4):
        vocab = self.__generate_vocab(doc)
        token_pairs = self.__get_token_pairs(doc, window_size)
        
        g = self.__get_matrix(vocab, token_pairs)

        # Init weight (pagerank values)
        pr = np.array([1] * len(vocab))

        previous_pr = 0
        for _ in range(self.steps):
            pr = (1 - self.damping) + self.damping * np.dot(g, pr)
            if abs(previous_pr - sum(pr)) < self.min_diff:
                break
            else:
                previous_pr = sum(pr)

        # Get weight for each node
        node_weights = {}
        for word, index in vocab.items():
            node_weights[word] = pr[index]
        
        return node_weights


    def get_keywords(self, doc, number=10, window_size=4):
        node_weights = self.__analyze(doc, window_size)
        node_weights = sorted(node_weights.items(), key=lambda t: t[1], reverse=True)

        keywords = []
        for i, (key, value) in enumerate(node_weights):
            keywords.append((key, str(value)))
            if i >= number:
                break
        return keywords