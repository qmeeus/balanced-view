import os
import os.path as p
import sys
import numpy as np
from typing import List, Optional, Callable, Any
import spacy
from gensim.models import Word2Vec, KeyedVectors
from gensim.parsing import preprocessing, preprocess_string



SPACY_LANG_MODELS = {
    "nl": "nl_core_news_sm",
    "en": "en_core_web_md",
}

def get_stopwords(lang:str) -> List[str]:
    if lang not in SPACY_LANG_MODELS:
        raise KeyError(f"Model not available: {lang}")
    spacy.load(find_model(SPACY_LANG_MODELS[lang]))
    return getattr(spacy.lang, lang).stop_words.STOP_WORDS


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
        # preprocessing.strip_numeric
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


def get_embeddings_file(lang:str, identifier:str) -> str:
    embeddings_file = p.join(p.dirname(__file__), "embeddings", lang, identifier + ".txt")
    if not p.exists(embeddings_file):
        raise FileNotFoundError(embeddings_file)
    return embeddings_file


def load_word_vectors(path_to_vectors:str) -> KeyedVectors:
    binary = path_to_vectors.endswith("bin")
    return KeyedVectors.load_word2vec_format(path_to_vectors, binary=binary)


def train_word2vec(texts:List[str], path_to_vectors:Optional[str]=None, save_to:Optional[str]=None, **kwargs:Any) -> KeyedVectors:

    if path_to_vectors:
        pretrained_vectors = load_word_vectors(path_to_vectors)
        kwargs.pop("size", None)
        model = Word2Vec(size=pretrained_vectors.vector_size, **kwargs)
        model.build_vocab(np.array(list(pretrained_vectors.vocab)).reshape(1, -1))
        model.intersect_word2vec_format(path_to_vectors)
        model.build_vocab(texts, update=True)
        model.train(
            texts,
            total_examples=model.corpus_count, 
            epochs=model.epochs
        )

    else:
        model = Word2Vec(texts, **kwargs)

    if save_to:
        model.save(save_to)

    return model.wv
