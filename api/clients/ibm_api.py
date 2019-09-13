import shutil
import os.path as p
from ibm_watson import LanguageTranslatorV3
from typing import Callable, Any, Union, Dict, List
from api.utils.logger import logger

Json = Dict[str, Any]

def index(items, key, value):
    for i, item in enumerate(items):
        if item[key] == value:
            return i
    raise KeyError(f"{key}={value}")   

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
                    # FIXME: Ugly workaround because af and nl might be confused in "identify"
                    nl_index = index(predictions, "language", "nl")
                    af_index = index(predictions, "language", "af")
                    predictions[nl_index]["confidence"] += predictions.pop(af_index)["confidence"]
                    logger.debug("Confidence: {confidence}".format(**prediction))
                return predictions if return_all else prediction[json_key]
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
