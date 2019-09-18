import os.path as p
import numpy as np

from text.utils.analyse import preprocess_text, preprocess_many, load_model
from text.utils.embeddings import load_word_vectors, train_word2vec, get_embeddings_file
from tests.utils import load_texts


NL_STOPWORDS = load_model("nl").Defaults.stop_words


def test_preprocessing():
    texts = load_texts("dutch_texts.txt")
    first_example = list(texts)[0]
    preprocessed_first = preprocess_text(first_example)
    print(first_example)
    print(preprocessed_first)
    texts = load_texts("dutch_texts.txt")
    preprocessed_texts = preprocess_many(texts, NL_STOPWORDS)
    print(preprocessed_texts)


def test_loading():
    file = get_embeddings_file("dutch", "roularta-320")
    wv = load_word_vectors(file)
    print(np.random.choice(list(wv.vocab), size=100, replace=False))
    print(wv.get_vector("kat"))
    print(wv.most_similar("kat"))


def test_train():
    texts = preprocess_many(load_texts("dutch_texts.txt"), NL_STOPWORDS)
    wv = train_word2vec(texts, min_count=1, window=5)
    print(list(wv.vocab))
    print(wv.get_vector("president"))
    print(wv.most_similar("president"))


def test_retrain():
    texts = preprocess_many(load_texts("dutch_texts.txt"), NL_STOPWORDS)
    file = get_embeddings_file("dutch", "roularta-320")
    wv = train_word2vec(texts, file, min_count=1, window=5)
    print(list(wv.vocab))
    print(wv.get_vector("president"))
    print(wv.most_similar("president"))


if __name__ == '__main__':
    import ipdb; ipdb.set_trace()
    test_preprocessing()
    test_loading()
    test_train()
    test_retrain()
