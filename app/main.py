import os
env = os.environ

from elasticsearch import Elasticsearch
from flask import Flask, render_template, current_app
from flask_redis import FlaskRedis

from socket import gaierror, gethostbyname_ex

# Create flask app
from lib.decorators import exception_handler

app = Flask(__name__)

# Update a few vars we'll need later in our app config
app.config['ES_URL'] = "http://es:9200"
app.config['REDIS_URL'] = "redis://redis:6379/0"

if 'ES_HOST' in env and 'ES_PORT' in env:
    app.config['ES_URL'] = f'{env["ES_HOST"]:{env["ES_PORT"]}}'

if "REDIS_URL" in env and 'REDIS_HOST' in env and 'REDIS_PORT' in env and 'REDIS_DATABSE' in env:
    app.config['REDIS_URL'] = f'redis://{env["REDIS_HOST"]}:{env["REDIS_PORT"]}/{env["REDIS_DATABASE"]}'

# Create our clients
redis = FlaskRedis(app)
es = Elasticsearch(hosts=[app.config.get('ES_URL')])


@app.route('/', strict_slashes=False)
@exception_handler
def hello_world():
    return render_template("index.html")


@app.route("/api/domain/<domain>", methods=['POST'], strict_slashes=False)
@exception_handler
def add_new_domain(domain):
    """ Add a new domain to be perpetually resolved
    """

    # Check to see if this domain is already being tracked


    # This is a new domain, lets try to resolve it for the first time
    try:
        hostname, aliastlist, ipaddrlist = gethostbyname_ex(domain)
    except gaierror as e:
        current_app.logger.exception(e)
        raise e


@app.route("/api/domain/<domain>", methods=['DELETE'], strict_slashes=False)
@exception_handler
def remove_domain(domain):
    """ Delete a domain that's being perpetually resolved
    """
    raise NotImplemented


@app.route("/api/stats/<domain>", methods=['GET'], strict_slashes=False)
@exception_handler
def historical_domain_resolutions(domain):
    """ Return historical records for an exact match domain
    """
    raise NotImplemented


@app.route("/api/stats/tag/<tag>", methods=['GET'], strict_slashes=False)
@exception_handler
def current_domain_resolutions(tag):
    """ Return current resolutions for all domains that match a given tag
    """
    raise NotImplemented
