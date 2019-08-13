import pandas as pd
from summa.keywords import keywords


class Summary:


    def __init__(self, text, language='english', stopwords=None):        
        self.language = language
        self.stopwords = stopwords
        self.keywords, self.graph, self.lemma2words, self.scores = \
            self._process_text(text)

    def get_graph(self, min_kws=3, max_kws=5, min_score=.05):
        nodes, edges = self.graph.nodes(), []
        for node_a, node_b in self.graph.edges():
            if (node_b, node_a) not in edges and node_a != node_b:
                edges.append((node_a, node_b))

        def node_info(node):
            return {"name": self.lemma2words[node][0], 
                    "token": node, 
                    "score": self.scores[node]}

        return {
            "nodes": list(map(node_info, nodes)),
            "links": [
                {"source": nodes.index(node_a), "target": nodes.index(node_b)}
                for node_a, node_b in edges]
        }

    def get_keywords(self, min_kws=3, max_kws=5, min_score=.05):
        filters = (min_kws, max_kws, min_score)
        to_keep = self._num_keywords_to_keep(*filters)
        if to_keep < 1:
            msg = "min_kws: {}, max_kws: {}, min_score: {}".format(*filters)
            raise Exception("Filter is too strict: {}".format(msg))    
        return " ".join(self.keywords['keyword'].head(to_keep).values)

    def _process_text(self, text):
        kwds, (graph, l2w, scores) = keywords(
            text, 
            language=self.language,
            ratio=1.0, 
            split=True,
            scores=True
        )

        kwds_df = pd.DataFrame(kwds, columns=["keyword", "score"])
        kwds_df = kwds_df.sort_values("score", ascending=False)
        return kwds_df, graph, l2w, scores

    def _num_keywords_to_keep(self, min_kws, max_kws, min_score):
        # FIXME
        n_sufficient_score = (self.keywords["score"] > min_score).sum()
        n_words = self.keywords['keyword'].map(lambda s: len(s.split()))
        return max(min(n_sufficient_score, min_kws), max_kws)

