# -*- coding: utf-8 -*-
from flask import request
from flask.ext.cache import Cache

cache = Cache()


def args_cache_key(*args, **kwargs):
    args = str(hash(frozenset(request.args.items(multi=True))))
    return (request.path + args).encode('utf-8')
