from flask import request
from flask.ext.cache import Cache

cache = Cache()


def args_cache_key(*args, **kwargs):
    """Create a string from the path of the request AND arguments
    From: http://stackoverflow.com/questions/9413566/flask-cache-memoize-url-query-string-parameters-as-well
    """
    args = str(hash(frozenset(request.args.items(multi=True))))
    return (request.path + args).encode('utf-8')
