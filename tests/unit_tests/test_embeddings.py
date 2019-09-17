import os.path as p
import numpy as np
from tests.utils import load_texts
from text.utils import preprocess_text, preprocess_many, get_stopwords
from text.utils import load_word_vectors, train_word2vec, get_embeddings_file
# from text.text import Embedding

def test_preprocessing():
    texts = load_texts("dutch_texts.txt")
    first_example = list(texts)[0]
    preprocessed_first = preprocess_text(first_example)
    print(first_example)
    print(preprocessed_first)
    texts = load_texts("dutch_texts.txt")
    preprocessed_texts = preprocess_many(texts, get_stopwords("nl"))
    print(preprocessed_texts)

def test_loading():
    file = get_embeddings_file("dutch", "roularta-320")
    wv = load_word_vectors(file)
    print(np.random.choice(list(wv.vocab), size=100, replace=False))
    print(wv.get_vector("kat"))
    print(wv.most_similar("kat"))

def test_train():
    texts = preprocess_many(load_texts("dutch_texts.txt"), get_stopwords("nl"))
    wv = train_word2vec(texts, min_count=1, window=5)
    print(list(wv.vocab))
    print(wv.get_vector("president"))
    print(wv.most_similar("president"))

def test_retrain():
    texts = preprocess_many(load_texts("dutch_texts.txt"), get_stopwords("nl"))
    file = get_embeddings_file("dutch", "roularta-320")
    wv = train_word2vec(texts, file, min_count=1, window=5)
    print(list(wv.vocab))
    print(wv.get_vector("president"))
    print(wv.most_similar("president"))



# EMBEDDING_FILE = p.abspath(p.join(p.dirname(__file__), "../test_data/dutch_embeddings.txt"))

# def _test_init(embedding):
#     assert hasattr(embedding, "vectors")
#     assert type(embedding.vectors) == np.ndarray
#     assert hasattr(embedding, "word_index")
#     assert type(embedding.word_index) == np.ndarray
#     assert hasattr(embedding, "vocabulary_size")
#     assert type(embedding.vocabulary_size) == int
#     assert hasattr(embedding, "embedding_dim")
#     assert type(embedding.embedding_dim) == int

# def test_constructor():
#     embedding_dim = 20
#     vocab = ["cat", "dog", "mouse", "parrot"]    
#     vectors = np.random.normal(size=(len(vocab), embedding_dim))
#     embedding = Embedding(vectors, vocab)
#     _test_init(embedding)

# def test_load_embedding():
#     embedding = Embedding.from_file(EMBEDDING_FILE)
#     _test_init(embedding)

# def test_train_embedding():
#     texts = load_texts("dutch_texts.txt")
#     embedding = Embedding.from_texts(texts, min_count=1)
#     _test_init(embedding)

# def test_retrain_embedding():
#     texts = load_texts("dutch_texts.txt")
#     embedding = Embedding.from_texts(
#         texts, 
#         initial_weights=Embedding.WORD2VEC_FILE, 
#         size=320)
#     _test_init(embedding)
#     print(embedding.embedding_dim)
#     print(embedding.vocabulary_size)
#     print(embedding.word_index)

if __name__ == '__main__':
    import ipdb; ipdb.set_trace()
    # test_preprocessing()
    # test_loading()
    test_train()
    test_retrain()
    # test_constructor()
    # test_load_embedding()
    # test_train_embedding()
    # test_retrain_embedding()