from app.api.clients.googletranslate_api import GoogleTranslator

import ipdb; ipdb.set_trace()

translator = GoogleTranslator()
target = translator.detect_language("Waar is de papegaai?")
print(target)
translated = translator.translate("The parrot is in the cage", source_language="en", target_language=target)
print(translated)

text = """Zaak-Epstein: Amerikaanse Justitie richt pijlen nu op Epsteins medewerkers
De dood van Jeffrey Epstein, de van misbruik verdachte Amerikaanse miljardair die afgelopen weekend zelfmoord pleegde in zijn cel, betekent niet het einde van het onderzoek. Justitie belooft nu haar pijlen te richten op mogelijke medeplichtingen. Ook is een grondig onderzoek bevolen naar de zelfdoding van Epstein. Minister van Justitie William Barr zegt dat er "ernstige onregelmatigheden" zijn gebeurd in de gevangenis."""
target = translator.identify(text)
print(target)
translated = translator.translate(text, source_language="nl", target_language=target)
print(translated)