import shutil
import os.path as p
import os
from ibm_watson import LanguageTranslatorV3
from typing import Callable, Any, Union, Dict, List
from api.utils.logger import logger
from api.utils.exceptions import hijack, TranslationError
from api.utils.patterns import Json


def index(items:List[Json], key:str, value:str) -> int:
    for i, item in enumerate(items):
        if item[key] == value:
            return i
    raise KeyError(f"{key}={value}")

def merge_languages(predictions:Json) -> Json:
    """ 
    This is a workaround for a rather annoying habit of IBM translate to misclassify
    extremely similar languages, for example Africaans for Dutch and Haitian for French
    """
    merges = [("nl", "af"), ("fr", "ht")]
    for target, source in merges:
        target_index = index(predictions, "language", target)
        source_index = index(predictions, "language", source)
        predictions[target_index]["confidence"] += \
            predictions.pop(source_index)["confidence"]
    return predictions


@hijack(TranslationError)
def parse_result(json_key:str) -> Callable:
    def parse_result_decorator(func:Callable) -> Callable:
        def wrapper(*args:Any, **kwargs:Any) -> Union[Json, List[Json]]:
            logger.info(f"{func.__name__.title()}: {args[1:]} {kwargs}")
            return_all = kwargs.pop("return_all", True)
            response = func(*args, **kwargs)
            result = response.get_result()
            top_level_key = json_key + "s"
            if top_level_key in result:
                predictions = result[top_level_key]
                prediction = predictions[0]
                if "confidence" in prediction:
                    logger.debug("Language: {language} Confidence: {confidence:.2%}".format(**prediction))
                    predictions = merge_languages(predictions)
                return predictions if return_all else predictions[0][json_key]
            raise Exception("API Error: {}".format(result))
        return wrapper
    return parse_result_decorator


class IBMTranslator(LanguageTranslatorV3):

    cred_file = "../resources/ibm-credentials.env"
    version = "2018-05-01"

    def __init__(self):
        # Make sure that the credentials file location is known
        os.environ["IBM_CREDENTIALS_FILE"] = p.join(p.dirname(__file__), self.cred_file)
        super(IBMTranslator, self).__init__(version=self.version)

    @parse_result(json_key="language")
    def identify(self, *args, **kwargs):
        return super(IBMTranslator, self).identify(*args, **kwargs)

    @parse_result(json_key="translation")
    def translate(self, *args, **kwargs):
        return super(IBMTranslator, self).translate(*args, **kwargs)


translator = IBMTranslator()
