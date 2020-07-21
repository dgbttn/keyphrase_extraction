import numpy as np


class TextRankModel:

    def __init__(self, damping=0.85, min_diff=1e-5, steps=10, window_size=4):
        self.damping = damping  # damping coefficient
        self.min_diff = min_diff  # convergence threshold
        self.steps = steps  # iteration steps
        self.window_size = window_size
        self.vocab = None
        self.ignored_words = []

    def set_ignored_words(self, ignored_words=()):
        self.ignored_words = ignored_words

    def _get_matrix(self, doc, doc_ignores):
        # local vocabulary of the document
        vocab = {}
        cnt = 0
        for sent in doc:
            for word in sent:
                if word not in vocab and word not in self.ignored_words and word not in doc_ignores:
                    vocab[word] = cnt
                    cnt += 1
        V = len(vocab)

        g = np.zeros((V, V), dtype='float')
        for sent in doc:
            for i, word1 in enumerate(sent):
                if word1 in self.ignored_words or word1 in doc_ignores:
                    continue
                for j in range(i+1, i+self.window_size):
                    if j >= len(sent):
                        break
                    word2 = sent[j]
                    if word2 in self.ignored_words or word2 in doc_ignores:
                        continue
                    w1, w2 = vocab[word1], vocab[word2]
                    g[w1][w2] += 1
                    g[w2][w1] += 1

        norm = np.sum(g, axis=0)
        g_norm = np.divide(g, norm, where=norm != 0)

        return g_norm, vocab

    def _analyze(self, doc, doc_ignores):
        g, local_vocab = self._get_matrix(doc, doc_ignores)

        # Init weight (pagerank values)
        V = len(local_vocab)
        if V == 0:
            return dict()
        pr = np.array([1.0/V] * V)

        for _ in range(self.steps):
            new_pr = (1 - self.damping) / V + self.damping * np.dot(g, pr)
            error_rate = sum(abs(new_pr[i]-pr[i]) for i in range(V))
            if error_rate < self.min_diff:
                break
            else:
                pr = np.array(new_pr)

        # Get weight for each node
        node_weights = {}
        for word, index in local_vocab.items():
            node_weights[word] = pr[index]

        return node_weights

    def get_keywords(self, index, doc, doc_ignores, number=10):
        node_weights = self._analyze(doc, doc_ignores)
        node_weights = sorted(node_weights.items(), key=lambda t: t[1], reverse=True)

        keywords = []
        for i, (key, value) in enumerate(node_weights):
            keywords.append((key, value))
            if i >= number:
                break
        return keywords
