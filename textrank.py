import numpy as np 
from collections import OrderedDict

class TextRankModel(object):
    def __init__(self, vocab, damping=0.85, min_diff=1e-5, steps=10):
        self.vocab = vocab
        self.damping = damping # damping coefficient
        self.min_diff = min_diff # convergence threshold
        self.steps = steps # iteration steps

    @staticmethod
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

    @staticmethod
    def __symmetrize(self, a):
        return a + a.T - np.diag(a.diagonal())

    @staticmethod
    def __get_matrix(self, token_pairs):        
        vocab_size = len(self.vocab)
        g = np.zeros((vocab_size, vocab_size), dtype='float')

        for w1, w2 in token_pairs:
            i, j = self.vocab[w1], self.vocab[w2]
            g[i][j] = 1

        g = self.__symmetrize(g)

    @staticmethod
    def __analyze(self, doc, window_size=4):
        token_pairs = self.__get_token_pairs(doc, window_size)
        
        g = self.__get_matrix(token_pairs)

        # Init weight (pagerank values)
        pr = np.array([1] * len(self.vocab))

        previous_pr = 0
        for epoch in range(self.steps):
            pr = (1 - self.damping) + self.damping * np.dot(g, pr)
            if abs(previous_pr - sum(pr)) < self.min_diff:
                break
            else:
                previous_pr = sum(pr)

        # Get weight for each node
        node_weights = {}
        for word, index in self.vocab.items():
            node_weights[word] = pr[index]
        
        return node_weights


    def get_keywords(self, doc, number=10, window_size=4):
        node_weights = self.__analyze(doc, window_size)
        node_weights = OrderedDict(sorted(node_weights.items(), key=lambda t: t[1]), reverse=True)

        keywords = []
        for i, (key, value) in enumerate(node_weights.items()):
            keywords.append(key + ' - ' + str(value))
            if i >= number:
                break
        return keywords