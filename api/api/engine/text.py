import os
import os.path as p
import sys
import spacy
import numpy as np
import pandas as pd
from hashlib import md5
from knapsack import knapsack
from operator import itemgetter, attrgetter
from elasticsearch.exceptions import NotFoundError
from typing import List, Dict, Optional, Any, Union, Tuple, Callable, Iterator

from api.engine.ibm_api import translator
from api.engine.articles import fetch_articles
from api.data_provider.models import InputText
from api.utils.nlp_utils import get_model
from api.utils.logger import logger
from api.utils.patterns import Json
from api.utils.exceptions import hijack, TextRankError, TranslationError, BackendError


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

        logger.debug("Start TextRank analysis")
        pos_filter = lambda token: token[2] in self.INCLUDE_PART_OF_SPEECH
        tokens = list(filter(pos_filter, tokens))
        self.build_graph(tokens)
        self.textrank_algorithm()

        lemma2scores = dict(zip(self._lemmas, self._scores))
        self._lemma2word = l2w = {lemma: word for word, lemma, _ in tokens}
        word2scores = {l2w[lemma]: score for lemma, score in lemma2scores.items()}

        phrase2scores = self.reconstruct_phrases(word2scores, sentences)

        # Normalise and apply sigmoid function to the resulting scores
        weights = list(phrase2scores.values())
        mu, sigma = np.mean(weights), np.std(weights)
        norm = lambda weight: (weight - mu) / sigma
        sigmoid = lambda weight: (1 + np.exp(-weight))**(-1)
        scale = lambda weight: sigmoid(norm(weight))
        normalised_scores = {node: scale(weight) for node, weight in phrase2scores.items()}

        if not normalised_scores:
            raise ValueError("No keyword found! There might be something wrong with the input features.")
        
        self.keywords_ = pd.DataFrame(normalised_scores.items(), columns=["keyword", "score"])
        self.keywords_.sort_values("score", ascending=False, inplace=True)
        logger.debug(f"Top 5 keywords: {' '.join(self.keywords_.head(5)['keyword'].values)}")
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

    def __init__(self, related:Optional[bool]=False,
                 search_languages:Optional[List[str]]=None,
                 output_language:Optional[str]=None, 
                 groupby_options:Optional[Json]=None) -> None:

        self.related_articles = related
        self.article_languages = search_languages or ["en","fr", "nl"]
        self.output_language = output_language
        self.groupby_options = groupby_options

    def _fit(self, text:str) -> 'TextAnalyser':

        logger.debug("Start text analysis")
        self.detected_language_ = translator.identify(text, return_all=False)

        model = get_model(self.detected_language_)
        document = model(text)

        tokens = map(attrgetter('text'), document)
        lemmas = map(lambda token: token.lemma_.lower(), document)
        pos_tags = map(attrgetter('pos_'), document)
        remove_stopwords = self.remove_stopwords(model, itemgetter(0))
        features = list(filter(remove_stopwords, zip(tokens, lemmas, pos_tags)))
        self.textrank_ = TextRank().fit(features, document.sents)

        self.keywords_ = self.textrank_.get_keywords(max_kws=self.MAX_KEYWORDS_TO_GET, scores=True)

        # dependencies = map(attrgetter('dep_'), document)
        # iob_labels = map(attrgetter('ent_iob_'), document)
        # entity_labels = map(attrgetter('ent_type_'), document)

        return self

    def fit(self, text:str) -> 'TextAnalyser':

        text = self.clean_text(text)
        text_hash = md5(text.encode()).hexdigest()

        try:
            es_text = InputText.get(id=text_hash)
            es_text.save()
            self.detected_language_ = es_text.language
            self.keywords_ = es_text.keywords
            logger.debug("Text not processed...")

        except NotFoundError:
            self._fit(text)

            es_text = InputText(
                meta={"id": text_hash},
                body=text, 
                language=self.detected_language_, 
                keywords=self.keywords_
            )
            es_text.save()
            logger.debug(f"Text saved with id {text_hash}")

        self.articles_ = {"articles": []}
        if self.related_articles:
                            
            logger.debug(f"Find articles related to {self.keywords_}")
            options = dict(
                terms=list(map(itemgetter("keyword"),  self.keywords_)), 
                source_language=self.detected_language_, 
                search_languages=self.article_languages, 
                output_language=self.output_language,
                groupby_options=self.groupby_options,
            )

            self.articles_ = fetch_articles(**options)
        
        return self

    @staticmethod
    def clean_text(text):
        text = text.strip()
        return text

    def to_dict(self):
        return dict(
            graph=self.textrank_.get_graph() if hasattr(self, "textrank_") else {}, 
            **self.articles_
        )

    @staticmethod
    def remove_stopwords(model:Any, fget:Callable) -> Callable:
        stopwords = model.Defaults.stop_words
        def _remove_stopwords(item:Any) -> Any:
            return fget(item) not in stopwords
        return _remove_stopwords
