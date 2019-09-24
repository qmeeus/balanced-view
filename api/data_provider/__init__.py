import os
from elasticsearch_dsl import connections
from typing import Optional, List

from api.utils.patterns import Json


hosts = [{"host": os.environ["ES_HOST"], "port": os.environ["ES_PORT"]}]
index_name = os.environ["ES_INDEX"]
connections.create_connection(hosts=hosts)


__all__ = [
    "index_name"
]