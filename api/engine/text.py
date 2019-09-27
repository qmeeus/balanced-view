import os
import os.path as p
import sys
import spacy
import numpy as np
import pandas as pd
from knapsack import knapsack
from operator import itemgetter, attrgetter
from typing import List, Dict, Optional, Any, Union, Tuple, Callable, Iterator

from api.engine.ibm_api import translator
from api.engine.articles import fetch_articles
from api.utils.logger import logger
from api.utils.patterns import Json
from api.utils.exceptions import hijack, NLPModelNotFound, TextRankError, TranslationError, BackendError


SPACY_LANG_MODELS = {
    "nl": "nl_core_news_sm",
    "en": "en_core_web_md",
    "fr": "fr_core_news_md",
}

def load_model(lang:Optional[str]=None, path:Optional[str]=None) -> Any:
    if path is None:
        if not lang:
            raise ValueError("Must provide one of language or path to model")
        elif lang not in SPACY_LANG_MODELS:
            raise NLPModelNotFound(f"Model not available for {lang}")
        path = find_model(SPACY_LANG_MODELS[lang])
    nlp = spacy.load(path)
    return nlp

def find_model(model_name:str) -> str:
    env_path = p.abspath(p.join(sys.executable, "../.."))
    path_to_modules = p.join(env_path, f"lib/python{sys.version[:3]}/site-packages")
    path_to_model = p.join(path_to_modules, model_name)
    if not p.exists(path_to_model):
        raise FileNotFoundError(path_to_model)
    model_dir = [d for d in os.listdir(path_to_model) if d.startswith(model_name)][0]
    return p.join(path_to_model, model_dir)

class TextRank:

    '''textrank graph'''
    
    INCLUDE_PART_OF_SPEECH = ['PROPN', 'NOUN']
    BOOST_ENTITIES = ["LOC", "PER", "ORG", "GPE", "PERSON", "EVENT", "PRODUCT"]
    NER_BOOST_FACTOR = 2
    MINIMUM_WORD_LENGTH = 1
    LOOKUP_WINDOW = 5

    
    def __init__(self,
                 damping_factor:Optional[float]=0.85, 
                 convergence_thresh:Optional[float]=1e-9, 
                 steps:Optional[int]=1000) -> None:

        self.damping_factor = damping_factor
        self.convergence_thresh = convergence_thresh
        self.steps = steps

    def check_is_fitted(self):
        if not hasattr(self, "keywords_"):
            raise Exception("Not Fitted: call fit or fit_transform first")

    def get_graph(self):
        self.check_is_fitted()
        return {
            "nodes": [
                {"name": lemma, "score": score}
                for lemma, score in zip(self._lemmas, self._scores)
            ],
            "links": [
                {"source": i, "target": j, "weight": self._graph[i,j]} 
                for i in range(len(self._graph)) 
                for j in range(len(self._graph))
                if self._graph[i,j] > 0
            ]
        }

    def build_graph(self, tokens:List[Tuple[str,str,str]]) -> None:

        lemmas = list(set(map(itemgetter(1), tokens)))
        k = len(lemmas)        
        self._graph = np.zeros((k,k))
        self._lemmas = lemmas

        def is_candidate(word, pos_tag):
            return (pos_tag in self.INCLUDE_PART_OF_SPEECH 
                    and len(word) > self.MINIMUM_WORD_LENGTH)

        for i, (word, lemma, pos) in enumerate(tokens):
            if is_candidate(word, pos):
                start, end = i + 1, i + 1 + self.LOOKUP_WINDOW
                for cword, clemma, cpos in tokens[start:end]:
                    if is_candidate(cword, cpos):
                        self._graph[lemmas.index(lemma), lemmas.index(clemma)] +=  1
        
    def reconstruct_phrases(self, keyword_scores:Dict[str,float], sentences:Iterator[Any]) -> Dict[str,float]:
        
        candidate_entity = lambda ent: ent.label_ in self.BOOST_ENTITIES

        def weighted_score(chunk):
                boost = (
                    self.NER_BOOST_FACTOR * sum(map(candidate_entity, chunk.ents)) / len(chunk)
                    if len(chunk.ents) 
                    and any(candidate_entity(ent) for ent in chunk.ents)
                    else 1.
                )

                return sum([
                    keyword_scores[token.text] 
                    for token in chunk 
                    if token.text in keyword_scores
                ]) / len(chunk) * boost

        for sentence in sentences:
            for chunk in sentence.noun_chunks:
                import ipdb; ipdb.set_trace()
                if chunk.root.text in keyword_scores:
                    keyword_scores[chunk.text] = weighted_score(chunk)                

        return keyword_scores

        # return {
        #     chunk.text: weighted_score(chunk)
        #     for sent in sentences for chunk in sent.noun_chunks 
        #     if chunk.root.text in keyword_scores and len(chunk) > 1
        # }

    def fit_transform(self, tokens:List[Tuple[str,str,str]], 
            sentences:Iterator[Any], 
            num_keywords:Optional[int]=None) -> List[Tuple[str,float]]:

        self.fit(tokens, sentences)
        return self.get_keywords(num_keywords)

    @hijack(TextRankError)
    def fit(self, tokens:List[Tuple[str,str,str]], sentences:Iterator[Any]) -> 'TextRank':

        pos_filter = lambda token: token[2] in self.INCLUDE_PART_OF_SPEECH
        tokens = list(filter(pos_filter, tokens))
        self.build_graph(tokens)
        self.textrank_algorithm()

        lemma2scores = dict(zip(self._lemmas, self._scores))
        self._lemma2word = l2w = {lemma: word for word, lemma, _ in tokens}
        word2scores = {l2w[lemma]: score for lemma, score in lemma2scores.items()}

        import ipdb; ipdb.set_trace()
        phrase2scores = self.reconstruct_phrases(word2scores, sentences)

        # Normalise and apply sigmoid function to the resulting scores
        weights = list(phrase2scores.values())
        mu, sigma = np.mean(weights), np.std(weights)
        norm = lambda weight: (weight - mu) / sigma
        sigmoid = lambda weight: (1 + np.exp(-weight))**(-1)
        scale = lambda weight: sigmoid(norm(weight))
        normalised_scores = {node: scale(weight) for node, weight in phrase2scores.items()}

        self.keywords_ = pd.DataFrame(normalised_scores.items(), columns=["keyword", "score"])
        self.keywords_.sort_values("score", ascending=False, inplace=True)
        import ipdb; ipdb.set_trace()
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

    def textrank_algorithm(self) -> None:

        G, d = self._graph, self.damping_factor
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

            logger.debug(f"{step} SSE:{sse(scores, newscores):.2e}")

            if sse(scores, newscores) < self.convergence_thresh:
                break

            scores = newscores

        self._scores = newscores


