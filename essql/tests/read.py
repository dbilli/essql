import pprint

from datetime import datetime
from elasticsearch import Elasticsearch

es = Elasticsearch()

res = es.search(index="test-index", body={"query": {"match_all": {}}})

pprint.pprint(res)
