import os
import os.path as p
import sys
from time import time
import spacy
from typing import Optional, Any

from api.utils.exceptions import NLPModelNotFound
from api.utils.logger import logger


SPACY_LANG_MODELS = {
    "nl": "nl_core_news_sm",
    "en": "en_core_web_md",
    "fr": "fr_core_news_md",
}

def get_model(lang:str):
    try:
        return NLP_MODELS[lang] if NLP_MODELS else load_model(lang)
    except KeyError:
        raise NLPModelNotFound(f"Model not available for {lang}")


def load_model(lang:Optional[str]=None, path:Optional[str]=None) -> Any:
    if path is None:
        if not lang:
            raise ValueError("Must provide one of language or path to model")
        elif lang not in SPACY_LANG_MODELS:
            raise NLPModelNotFound(f"Model not available for {lang}")
        path = find_model(SPACY_LANG_MODELS[lang])
    logger.debug(f"Loading model {path}")
    t0 = time()
    nlp = spacy.load(path)
    logger.debug(f"Model loaded in {time() - t0:.2f}s")
    return nlp


def find_model(model_name:str) -> str:
    env_path = p.abspath(p.join(sys.executable, "../.."))
    path_to_modules = p.join(env_path, f"lib/python{sys.version[:3]}/site-packages")
    path_to_model = p.join(path_to_modules, model_name)
    if not p.exists(path_to_model):
        raise FileNotFoundError(path_to_model)
    model_dir = [d for d in os.listdir(path_to_model) if d.startswith(model_name)][0]
    return p.join(path_to_model, model_dir)


if os.environ.get("LOAD_MODELS_AT_START", False) == "yes":
    NLP_MODELS = {
        lang: load_model(lang) for lang in SPACY_LANG_MODELS
    }
else:
    NLP_MODELS = {}

