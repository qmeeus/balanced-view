import shutil
import os.path as p
from ibm_watson import LanguageTranslatorV3
from api.utils.logger import logger

def parse_result(json_key):
    def parse_result_decorator(func):
        def wrapper(*args, **kwargs):
            logger.info(f"{func.__name__.title()} language: {args[1:]} {kwargs}")
            return_all = kwargs.pop("return_all", True)
            response = func(*args, **kwargs)
            result = response.get_result()
            top_level_key = json_key + "s"
            if top_level_key in result:
                result = result[top_level_key]
                prediction = result[0]
                if "confidence" in prediction:
                    logger.debug("Confidence: {confidence}".format(**prediction))
                return result if return_all else prediction[json_key]
            raise Exception("API Error: {}".format(result))
        return wrapper
    return parse_result_decorator


class IBMTranslator(LanguageTranslatorV3):

    cred_file = "resources/ibm-credentials.env"
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
