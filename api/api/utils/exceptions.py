from typing import Callable, Any

from api.utils.logger import logger


def hijack(exc:Exception) -> Callable:
    def _hijack(func:Callable) -> Callable:
        def wrapper(*args, **kwargs) -> Any:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.exception(e)
                raise exc(str(e))
        return wrapper
    return _hijack


class NLPModelNotFound(Exception): pass

class TextRankError(Exception): pass

class BackendError(Exception): pass

class TranslationError(Exception): pass

class MalformedJSONException(Exception): pass

class EmptyJSONException(Exception): pass