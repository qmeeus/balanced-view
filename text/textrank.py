import sys
from operator import itemgetter, attrgetter
from collections import defaultdict
import numpy as np
import pandas as pd
from knapsack import knapsack
from typing import List, Dict, Optional, Any, Union, Tuple, Callable, Iterator

from text.utils.analyse import identify_language, load_model

Json = Dict[str,Any]

class TextRank:

    '''textrank graph'''
    
    INCLUDE_PART_OF_SPEECH = ['PROPN', 'NOUN', 'VERB']
    BOOST_ENTITIES = ["LOC", "PER", "ORG", "GPE", "PERSON", "EVENT", "PRODUCT"]
    MINIMUM_WORD_LENGTH = 1
    LOOKUP_WINDOW = 5

    
    def __init__(self,
                 damping_factor:Optional[float]=0.85, 
                 convergence_thresh:Optional[float]=1e-5, 
                 steps:Optional[int]=1000) -> None:

        self.damping_factor = damping_factor
        self.convergence_thresh = convergence_thresh
        self.steps = steps

    def check_is_fitted(self):
        if not hasattr(self, "keywords_"):
            raise Exception("Not Fitted: call fit or fit_transform first")

    def get_graph(self):
        self.check_is_fitted()
        nodes2index = {node: i for i, node in enumerate(self.graph_)}
        return {
            "nodes": [
                {"name": node, "score": score}
                for _, (node, score) in self.keywords_.iterrows()
            ],
            "links": [
                {"source": nodes2index[source], "target": nodes2index[target], "weight": weight} 
                for source, target, weight in self.graph_.values()
            ]
        }

    def build_graph(self, edge_counts:Dict[Tuple[str,str],int]) -> None:
        self.graph_ = defaultdict(list)
        for (node_from, node_to), weight in edge_counts.items():
            self.graph_[node_from].append((node_from, node_to, weight))
            # self.graph_[node_to].append((node_to, node_from, weight))
        # Remove unreachable nodes (no link to them)
        # self.graph_ = dict(filter(lambda it: len(it[1]), self.graph_.items()))

    def reconstruct_phrases(self, keyword_scores:Dict[str,float], sentences:Iterator[Any]) -> Dict[str,float]:
        
        def weighted_score(chunk):
            return sum([
                keyword_scores[token.text] * (2 if token.ent_type_ in self.BOOST_ENTITIES else 1)
                for token in chunk 
                if token.text in keyword_scores
            ]) / len(chunk)

        return {
            chunk.text: weighted_score(chunk)
            for sent in sentences for chunk in sent.noun_chunks 
            if chunk.root.text in keyword_scores and len(chunk) > 1
        }

    def fit_transform(self, tokens:List[Tuple[str,str,str]], 
            sentences:Iterator[Any], 
            num_keywords:Optional[int]=None) -> List[Tuple[str,float]]:

        self.fit(tokens, sentences)
        return self.get_keywords(num_keywords)

    def fit(self, tokens:List[Tuple[str,str,str]], sentences:Iterator[Any]) -> 'TextRank':

        def is_candidate(word, pos_tag):
            return (pos_tag in self.INCLUDE_PART_OF_SPEECH 
                    and len(word) > self.MINIMUM_WORD_LENGTH)

        cm = defaultdict(int)
        for i, (word, lemma, pos) in enumerate(tokens):
            if is_candidate(word, pos):
                start, end = i + 1, i + 1 + self.LOOKUP_WINDOW
                for cword, clemma, cpos in tokens[start:end]:
                    if is_candidate(cword, cpos):
                        cm[(lemma, clemma)] +=  1

        self.build_graph(cm)
        import ipdb; ipdb.set_trace()

        weight_default = 1.0 / (len(self.graph_) or 1.0)     # initialize weight
        nodeweight_dict = defaultdict(float)                # store weight of node
        outsum_node_dict = defaultdict(float)               # store wegiht of out nodes

        for node, out_edges in self.graph_.items():         # initilize nodes weight by edges
            nodeweight_dict[node] = weight_default
            outsum_node_dict[node] = sum((w for (_, _, w) in out_edges), 0.0) # if no out edge, set weight 0

        # Trade off random jump vs. follow link
        norm = lambda score: (1 - self.damping_factor) + self.damping_factor * score

        def update_scores(node_dict):
            return {
                node: norm(sum(
                    weight * node_dict[cword] / outsum_node_dict[cword] 
                    for (word, cword, weight) in edges_from
                )) for node, edges_from in self.graph_.items()
            }
        
        step, history = 0, []
        while step < self.steps:
            nodeweight_dict = update_scores(nodeweight_dict)
            history.append(sum(nodeweight_dict.values()))
            if step > 1 and abs(history[step] / history[step - 1] - 1) < self.convergence_thresh:
                break
            step += 1

        lemma2word = {lemma: word for word, lemma, _ in tokens}
        nodeweight_dict = {lemma2word[lemma]: score for lemma, score in nodeweight_dict.items()}

        noun_chunks = self.reconstruct_phrases(nodeweight_dict, sentences)
        nodeweight_dict = dict(**nodeweight_dict, **noun_chunks)

        # Normalise and apply sigmoid function to the resulting scores
        weights = list(nodeweight_dict.values())
        mu, sigma = np.mean(weights), np.std(weights)
        norm = lambda weight: (weight - mu) / sigma
        sigmoid = lambda weight: (1 + np.exp(-weight))**(-1)
        scale = lambda weight: sigmoid(norm(weight))
        nodeweight_dict = {node: scale(weight) for node, weight in nodeweight_dict.items()}

        self.keywords_ = pd.DataFrame(nodeweight_dict.items(), columns=["keyword", "score"])
        self.keywords_.sort_values("score", ascending=False, inplace=True)
        return self

    def get_keywords(self, max_kws:Optional[int]=None, scores:Optional[bool]=True) -> Union[List[Json],List[str]]:
        to_keep = self._keywords_to_keep(max_kws) if max_kws else range(len(self.keywords_))
        keywords = self.keywords_.iloc[to_keep]
        if scores:
            return list(keywords.T.to_dict().values())
        return keywords['keyword'].values.tolist()

    def _keywords_to_keep(self, max_kws:int) -> List[int]:
        lengths = self.keywords_['keyword'].map(lambda s: len(s.split())).values.tolist()
        weights = self.keywords_['score'].values.tolist()
        _, to_keep = knapsack(lengths, weights).solve(max_kws)
        return to_keep

    @staticmethod
    def textrank_algorithm(G, d=0.8):

        k = len(G)
        outgoing = G.sum(0)
        scores = np.ones((k,)) * 1/k
        sse = lambda x, y: ((x - y)**2).sum()

        for step in range(10):

            newscores = np.empty((k,))
            for j in range(k):
                newscores[j] = d / k + (1-d) * np.sum([
                    scores[l] / outgoing[l] 
                    for l in range(k) 
                    if l != j and G[j,l] != 0
                ])

            print(f"{step} SSE:{sse(scores, newscores):.2e}, {newscores}")
            scores = newscores

        return scores


