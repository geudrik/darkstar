import collections, re
from functools import wraps
from flask import jsonify, current_app, request, escape
from .exceptions import RequestException, ClientError


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
                print(dir(e))
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


def validate_domain_opts(require_json_body=False):
    """ Validate the args being passed in a JSON body when creating or updating
    a domain within Darkstar
    """

    def decorator(calling_func):

        @wraps(calling_func)
        def wrapper(*args, **kwargs):

            # If we're requiring a json body... make sure it is so
            if require_json_body and not request.is_json:
                msg = "Creating and Updating tracked domains requires a complete JSON blob of parameters"
                raise ClientError(msg)

            # Ensure the tag name being passed is acceptable
            tag = request.get_json().get('tag', '')
            if tag and not isinstance(tag, str):
                raise ClientError("The tag option must be a string")
            if not re.match('[a-z0-9]*', tag.lower()):  # Tags can only be alnum
                raise ClientError(f"Tag names are only allowed to be alphanumeric")
            kwargs['tag'] = escape(tag)

            # Ensure the TTR being passed is a valid integer
            try:
                ttr = int(request.get_json().get('ttr', 5))
                kwargs['ttr'] = ttr
            except ValueError:
                raise ClientError(f"Couldn't convert {request.get_json().get('ttr')} to an integer, "\
                                f"representing the number of minutes between resolution attempts")

            # Ensure that we're passing a valid notes blob
            notes = request.get_json().get('notes', '')
            if notes and not isinstance(notes, str):
                raise ClientError("The notes option must be a string")
            kwargs['notes'] = escape(notes)

            # Ensure that our enabled bool is acceptable
            enabled = request.get_json().get('enabled', True)
            if enabled and not isinstance(enabled, bool):
                raise ClientError("The enabled option must be a boolean")
            kwargs['enabled'] = enabled

            return calling_func(*args, **kwargs)

        return wrapper
    return decorator
