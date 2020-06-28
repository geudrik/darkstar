import os
env = os.environ

from elasticsearch_dsl import connections
from flask import Flask, render_template, current_app
from flask_redis import FlaskRedis

from socket import gaierror, gethostbyname_ex

from lib.decorators import exception_handler
from lib.exceptions import DomainExists
from models import Domain

# Create flask app
app = Flask(__name__)

# Set default connection strings to be default docker
app.config['ES_URL'] = "http://es:9200"
app.config['REDIS_URL'] = "redis://redis:6379/0"

if 'ES_HOST' in env and 'ES_PORT' in env:
    app.config['ES_URL'] = f'{env["ES_HOST"]:{env["ES_PORT"]}}'

if "REDIS_URL" in env and 'REDIS_HOST' in env and 'REDIS_PORT' in env and 'REDIS_DATABSE' in env:
    app.config['REDIS_URL'] = f'redis://{env["REDIS_HOST"]}:{env["REDIS_PORT"]}/{env["REDIS_DATABASE"]}'

# Create our clients
redis = FlaskRedis(app)
connections.create_connection(hosts=app.config.get('ES_URL'), timeout=5)


@app.route('/', strict_slashes=False)
@exception_handler
def hello_world():
    Domain.init()  # TODO: This is .. bad. Fix how this is being done
    return render_template("index.html")


@app.route("/api/domain/<domain>", methods=['POST'], strict_slashes=False)
@exception_handler
def add_new_domain(domain):
    """ Add a new domain to be perpetually resolved
    """

    # Check to see if this domain is already being tracked
    exists = Domain.search().filter('term', domain=domain).execute()
    if exists:
        raise DomainExists(f"Supplied domain {domain} is already being tracked by Darkstar")


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


@app.route("/api/stats", methods=['GET'], strict_slashes=False)
@exception_handler
def current_domain_resolutions(domain):
    """ Return all of the current domain resolutions
    """
    raise NotImplemented


@app.route("/api/stats/<domain>", methods=['GET'], strict_slashes=False)
@exception_handler
def current_specific_domain_resolutions(domain):
    """ Return the current resolutions for the specified domain
    """
    raise NotImplemented


@app.route("/api/stats/tag/<tag>", methods=['GET'], strict_slashes=False)
@exception_handler
def current_domain_resolutions_for_tag(tag):
    """ Return current resolutions for all domains that match a given tag
    """
    raise NotImplemented


@app.route("/api/historical/<domain>", methods=['GET'], strict_slashes=False)
@exception_handler
def historical_specific_domain_resolutions(domain):
    """ Return the the historical timeline of resolutions for a given domain
    """
    raise NotImplemented
