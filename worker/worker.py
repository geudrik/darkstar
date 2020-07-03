import redis as _redis
import json
import sys
import os

from socket import gaierror, gethostbyname_ex
from datetime import datetime
from time import sleep

import logging
logging.basicConfig(stream=sys.stdout, level=os.environ.get("LOG_LEVEL", "INFO"))
logger = logging
logger.info("Darkstar worker sponning up...")

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

# Enter our infinite loop
while True:
    
    try:
        logger.debug("Getting domain from Redis work queue...")
        domain = redis.blpop(redis_work_key, 5)
        logger.debug(f"Got domain {domain} from redis")

        if domain is None:
            logger.info("No work found in Redis. Sleeping...")
            sleep(15)
            continue

    except Exception:
        logger.exception("Failed to get domain from work queue")
        raise

    logger.debug(f"Resolving {domain}...")
    try:
        hostname, aliastlist, ipaddrlist = gethostbyname_ex(domain)
        logger.info(f"Resolved {domain} to {ipaddrlist}")

    except gaierror as e:
        logger.exception(e)
        raise e

    res = {"domain": domain, "resolutions": ipaddrlist, "timestamp": datetime.utcnow()}
    logger.debug(f"Pushing results to redis: {res}")
    
    redis.rpush(redis_done_key, json.dumps({"domain": domain, "resolutions": ipaddrlist}))

