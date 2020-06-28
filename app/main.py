import traceback
import logging
import sys
import os
import re
from socket import gaierror, gethostbyname_ex
from datetime import datetime
env = os.environ

from elasticsearch_dsl import connections, Search
from flask import Flask, render_template, current_app, jsonify, request, escape, logging as flask_logging

from lib.decorators import exception_handler
from lib.exceptions import DomainExists, ClientError
from models import Domain

# Create flask app
app = Flask("darkstar")

# Set up logging
formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s request_id:%(request_id)s '
                              'user:%(username)s [in %(pathname)s:%(lineno)d]')
log_level = env.get("LOG_LEVEL", "DEBUG")
handler = logging.StreamHandler()
handler.setFormatter(formatter)
handler.setLevel(log_level)
app.logger.addHandler(handler)

# Set default connection strings to be default docker
app.config['ES_URL'] = "http://es:9200"
if 'ES_HOST' in env and 'ES_PORT' in env:
    app.config['ES_URL'] = f'{env["ES_HOST"]:{env["ES_PORT"]}}'

# Create our es client
connections.create_connection(hosts=app.config.get('ES_URL'), timeout=5)


@app.route('/', strict_slashes=False)
@exception_handler
def hello_world():
    try:
        Domain.init()  # TODO: This is .. bad. Fix how this is being done
        return render_template("index.html", ready=True)
    except Exception:
        exc_info = sys.exc_info()
        return render_template('index.html', ready=False, e=''.join(traceback.format_exception(*exc_info)))


@app.route("/api/domain/<domain>", methods=['POST'], strict_slashes=False)
@exception_handler
def add_new_domain(domain):
    """ Add a new domain to be perpetually resolved
    """

    # Default optional params
    tag = ''
    ttr = 5
    notes = ''
    enabled = True

    # Read the json posted data, if any (its all optional params)
    if request.is_json:

        tag = request.get_json().get('tag', '')
        if tag and not isinstance(tag, str):
            raise ClientError("The tag option must be a string")
        if not re.match('[a-z0-9]*', tag.lower()):  # Tags can only be alnum
            raise ClientError(f"Tag names are only allowed to be alphanumeric")

        try:
            ttr = int(request.get_json().get('ttr', 5))
        except ValueError:
            raise ClientError(f"Couldn't convert {request.get_json().get('ttr')} to an integer, "\
                              f"representing the number of minutes between resolution attempts")

        notes = request.get_json().get('notes', '')
        if notes and not isinstance(notes, str):
            raise ClientError("The notes option must be a string")
        notes = escape(notes)

        enabled = request.get_json().get('enabled', True)
        if enabled and not isinstance(enabled, bool):
            raise ClientError("The enabled option must be a boolean")

    # Check to see if this domain is already being tracked
    exists = Domain.search().filter('term', domain=domain).execute()
    if exists:
        raise DomainExists(f"Supplied domain {domain} is already being tracked by Darkstar")

    # This is a new domain, lets try to resolve it for the first time
    current_app.logger.debug(f"{domain} appears to be a new domain, lets try to resolve it")
    try:
        hostname, aliastlist, ipaddrlist = gethostbyname_ex(domain)
        current_app.logger.debug(f"Resolved {domain} to {ipaddrlist}")
    except gaierror as e:
        current_app.logger.exception(e)
        # TODO: Allow adding domains that don't resolve
        raise ClientError("The supplied domain doesn't resolve. Refusing to add to tracking")

    # New domain instance, and add all resolutions for it
    new_domain = Domain(added=datetime.utcnow(), domain=domain, tag=tag, ttr=ttr, notes=notes, enabled=enabled)
    [new_domain.add_resolution(ip) for ip in ipaddrlist]
    new_domain.save()

    return jsonify(new_domain.to_dict())


@app.route("/api/health/es", methods=['GET'], strict_slashes=False)
@exception_handler
def health_check_es():
    return '', 200


@app.route("/api/health/redis", methods=['GET'], strict_slashes=False)
@exception_handler
def health_check_redis():
    return '', 200


@app.route("/api/domain/<domain>", methods=['DELETE'], strict_slashes=False)
@exception_handler
def remove_domain(domain):
    """ Delete a domain that's being perpetually resolved
    """
    raise NotImplemented


@app.route("/api/resolutions", methods=['GET'], strict_slashes=False)
@exception_handler
def current_domain_resolutions():
    """ Return all of the current domain resolutions
    """
    s = Search(index="domain_resolutions").query('match_all')
    print(s.to_dict())
    if request.args.get('only_enabled'):
        current_app.logger.info("Only displaying domains that are enabled")
        s = Search(index="domain_resolutions").filter('term', enabled=True)

    res = s.execute()
    return jsonify(items=[d.to_dict() for d in res])


@app.route("/api/resolutions/<domain>", methods=['GET'], strict_slashes=False)
@exception_handler
def current_specific_domain_resolutions(domain):
    """ Return the current resolutions for the specified domain
    """
    raise NotImplemented


@app.route("/api/resolutions/tag/<tag>", methods=['GET'], strict_slashes=False)
@app.route("/api/resolutions/tag/<tag>/<include_disabled>", methods=['GET'], strict_slashes=False)
@exception_handler
def current_domain_resolutions_for_tag(tag, include_disabled=False):
    """ Return current resolutions for all domains that match a given tag
    """
    s = Search(index="domain_resolutions").filter('term', tag=tag)

    # If anything comes after <tag>, we don't filter again based on enabled status
    if not include_disabled:
        s.filter('term', enabled=True)

    res = s.execute()
    return jsonify(items=[d.to_dict() for d in res])


@app.route("/api/resolutions/historical/<domain>", methods=['GET'], strict_slashes=False)
@exception_handler
def historical_specific_domain_resolutions(domain):
    """ Return the the historical timeline of resolutions for a given domain
    """
    raise NotImplemented
