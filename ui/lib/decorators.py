import collections
import json
import re
from functools import wraps
from flask import jsonify, current_app, request, escape, Response
from .exceptions import RequestException, ClientError, DomainNotFound, ServerError
from models import Domain


def exception_handler(original_function, *dargs, **dkwargs):
    if isinstance(original_function, collections.Callable):
        message = "Generic Exception Occurred"
    else:
        message = original_function

    def format_error(e):
        if hasattr(e, "error_debug") and e.error_debug is not None:
            error_debug = str(e.error_debug)
        else:
            error_debug = str(e)
        return error_debug

    def _exception_handler(f):
        @wraps(f)
        def wrapped_function(*args, **kwargs):
            try:
                ret_val = f(*args, **kwargs)
            except RequestException as e:
                return jsonify(
                    {
                        "error_title": e.title,
                        "error_msg": str(e.message),
                        "error_debug": format_error(e)
                    }
                ), e.error_code
            except Exception as e:
                current_app.logger.exception(e)
                return jsonify(
                    {
                        "error_title": "ServerError",
                        "error_msg": message,
                        "error_debug": format_error(e)
                    }
                ), 500
            return ret_val

        return wrapped_function

    if isinstance(original_function, collections.Callable):
        return _exception_handler(original_function)

    return _exception_handler


def validate_domain_opts(is_update=True):
    """ Validate the args being passed in a JSON body when creating or updating
    a domain within Darkstar. If is_update is True, this decorator add a 'domain_obj' param
    to kwargs that's the instance of the currently existing domain
    """

    def decorator(calling_func):

        @wraps(calling_func)
        def wrapper(*args, **kwargs):

            domain = kwargs.get('domain')
            domain_obj = None

            # Default option values
            kwargs['tag'] = ''
            kwargs['ttr'] = 15
            kwargs['notes'] = ''
            kwargs['enabled'] = True

            # Check that the domain is all ascii chars
            if all(ord(char) < 128 for char in domain):

                # Domain is all ascii, and doesn't start with xn--, so force it to lower (normalize domain)
                if not domain.startswith("xn--"):
                    domain = domain.lower()

            # The domain is not all ascii chars (contains unicode). Lets convert it to punycode
            else:
                domain = domain.strip().decode('utf-8').encode('idna')

            # Overwrite defaults with existing options if this is an update call
            if is_update:
                domain_obj = Domain.search().filter('term', domain=domain)
                if not domain_obj.count() >= 1:
                    raise DomainNotFound("Refusing to update a domain that doesn't exist")
                d = domain_obj.execute().hits[0]
                kwargs['tag'] = d.tag
                kwargs['ttr'] = d.ttr
                kwargs['notes'] = d.notes
                kwargs['enabled'] = d.enabled

            # Check to see if tag option is passed
            tag = request.get_json().get('tag', None)
            if tag is not None:
                if not isinstance(tag, str) or not re.match('[a-z0-9]*', tag.lower()):
                    raise ClientError("The tag option must be an alphanumeric string")
                kwargs['tag'] = escape(tag).lower()

            # Check to see if TTR passed
            ttr = request.get_json().get('ttr', None)
            if ttr is not None:
                try:
                    kwargs['ttr'] = int(ttr)
                except ValueError:
                    raise ClientError("The passed 'ttr' option isn't an integer")

            # Check to see
            notes = request.get_json().get('notes', None)
            if notes is not None:
                if not isinstance(notes, str):
                    raise ClientError("The notes option must be a string")
                kwargs['notes'] = escape(notes)

            enabled = request.get_json().get('enabled', None)
            if enabled is not None:
                if not isinstance(enabled, bool):
                    raise ClientError("The 'enabled' arg must be a boolean")
                kwargs['enabled'] = enabled

            kwargs['domain_obj'] = domain_obj
            return calling_func(*args, **kwargs)

        return wrapper
    return decorator


