from operator import itemgetter
import unittest

from api.engine.ibm_api import IBMTranslator, LanguageTranslatorV3
from api.utils.logger import logger


class TestIBMAPI(unittest.TestCase):

    def test_constructor(self):
        translator = IBMTranslator()
        self.assertIsInstance(translator, LanguageTranslatorV3)

    def test_identify(self):
        translator = IBMTranslator()
        target = translator.identify(
            "Waar is de papegaai?", return_all=False
        )
        self.assertIs(type(target), str)
        self.assertEqual(target, "nl")

    def test_translate(self):
        translator = IBMTranslator()
        preds = translator.translate(
            "The parrot is in the cage.", 
            source="en", target="nl", 
            return_all=True
        )

        self.assertIs(type(preds), list)
        self.assertTrue(all(type(pred) is dict for pred in preds))
        logger.debug(preds[0])

    def test_both(self):
        text = """Zaak-Epstein: Amerikaanse Justitie richt pijlen nu op Epsteins medewerkers
        De dood van Jeffrey Epstein, de van misbruik verdachte Amerikaanse miljardair die afgelopen weekend zelfmoord pleegde in zijn cel, betekent niet het einde van het onderzoek. Justitie belooft nu haar pijlen te richten op mogelijke medeplichtingen. Ook is een grondig onderzoek bevolen naar de zelfdoding van Epstein. Minister van Justitie William Barr zegt dat er "ernstige onregelmatigheden" zijn gebeurd in de gevangenis."""

        translator = IBMTranslator()
        predictions = translator.identify(text, return_all=True)
        self.assertTrue(bool(predictions))
        self.assertIs(type(predictions), list)
        keys = ("language", "confidence")
        self.assertTrue(all(
            type(pred) is dict 
            and all(k in pred for k in keys) 
            for pred in predictions
        ))

        confidences = list(map(itemgetter("confidence"), predictions))
        self.assertAlmostEqual(sum(confidences), 1)
        self.assertEqual(predictions[0]["language"], "nl")
        translated = translator.translate(
            text, source="nl", target="en", return_all=False
        )
        self.assertTrue(bool(translated))


if __name__ == "__main__":
    unittest.main()