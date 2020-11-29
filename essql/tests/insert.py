import pprint

from datetime import datetime
from elasticsearch import Elasticsearch

es = Elasticsearch()

es.indices.delete(index="test-index")

NUM=5

for x in range(NUM):
    for y in range(NUM):
        for z in range(NUM):

            doc = {
                'x'   : 1000+x,
                'y'   : 2000+y,
                'z'   : 3000+z, 
                'timestamp': datetime.now(),
                'log': { 'level': { 'num': x-y-z, 'descr': str(z+x+y) } },
            }

            res = es.index(index="test-index", body=doc)
            print(res['result'], x,y,z)

es.indices.refresh(index="test-index")

res = es.search(index="test-index", body={"query": {"match_all": {}}})

pprint.pprint(res)