def paginate(f):
    """ Decorator to handle pagination args, and returning data at the REST level. This should decorate
    any and all endpoint declarations that require pagination. This also handles filtering args.

    Any function that is decorated by this function, needs to return a three-part tuple of 
    (items, filtered_count, total_count), where items is an array of items that the table can use. Take
    note that when something decorated with @paginate_esdsl, kwargs['as_tuple']=True will handle this
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):

        # These are the chunks in the URL that we want to pull values out for
        offset_parameter = "start"
        size_parameter = "length"
        search_parameter = "search[value]"
        order_parameter = "order[0][column]"
        order_dir_parameter = "order[0][dir]"
        include_parameter = "include"
        exclude_parameter = "exclude"

        # Set our pagination vars
        offset = request.args.get(offset_parameter, None)
        size = request.args.get(size_parameter, None)
        q = request.args.get(search_parameter, None)
        order_by = request.args.get(order_parameter, None)
        order_by = request.args.get(f"columns[{order_by}][data]", None)
        include = request.args.get(include_parameter, None)
        exclude = request.args.get(exclude_parameter, None)
        
        include = [v for k, v in request.args.items() if k.startswith("columns") and k.endswith("[data]")]
        order_dir = request.args.get(order_dir_parameter, None)
        group_by = request.args.get("group_by", None)

        # Default to the beginning of the data set
        if offset is None:
            offset = 0

        # Default page size is 10 items
        if size is None:
            size = 10

        offset = int(offset)
        size = int(size)

        # Allow for disabling of paging, but handle overflow potentials
        #   `sys.maxsize` is a 64bit int in Py3, which is larger than ES' max. We could in theory set this to be a 
        #   32bit int, but that seems like an exceedingly poor choice. So let's set a sane default "max"
        max_size = 100000
        if size <= 0:
            size = max_size
        if size > max_size:
            raise ClientError(f"The supplied 'size' field is too large. Use 'offset' and 'size' together to paginate "
                              f"through the results. The maximum value for 'size' is {max_size}")

        # Since this is a decorator, ensure we set our kwargs
        kwargs["offset"] = offset
        kwargs["size"] = size
        kwargs["q"] = q
        kwargs["order_by"] = order_by
        kwargs["order_dir"] = order_dir
        kwargs["group_by"] = group_by
        kwargs["include"] = include
        kwargs["exclude"] = exclude

        response = f(*args, **kwargs)
        if not isinstance(response, tuple) or isinstance(response[0], Response):
            current_app.logger.warning("Paginate decorator called, but wrapped function did not return a tuple")
            return response

        # Our response should return a three-part tuple (items, filtered_count, total_count)
        items, filtered_count, total_count = response

        # One of my normal routines when creating objects is to have a parent-level serialize() method. Try to use it
        if items and isinstance(items[0], object) and hasattr(items[0], "serialize"):
            for item in items:
                if not hasattr(item, "serialize"):
                    current_app.logger.error(f"Auto-serialization failed for endpoint {request.url}: {str(item)}")
                    raise ServerError("Failed serializing results")
            # Blindly assume we're safe, punch it chewie
            items = [i.serialize() for i in items]

        # Welp, no serialize. Fall back to pythons to_dict() method. Not a good idea, but better than nothin'
        elif items and isinstance(items[0], object) and hasattr(items[0], 'to_dict'):
            current_app.logger.warning(f"Falling back to to_dict() serialization on type {type(items[0])}: {items[0]}")
            items = [i.to_dict() for i in items]

        # We've exhausted our serializable methods, last ditch attempt to try to serialize our object
        elif items:
            try:
                json.dumps(items[0])
            except TypeError:
                current_app.logger.exception(f"Unexpected response - cannot serialize [{type(items[0])}]: {items[0]} "
                                             f"\n {dir(items[0])}")
                raise ServerError("Exhausted all attempts to serialize results")

        # This is exceedingly messy, but it works
        my_url = request.base_url
        params = []

        # Determine if we have additional URL args
        if len(request.url.split("?", 1)) > 1:
            params = request.url.split("?", 1)[1]
        other_params = []
        if params:
            params = params.split("&")
            for param_pair in params:
                if not param_pair.startswith("offset=") and not param_pair.startswith("size="):
                    other_params.append(param_pair)
        additional = "&".join(other_params)
        if additional:
            additional = "&" + additional

        # Calculate offsets for the links DataTables wants
        prev_offset = offset - size
        if prev_offset < 0:
            prev_offset = 0
        next_offset = offset + size
        last_offset = filtered_count - size
        if last_offset < 0:
            last_offset = 0

        # Let DT know its own page size
        size_str = ""
        if size:
            size_str = f"&size={size}"

        # Specify the links that DataTables wants
        links = {
            "first": f"{my_url}?offset=0{size_str}{additional}",
            "last": f"{my_url}?offset={last_offset}{size_str}{additional}",
            "prev": f"{my_url}?offset={prev_offset}{size_str}{additional}",
            "next": f"{my_url}?offset={next_offset}{size_str}{additional}"
        }

        # We found the end of the universe, don't include a next link
        if next_offset >= filtered_count:
            links["next"] = ""

        # Looks like we're at the beginning, don't include a prev link
        if offset == 0:
            links["prev"] = ""

        # Dump our json back to the client
        return jsonify(recordsTotal=total_count, recordsFiltered=filtered_count, items=items, start=offset, 
                       length=size, links=links
                       )

    return decorated_function
