import numpy as np
from gensim import corpora, models


class LDAModel:

    def __init__(self, input_corpora):
        print('Init LDA...')
        self.flatted_corpora = [[word for sent in corpus for word in sent] for corpus in input_corpora]
        self.dictionary = corpora.Dictionary(self.flatted_corpora)
        # self.dictionary.filter_extremes(no_below=2, no_above=0.65)
        self.bow_corpora = [self.dictionary.doc2bow(doc) for doc in self.flatted_corpora]
        self.model = None

    def init_model(self, num_topics=100):
        print('Setup LDA model...')
        self.model = models.LdaModel(
            corpus=self.bow_corpora,
            num_topics=num_topics,
            id2word=self.dictionary,
            chunksize=100,
            passes=10,
            gamma_threshold=1e-5
        )

    def get_doc_bow(self, idx):
        """ Return BOW form of document by its `idx` index. """
        return self.bow_corpora[idx]

    def get_topics(self, bow):
        """ 
        Return list of (int, float)
        Each element is topic id and its probability of BOW document
        """
        topics = self.model[bow]
        sum_value = sum([value for idx, value in topics])
        for i, topic in enumerate(topics):
            idx, value = topic
            topics[i] = (idx, value/sum_value)
        return topics

    def word2id(self, word):
        return self.dictionary.token2id[word]

    def get_topic_given_term(self, topic_id, term):
        """ 
        Return p(z|w): 
            - topic z
            - given word w
        """

        topic_distribution = self.model.get_term_topics(word_id=term)
        return next(filter(lambda topic: topic[0] == topic_id, topic_distribution), (0, -1))[1]


class TopicalPageRank:

    def __init__(self, window_size=4, damping=0.85, min_diff=1e-6, steps=20):
        self.damping = damping  # damping coefficient
        self.window_size = window_size  # sliding window size
        self.min_diff = min_diff  # convergence threshold
        self.steps = steps  # iteration steps
        self.lda_model = None
        self.ignored_words = []

    def set_extensions(self, lda_model, ignored_words=()):
        self.lda_model = lda_model
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

    def _analyze(self, doc, doc_ignores, topic_id):
        g, local_vocab = self._get_matrix(doc, doc_ignores)

        # Init weight (pagerank values)
        V = len(local_vocab)
        if V == 0:
            return dict()
        # pagerank
        start_state = [1.0/V] * V
        # topical pagerank
        for word, idx in local_vocab.items():
            start_state[idx] = self.lda_model.get_topic_given_term(topic_id, word)
        real_sum = sum(filter(lambda x: x > 0, start_state))
        negative_count = len([score for score in start_state if score <= 0])
        if real_sum < 1:
            for i in range(V):
                if start_state[i] <= 0:
                    start_state[i] = (1-real_sum)/negative_count
        pr = np.array(start_state)

        for _ in range(self.steps):
            new_pr = [1] * V
            for i in range(V):
                new_pr[i] = (1-self.damping) * start_state[i] + self.damping * sum(g[i][j]*pr[j] for j in range(V))

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

    def get_keywords(self, doc_idx, doc, doc_ignores=(), number=10):
        doc_bow = self.lda_model.get_doc_bow(doc_idx)
        topics = self.lda_model.get_topics(doc_bow)
        if len(topics) == 0:
            return []

        weights = []
        topic_values = []

        for topic_id, value in topics:
            node_weights = self._analyze(doc, doc_ignores, topic_id)
            weights.append(node_weights)
            topic_values.append(value)

        # compute final weights
        final_score = {}
        vocab = weights[0].keys()
        for word in vocab:
            final_score[word] = sum(weights[i][word] * topic_values[i] for i in range(len(topics)))

        final_score = sorted(final_score.items(), key=lambda item: item[1], reverse=True)

        keywords = []
        for i, (key, value) in enumerate(final_score):
            keywords.append((key, value))
            if i >= number:
                break
        return keywords
