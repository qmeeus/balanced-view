import os
import os.path as p
import sys
import operator
from collections import namedtuple, Counter
import spacy
from spacy_langdetect import LanguageDetector
from gensim.parsing import preprocessing, preprocess_string
from typing import List, Optional, Any


SPACY_LANG_MODELS = {
    "nl": "nl_core_news_sm",
    "en": "en_core_web_md",
    "fr": "fr_core_news_md",
}

DEFAULT_INCLUDE_POS = ['NOUN', 'PROPN', 'VERB']
SUBJECTS = {"nsubj", "nsubjpass", "csubj", "csubjpass", "agent", "expl"}

ENTITIES = {
    'PERSON': 'Person',     # People, including fictional
    'PER': 'Person',
    'ORG': 'Organization',  # Companies, agencies, institutions, etc.
    'GPE': 'Place',         # Countries, cities, states.
    'LOC': 'Place',
}

def load_model(lang:Optional[str]=None, path:Optional[str]=None) -> Any:
    if path is None:
        if not lang:
            raise ValueError("Must provide one of language or path to model")
        elif lang not in SPACY_LANG_MODELS:
            raise KeyError(f"Model not available for {lang}")
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


def preprocess_text(text:str, stopwords:Optional[List[str]]=None) -> List[str]:
    filters = [
        preprocessing.strip_tags,
        preprocessing.strip_punctuation,
        preprocessing.strip_multiple_whitespaces,
    ]
    tokens = preprocess_string(text, filters)
    if stopwords:
        tokens = filter_stopwords(tokens, stopwords)

    return tokens


def preprocess_many(texts:List[str], stopwords:List[str]) -> List[List[str]]:
    def _preprocess(text):
        return preprocess_text(text, stopwords)
    return list(map(_preprocess, texts))


def filter_stopwords(tokens:List[str], stopwords:List[str]) -> List[str]:
    return list(filter(lambda token: token.lower() not in stopwords, tokens))


def identify_language(text:str) -> str:
    model = load_model('en')
    model.add_pipe(LanguageDetector(), name="language_detector", last=True)

    document = model(text)
    prediction = document._.language
    print("Language identified: {language}, confidence: {score:.2%}".format(**prediction))
    lang = prediction["language"]
    return lang


# def collect_entities(entities):
#     fmap = lambda token: (token.text, token.label_)
#     cond = lambda pair: pair[1] in ENTITIES
#     pairs = list(map(fmap, entities))
#     collected = list(filter(cond, pairs))
#     return pairs, collected


# def get_object(sentence, verb):
#     raise NotImplementedError()


# def get_subject_verb_complement(sentence):
#     SVO = namedtuple("SVO", ["subject", "verb", "complement"])
#     for token in sentence:
#         if token.dep_ in SUBJECTS:
#             return SVO(
#                 subject=token.text,
#                 verb=token.head.text,
#                 complement=get_object(sentence, token.head)
#             )


# def analyse_text(content):

#     if not content:
#         return []

#     model = load_model('en')
#     model.add_pipe(LanguageDetector(), name="language_detector", last=True)

#     document = model(content)
#     prediction = document._.language
#     logger.debug("Language identified: {language}, confidence: {score:.2%}".format(**prediction))
#     lang = prediction["language"]

#     if lang != 'en':
#         model = load_model(lang)
#         document = model(content)

#     named_entities = []
#     svo_triplets = []
#     relevant_sentences = []
#     events = []
#     pos_tags = [(token.text, token.pos_) for token in document]
    
#     # TODO 01 preprocessing

#     # 02 sentence-level NER and SVO
#     for i, sentence in enumerate(document.sents):
#         entities = model(sentence.text).ents
#         entities, collected_entities = collect_entities(entities)

#         import ipdb; ipdb.set_trace()

#         if collected_entities:
#             svo_triplet = get_subject_verb_complement(sentence)
#             if svo_triplet:
#                 svo_triplets.extend(svo_triplet)
#                 named_entities.extend(collected_entities)
#                 relevant_sentences.append(entities)

#     # 03 get keywords
#     scores = TextRank().extract_keywords(pos_tags, 10)
#     keywords = list(map(operator.itemgetter(0), scores))
#     events.extend([(keyword, 'keyword') for keyword in keywords])

#     # 04 add triples to event only the word in keyword
#     events.extend([
#         (s, v)
#         for s, v, _ in svo_triplets 
#         if any(w in keywords for w in (s, v)) 
#         and all(len(w) > 1 for w in (s, v))
#     ])

#     # 05 get word frequency and add to events
#     counter = Counter([
#         word 
#         for word, pos in pos_tags 
#         if len(word) > 1 
#         and pos in DEFAULT_INCLUDE_POS
#     ])

#     word_dict = [count for count in counter.most_common()][:10]
#     events.extend([
#         (word, 'frequency') 
#         for word in counter.most_common(10)
#     ])

#     # 06 get article-level NER
#     article_entities = Counter(entities).most_common(20)
#     events.extend([
#         (entity, ENTITIES[label])
#         for entity, label in article_entities
#     ])

#     # 07 get all NER entity co-occurrence information
#     events.extend(
#         # TODO
#     )


# def clean_spaces(string):
#     for whitespace in ["\r", "\t", "\n"]:
#         string = string.replace(whitespace, '')
#     return string

# def remove_noisy(string):
#     """Remove brackets"""
#     p1 = re.compile(r'（[^）]*）')
#     p2 = re.compile(r'\([^\)]*\)')
#     return p2.sub('', p1.sub('', string))