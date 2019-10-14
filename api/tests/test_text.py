import unittest

from api.engine.text import TextAnalyser, TextRank
from api.utils.exceptions import NLPModelNotFound
from api.utils.logger import logger
from tests.utils import load_texts


class TestTextAnalyser(unittest.TestCase):

    def test_analyser(self):
        analyser = TextAnalyser(related=False)
        self.assertIsInstance(analyser, TextAnalyser)
        
        for _, text in load_texts():

            try:

                analyser.fit(text)
                self.assertTrue(hasattr(analyser, 'textrank_'))
                self.assertIsInstance(analyser.textrank_, TextRank)
                self.assertTrue(hasattr(analyser, 'articles_'))

                output = analyser.to_dict()
                self.assertIs(type(output), dict)
                self.assertIn('articles', output)
                self.assertIn('graph', output)

                keywords = analyser.textrank_.get_keywords(max_kws=10)
                self.assertIs(type(keywords), list)
                self.assertTrue(all(type(kw) is dict for kw in keywords))
                logger.debug(str(keywords))

            except NLPModelNotFound as e:
                logger.error(e)


if __name__ == "__main__":
    unittest.main()