class TextAnalyser:

    """Extract keywords based on textrank graph algorithm"""

    MAX_KEYWORDS_TO_GET = 5

    def __init__(self, related_articles:Optional[bool]=False,
                 article_languages:Optional[str]=None,
                 output_language:Optional[str]=None,) -> None:

        self.related_articles = related_articles
        self.article_languages = article_languages or 'en,fr,nl'
        self.output_language = output_language

    def fit(self, text:str) -> 'TextAnalyser':

        self.detected_language_ = translator.identify(text, return_all=False)

        model = load_model(self.detected_language_)
        document = model(text)

        tokens = map(attrgetter('text'), document)
        lemmas = map(lambda token: token.lemma_.lower(), document)
        pos_tags = map(attrgetter('pos_'), document)
        remove_stopwords = self.remove_stopwords(model, itemgetter(0))
        features = list(filter(remove_stopwords, zip(tokens, lemmas, pos_tags)))

        self.textrank_ = TextRank()

        self.textrank_.fit(features, document.sents)

        self.articles_ = {}

        if self.related_articles:
            
            query_terms = self.textrank_.get_keywords(
                self.MAX_KEYWORDS_TO_GET, scores=False)
                
            options = dict(
                terms=",".join(query_terms), 
                source_language=self.detected_language_, 
                search_languages=self.article_languages, 
                output_language=self.output_language
                # TODO: groupby language & max results per category
            )

            self.articles_ = fetch_articles(**options)

        # dependencies = map(attrgetter('dep_'), document)
        # iob_labels = map(attrgetter('ent_iob_'), document)
        # entity_labels = map(attrgetter('ent_type_'), document)

        return self

    def to_dict(self):
        return {
            "articles": self.articles_,
            "graph": self.textrank_.get_graph(),
        }

    @staticmethod
    def remove_stopwords(model:Any, fget:Callable) -> Callable:
        stopwords = model.Defaults.stop_words
        def _remove_stopwords(item:Any) -> Any:
            return fget(item) not in stopwords
        return _remove_stopwords
