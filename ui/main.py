import logging
import sys
import os
from socket import gaierror, gethostbyname_ex
from datetime import datetime

from elasticsearch.exceptions import TransportError
from elasticsearch_dsl import connections, Search
from flask import Flask, render_template, current_app, jsonify, request

from lib.decorators import paginate, exception_handler, validate_domain_opts
from lib.exceptions import DomainExists, ClientError
from models import Domain

# Create flask app
app = Flask("darkstar")

# Set up logging
logging.basicConfig(level=os.environ.get("LOG_LEVEL", "WARNING"))
app.logger = logging

# Set connection string to ES
app.config['ES_URL'] = "http://es:9200"
if os.environ.get('ES_HOST') and os.environ.get('ES_PORT'):
    app.config['ES_URL'] = f'{os.environ.get("ES_HOST")}:{int(os.environ.get("ES_PORT"))}'

# Create our es client
try:
    connections.create_connection(hosts=app.config.get('ES_URL'), timeout=5, sniff_on_start=True,
                                  sniff_on_connection_fail=True, sniffer_timeout=60)
    Domain.init()
except TransportError:
    app.logger.exception("Failed to sniff ES host. Are you sure it's reachable?")
    sys.exit(1)


@app.route('/', strict_slashes=False)
def hello_world():
    return render_template("index.html", ready=True)


@app.route("/api/domain/<domain>", methods=['POST'], strict_slashes=False)
@exception_handler("Failed to add domain name to Darkstar")
@validate_domain_opts(is_update=False)
def add_new_domain(**kwargs):
    """ Add a new domain to be perpetually resolved
    """

    domain = kwargs['domain']
    tag = kwargs['tag']
    ttr = kwargs['ttr']
    notes = kwargs['notes']
    enabled = kwargs['enabled']

    # Check to see if this domain is already being tracked
    if Domain.search().filter('term', domain=domain).count() >= 1:
        raise DomainExists(f"Supplied domain {domain} is already being tracked by Darkstar")

    # This is a new domain, lets try to resolve it for the first time
    # TODO: Possible don't rely on Pythons socket lib for resolution, see issue #1 on GitHub
    current_app.logger.debug(f"{domain} appears to be a new domain, lets try to resolve it")
    try:
        hostname, aliastlist, ipaddrlist = gethostbyname_ex(domain)
        current_app.logger.debug(f"Resolved {domain} to {ipaddrlist}")
    except gaierror as e:
        current_app.logger.exception(e)
        # TODO: Allow adding domains that don't resolve
        raise ClientError("The supplied domain doesn't resolve. Refusing to add to tracking")

    # New domain instance, and add all resolutions for it
    ts = datetime.utcnow()
    new_domain = Domain(added=ts, domain=domain, tag=tag, ttr=ttr, notes=notes, enabled=enabled)
    [new_domain.add_resolution(ip, ts) for ip in ipaddrlist]
    new_domain.save(refresh="wait_for")

    return jsonify(new_domain.to_dict())


@app.route("/api/domain/<domain>", methods=['PUT'], strict_slashes=False)
@exception_handler("Failed to update domain details")
@validate_domain_opts(is_update=True)
def update_domain(**kwargs):
    """ Update a domain.
    """

    existing = kwargs['domain_obj'].execute().hits[0]

    # Update domain attributes
    existing.tag = kwargs['tag']
    existing.notes = kwargs['notes']
    existing.ttr = kwargs['ttr']
    existing.save(refresh="wait_for")

    return jsonify(existing.to_dict())


@app.route("/api/domain/<domain>", methods=['DELETE'], strict_slashes=False)
@exception_handler("Failed to delete domain")
def remove_domain(domain):
    """ Delete a domain from Darkstar
    """

    # Check to see if this domain is already being tracked
    domain = Domain.search().filter('term', domain=domain)
    if not domain.count() >= 1:
        raise DomainExists(f"Supplied domain {domain} could not be found. Not deleting")

    # Delete the domain, waiting for shards to refresh before returning
    domain.params(refresh=True).delete()
    return '', 200


@app.route("/api/resolutions", methods=['GET'], strict_slashes=False)
@exception_handler("Unable to get resolutions")
@paginate
def current_domain_resolutions(**kwargs):
    """ Return all of the current domain resolutions, paginating through them
    """

    # Handle our pre-filtering of the enabled status
    enabled_opt = request.args.get('enabled_opt', 'all')
    valid_enabled_opts = ('all', 'enabled', 'disabled')
    if enabled_opt and enabled_opt not in (valid_enabled_opts):
        raise ClientError(f"The enabled_opt param must be one of {valid_enabled_opts}")

    return Domain.list(as_tuple=True, enabled_opt=enabled_opt, offset=kwargs['offset'],
                       size=kwargs['size'], q=kwargs['q'], order_by=kwargs['order_by'],
                       order_dir=kwargs['order_dir']
                       )


@app.route("/api/resolutions/<domain>", methods=['GET'], strict_slashes=False)
@exception_handler
def current_specific_domain_resolutions(domain):
    """ Return the current resolutions for the specified domain
    """
    raise NotImplementedError


@app.route("/api/resolutions/tag/<tag>", methods=['GET'], strict_slashes=False)
@app.route("/api/resolutions/tag/<tag>/<include_disabled>", methods=['GET'], strict_slashes=False)
@exception_handler
def current_domain_resolutions_for_tag(tag, include_disabled=False):
    """ Return current resolutions for all domains that match a given tag
    """
    s = Search(index="domain_resolutions").filter('term', tag=tag)

    # If anything comes after <tag>, it indicates that we _want_ to inclue disabled domains
    if not include_disabled:
        s.filter('term', enabled=True)

    res = s.execute()
    return jsonify(items=[d.to_dict() for d in res])


@app.route("/api/resolutions/historical/<domain>", methods=['GET'], strict_slashes=False)
@exception_handler
def historical_specific_domain_resolutions(domain):
    """ Return the the historical timeline of resolutions for a given domain
    """
    raise NotImplementedError
