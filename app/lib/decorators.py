import collections
from functools import wraps
from flask import jsonify, current_app
from .exceptions import RequestException


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
