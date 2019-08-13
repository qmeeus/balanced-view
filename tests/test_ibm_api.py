from app.api.clients import IBMTranslator


translator = IBMTranslator()
target = translator.identify("Waar is de papegaai?", return_best=True)
print(target)
translated = translator.translate("The parrot is in the cage", source="en", target=target, return_best=True)
print(translated)