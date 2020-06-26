import numpy as np
from gensim import corpora, models


class LDAModel:

    def __init__(self, wordbook_corpora):
        input_corpora = [content.tokenized_text for about, content in wordbook_corpora]
        self.flatted_corpora = [[word for sent in corpus for word in sent] for corpus in input_corpora]
        self.dictionary = corpora.Dictionary(self.flatted_corpora)
        # self.dictionary.filter_extremes(no_below=2, no_above=0.65)
        self.bow_corpora = [self.dictionary.doc2bow(doc) for doc in self.flatted_corpora]
        self.model = None

    def init_model(self, num_topics=100):
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

    def _generate_vocab(self, doc):
        vocab = {}
        cnt = 0
        for sent in doc:
            for word in sent:
                if word not in vocab:
                    vocab[word] = cnt
                    cnt += 1
        return vocab

    def _get_token_pairs(self, doc):
        token_pairs = []
        for sent in doc:
            for i, word in enumerate(sent):
                for j in range(i+1, i+self.window_size):
                    if j >= len(sent):
                        break
                    pair = (word, sent[j])
                    if pair not in token_pairs:
                        token_pairs.append(pair)
        return token_pairs

    def _symmetrize(self, a):
        return a + a.T - np.diag(a.diagonal())

    def _get_matrix(self, vocab, token_pairs):
        vocab_size = len(vocab)
        g = np.zeros((vocab_size, vocab_size), dtype='float')

        for w1, w2 in token_pairs:
            i, j = vocab[w1], vocab[w2]
            g[i][j] = 1

        g = self._symmetrize(g)

        norm = np.sum(g, axis=0)
        g_norm = np.divide(g, norm, where=norm != 0)

        return g_norm

    def _analyze(self, doc, topic_id):
        local_vocab = self._generate_vocab(doc)
        token_pairs = self._get_token_pairs(doc)
        g = self._get_matrix(local_vocab, token_pairs)

        # Init weight (pagerank values)
        V = len(local_vocab)
        start_state = [1.0/V] * V
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
                new_pr[i] = (1-self.damping) * start_state[i] + self.damping * sum(g[i][k]*pr[k] for k in range(V))

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

    def get_keywords(self, doc_idx, doc, number=10):
        doc = [[w for w in sent if w not in self.ignored_words] for sent in doc]
        doc_bow = self.lda_model.get_doc_bow(doc_idx)
        topics = self.lda_model.get_topics(doc_bow)

        weights = []
        topic_values = []

        for topic_id, value in topics:
            node_weights = self._analyze(doc, topic_id)
            weights.append(node_weights)
            topic_values.append(value)

        # compute final weights
        final_score = {}
        vocab = node_weights[0].keys()
        for word in vocab:
            final_score[word] = sum(weights[i][word] * topic_values[i] for i in range(len(topics)))

        final_score = sorted(final_score.items(), key=lambda item: item[1], reverse=True)

        keywords = []
        for i, (key, value) in enumerate(final_score):
            keywords.append((key, str(value)))
            if i >= number:
                break
        return keywords
