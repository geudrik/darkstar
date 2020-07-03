import redis as _redis
import json
import sys
import os

from elasticsearch_dsl import connections, Search
from socket import gaierror, gethostbyname_ex
from time import sleep

import logging
logging.basicConfig(stream=sys.stdout, level=os.environ.get("LOG_LEVEL", "INFO"))
logger=logging
logger.info("Darkstar worker sponning up...")

# Set connection string to ES
es_url = "http://es:9200"
if 'ES_HOST' in env and 'ES_PORT' in env:
    app.config['ES_URL'] = f'{env["ES_HOST"]:{env["ES_PORT"]}}'
connections.create_connection(hosts=es_url, timeout=5)

# The keynames this worker will communicate with
redis_work_key = "WORKER:QUEUED"  # Will BLPOP to get work from this array
redis_done_key = "WORKER:COMPLETE"  # We'll RPUSH into this array

redis_args = {
    'host': os.environ.get('REDIS_HOST', 'localhost'),
    'port': os.environ.get('REDIS_PORT', 6379),
    'password': os.environ.get('REDIS_PASSWORD', ''),
    'db': os.environ.get('REDIS_DB', 0),

    'health_check_interval': 20
}

# Create our redis connection
try:
    redis = _redis.Redis(**redis_args)

except Exception:
    logger.exception("Unable to init a redis connection")
    raise

# This scripted query lets us pull all docs whos last_resolved timestamp is older than that docs TTR
#   TODO: Yes, this means we can potentially shove the same domain into the work queue more than once within
#   its TTR window. But for now, this is acceptable. More often is better than misses. Besides, the lookup
#   is going to hit the local name server most likely anyway, which means its a cached response so /shrug
query = {
    "query": {
        "bool": {
            "filter": {
                "script": {
                    "script": {
                        "source": "doc['last_resolved'].value.millis <= doc['last_resolved'].value.millis + doc['ttr'].value * 1000",
                        "lang": "painless"
                    }
                }
            }
        }
    }
}

while True:

    