class TextAnalyser:
    """Extract keywords based on textrank graph algorithm"""

    def __init__(self, 
                 lang:Optional[str]=None,
                 min_length:Optional[int]=1, 
                 span:Optional[int]=5) -> None:

        self.lang = lang
        self.min_length = min_length
        self.span = span

    def fit(self, text:str) -> List[Tuple[str,str]]:
        if not self.lang:
            self.lang = identify_language(text)
        model = load_model(self.lang)
        document = model(text)

        tokens = map(attrgetter('text'), document)
        lemmas = map(lambda token: token.lemma_.lower(), document)
        pos_tags = map(attrgetter('pos_'), document)
        remove_stopwords = self.remove_stopwords(model, itemgetter(0))
        features = list(filter(remove_stopwords, zip(tokens, lemmas, pos_tags)))
        
        self.textrank = TextRank()
        self.keywords_ = self.textrank.fit_transform(features, document.sents)
        import ipdb; ipdb.set_trace()
        # dependencies = map(attrgetter('dep_'), document)
        # iob_labels = map(attrgetter('ent_iob_'), document)
        # entity_labels = map(attrgetter('ent_type_'), document)
        return self

    def to_dict(self):
        return {
            "keywords": self.keywords_,
            "graph": self.textrank.get_graph(),
        }

    @staticmethod
    def remove_stopwords(model:Any, fget:Callable) -> Callable:
        stopwords = model.Defaults.stop_words
        def _remove_stopwords(item:Any) -> Any:
            return fget(item) not in stopwords
        return _remove_stopwords