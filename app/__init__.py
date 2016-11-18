# -*- coding: utf-8 -*-
from requests_toolbelt.adapters import appengine; appengine.monkeypatch()
from google.appengine.ext.appstats import recording

from flask import Flask

__all__ = ['create_app']


def create_app(config=None, **kwargs):
    app = Flask(__name__, **kwargs)
    _configure_app(app, config)
    _configure_cache(app)
    _configure_cors(app)
    _configure_hooks(app)
    _configure_blueprints(app)
    _configure_logging(app)
    _configure_error_handlers(app)
    return recording.appstats_wsgi_middleware(app)


def _configure_app(app, config=None):
    app.secret_key = 'super secret string'


def _configure_cache(app):
    from app.core.cache import cache
    cache.init_app(app, config={'CACHE_TYPE': 'gaememcached'})


def _configure_cors(app):
    from flask_cors import CORS
    cors = CORS()
    cors.init_app(app)


def _configure_hooks(app):
    pass


def _configure_blueprints(app):
    from app.api.v1 import api_blueprint
    app.register_blueprint(api_blueprint)

    from app.blueprints.site import site as site_blueprint
    app.register_blueprint(site_blueprint)

    # from app.tasks import tasks as tasks_blueprint
    # app.register_blueprint(tasks_blueprint, url_prefix='/tasks')


def _configure_logging(app):
    pass


def _configure_error_handlers(app):
    pass
