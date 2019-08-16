from app.api.clients import IBMTranslator


translator = IBMTranslator()
target = translator.identify("Waar is de papegaai?", return_all=False)
print(target)
translated = translator.translate("The parrot is in the cage", source="en", target=target, return_all=False)
print(translated)

text = """Zaak-Epstein: Amerikaanse Justitie richt pijlen nu op Epsteins medewerkers
De dood van Jeffrey Epstein, de van misbruik verdachte Amerikaanse miljardair die afgelopen weekend zelfmoord pleegde in zijn cel, betekent niet het einde van het onderzoek. Justitie belooft nu haar pijlen te richten op mogelijke medeplichtingen. Ook is een grondig onderzoek bevolen naar de zelfdoding van Epstein. Minister van Justitie William Barr zegt dat er "ernstige onregelmatigheden" zijn gebeurd in de gevangenis."""
target = translator.identify(text, return_all=True)
print(target)
translated = translator.translate(text, source="nl", target=target, return_all=False)
print(translated)