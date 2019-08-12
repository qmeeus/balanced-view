import shutil
import os.path as p
from ibm_watson import LanguageTranslatorV3


def parse_result(json_key):
    def parse_result_decorator(func):
        def wrapper(*args, **kwargs):
            return_best = kwargs.pop("return_best", False)
            response = func(*args, **kwargs)
            result = response.get_result()
            top_level_key = json_key + "s"
            if top_level_key in result:
                result = result[top_level_key]
                return result if not return_best else result[0][json_key]
            raise Exception("API Error: {}".format(result))
        return wrapper
    return parse_result_decorator


class IBMTranslator(LanguageTranslatorV3):

    cred_file = "ibm-credentials.env"
    version = "2018-05-01"

    def __init__(self):
        # Make sure that the credentials file is located in the home directory
        home_dir = p.expanduser("~")
        if not p.exists(p.join(home_dir, self.cred_file)):
            full_path = p.join(p.dirname(__file__), self.cred_file)
            if not p.exists(full_path):
                raise FileNotFoundError(full_path)
            shutil.copy(full_path, home_dir)

        super(IBMTranslator, self).__init__(version=self.version)

    @parse_result(json_key="language")
    def identify(self, *args, **kwargs):
        return super(IBMTranslator, self).identify(*args, **kwargs)

    @parse_result(json_key="translation")
    def translate(self, *args, **kwargs):
        return super(IBMTranslator, self).translate(*args, **kwargs)
        

if __name__ == "__main__":
    translator = IBMTranslator()
    target = translator.identify("Waar is de papegaai?", return_best=True)
    print(target)
    translated = translator.translate("The parrot is in the cage", source="en", target=target, return_best=True)
    print(translated)
