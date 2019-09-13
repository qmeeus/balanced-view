import operator

from api.clients import IBMTranslator


def test_ibm_translate():
    translator = IBMTranslator()
    target = translator.identify("Waar is de papegaai?", return_all=False)
    assert target == "nl"

    translated = translator.translate("The parrot is in the cage.", source="en", target=target, return_all=False)
    assert translated == "De papegaai is in de kooi."

    text = """Zaak-Epstein: Amerikaanse Justitie richt pijlen nu op Epsteins medewerkers
    De dood van Jeffrey Epstein, de van misbruik verdachte Amerikaanse miljardair die afgelopen weekend zelfmoord pleegde in zijn cel, betekent niet het einde van het onderzoek. Justitie belooft nu haar pijlen te richten op mogelijke medeplichtingen. Ook is een grondig onderzoek bevolen naar de zelfdoding van Epstein. Minister van Justitie William Barr zegt dat er "ernstige onregelmatigheden" zijn gebeurd in de gevangenis."""
    predictions = translator.identify(text, return_all=True)
    assert predictions and type(predictions) is list
    keys = ("language", "confidence")
    assert all(type(pred) is dict and all(k in pred for k in keys) for pred in predictions)
    confidences = list(map(operator.itemgetter("confidence"), predictions))
    assert abs(sum(confidences) - 1) < 1e-5
    prediction = predictions[0]["language"]
    translated = translator.translate(text, source="nl", target="en", return_all=False)
    assert translated


if __name__ == "__main__":
    import ipdb; ipdb.set_trace()
    test_ibm_translate()
