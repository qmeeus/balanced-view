import pandas as pd
from summa.keywords import keywords

from api.utils.knapsack import knapsack_dp


class Summary:

    def __init__(self, language='english', stopwords=None):        
        self.language = language
        self.stopwords = stopwords

    def fit_transform(self, text):
        kwds, (self.graph_, self.lemma2words_, self.scores_) = keywords(
            text, 
            language=self.language,
            ratio=1.0, 
            split=True,
            scores=True
        )

        kwds_df = pd.DataFrame(kwds, columns=["keyword", "score"])
        kwds_df = kwds_df.sort_values("score", ascending=False)
        self.keywords_ = kwds_df
        return self.keywords_

    def fit(self, text):
        self.fit_transform(text)
        return self

    def get_graph(self):
        nodes, edges = self.graph_.nodes(), []
        for node_a, node_b in self.graph_.edges():
            if (node_b, node_a) not in edges and node_a != node_b:
                edges.append((node_a, node_b))

        def node_info(node):
            return {"name": self.lemma2words_[node][0], 
                    "token": node, 
                    "score": self.scores_[node]}

        return {
            "nodes": list(map(node_info, nodes)),
            "links": [
                {"source": nodes.index(node_a), "target": nodes.index(node_b)}
                for node_a, node_b in edges]
        }

    def get_keywords(self, max_kws=5):
        to_keep = self._keywords_to_keep(max_kws)
        return self.keywords_['keyword'].iloc[to_keep].values.tolist()

    def _keywords_to_keep(self, max_kws):
        weights = self.keywords_['keyword'].map(lambda s: len(s.split())).values.tolist()
        values = self.keywords_['score'].values.tolist()
        to_keep = knapsack_dp(values, weights, max_kws, max_kws)
        return to_keep


