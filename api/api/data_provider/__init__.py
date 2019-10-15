import os
from elasticsearch_dsl import connections
from typing import Optional, List

from api.utils.patterns import Json

hosts = [{"host": os.environ["ES_HOST"], "port": os.environ["ES_PORT"]}]
auth = (os.environ["ELASTICSEARCH_USERNAME"], os.environ["ELASTICSEARCH_PASSWORD"])
connections.create_connection(hosts=hosts, http_auth=auth)

