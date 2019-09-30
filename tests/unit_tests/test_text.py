from pprint import pformat
from api.engine.text import TextAnalyser, TextRank
from api.utils.exceptions import NLPModelNotFound
from api.utils.logger import logger
from tests.utils import load_texts


def test_analyser():
    analyser = TextAnalyser(related=False)
    assert isinstance(analyser, TextAnalyser)
    
    for _, text in load_texts():

        try:

            analyser.fit(text)
            assert hasattr(analyser, 'textrank_')
            assert isinstance(analyser.textrank_, TextRank)
            assert hasattr(analyser, 'articles_')

            output = analyser.to_dict()
            assert type(output) is dict
            assert 'articles' in output
            assert 'graph' in output

            keywords = analyser.textrank_.get_keywords(max_kws=10)
            assert type(keywords) is list
            assert all(type(kw) is dict for kw in keywords)
            logger.debug(pformat(keywords))

        except NLPModelNotFound as e:
            logger.error(e)

if __name__ == "__main__":
    test_analyser()
