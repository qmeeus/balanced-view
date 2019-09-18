import spacy
from spacy.lang.nl.examples import sentences


from text.textrank import TextRank
from text.utils.analyse import load_model
from tests.utils import load_texts


nlp = load_model('nl')


def test_pos_identifier():
    doc = nlp(sentences[0])
    print(doc.text)
    for token in doc:
        print(token.text, token.pos_, token.dep_)

def test_textrank():
    textrank = TextRank(lang='nl')
    for text in load_texts("dutch_texts.txt"):
        ranks = textrank.extract_keywords(text, 5)
        print(ranks)

# def test_processing():
#     texts = list(load_texts("dutch_texts.txt"))
#     analyse_text(texts[0])


if __name__ == '__main__':
    # import ipdb; ipdb.set_trace()
    # test_pos_identifier()
    test_textrank()
#     test_processing()