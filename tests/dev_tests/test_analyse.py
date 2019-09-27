import spacy
from spacy.lang.nl.examples import sentences
from operator import attrgetter, itemgetter

from api.engine.text import TextRank, TextAnalyser
from text.utils.analyse import load_model
from tests.utils import load_texts

print(spacy.__file__)

nlp = load_model('nl')

def test_spacy():
    for text in load_texts("texts.txt"):
        document = nlp(text)
        import ipdb; ipdb.set_trace()
        for sentence in document.sents:
            for chunk in sentence.noun_chunks:
                print(chunk.text, chunk.label_, chunk.ent_id_)


def test_pos_identifier():
    doc = nlp(sentences[0])
    print(doc.text)
    for token in doc:
        print(token.text, token.pos_, token.dep_)

def test_textrank():
    for text in load_texts("dutch_texts.txt"):
        document = nlp(text)
        tokens = map(attrgetter('text'), document)
        lemmas = map(lambda token: token.lemma_.lower(), document)
        pos_tags = map(attrgetter('pos_'), document)
        remove_stopwords = TextAnalyser.remove_stopwords(nlp, itemgetter(0))
        features = list(filter(remove_stopwords, zip(tokens, lemmas, pos_tags)))
        textrank = TextRank().fit(features, document.sents)
        ranks = textrank.get_keywords(5)
        print(ranks)

# def test_processing():
#     texts = list(load_texts("dutch_texts.txt"))
#     analyse_text(texts[0])


if __name__ == '__main__':
    # test_spacy()
    # import ipdb; ipdb.set_trace()
    # test_pos_identifier()
    test_textrank()
    # test_processing()