import os.path as p
import numpy as np
from gensim.models import Word2Vec, KeyedVectors
from typing import List, Optional, Any
from text.utils.analyse import load_model

def abspath(relpath):
    return p.abspath(p.join(p.dirname(__file__), "..", relpath))

def get_embeddings_file(lang:str, identifier:str) -> str:
    embeddings_file = abspath(f"embeddings/{lang}/{identifier}.txt")
    if not p.exists(embeddings_file):
        raise FileNotFoundError(embeddings_file)
    return embeddings_file


def load_word_vectors(path_to_vectors:str) -> KeyedVectors:
    binary = path_to_vectors.endswith("bin")
    return KeyedVectors.load_word2vec_format(path_to_vectors, binary=binary)


def train_word2vec(texts:List[str], 
                   path_to_vectors:Optional[str]=None, 
                   save_to:Optional[str]=None, 
                   **kwargs:Any) -> KeyedVectors:

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


def load_pretrained_model(model_name):
    path = abspath(f"embeddings/models/{model_name}")
    return load_model(path=path)
