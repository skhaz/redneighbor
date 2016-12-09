# -*- coding: utf-8 -*-
from os import getenv
from requests_toolbelt.adapters import appengine; appengine.monkeypatch()
import urllib3; urllib3.disable_warnings()
from google.appengine.ext.appstats import recording

from flask import Flask

__all__ = ['create_app']


def create_app(config=None, **kwargs):
    app = Flask(__name__, **kwargs)
    _configure_app(app, config)
    _configure_cache(app)
    _configure_jinja2(app)
    _configure_hooks(app)
    _configure_blueprints(app)
    _configure_error_handlers(app)
    return recording.appstats_wsgi_middleware(app)


def _configure_app(app, config=None):
    app.secret_key = 'super secret string'
    app.debug = not getenv('SERVER_SOFTWARE', '').startswith('Google App Engine')


def _configure_cache(app):
    from app.kernel.cache import cache
    cache_type = 'null' if app.debug else 'gaememcached'
    cache.init_app(app, config={'CACHE_TYPE': cache_type})


def _configure_jinja2(app):
    @app.context_processor
    def inject():
        return dict(DEBUG=True)  # app.debug)


def _configure_hooks(app):
    pass


def _configure_blueprints(app):
    from app.api.v1 import api_blueprint
    app.register_blueprint(api_blueprint)

    from app.web.views import site as site_blueprint
    app.register_blueprint(site_blueprint)

    from app.bot import blueprint as bot_blueprint
    app.register_blueprint(bot_blueprint)


def _configure_error_handlers(app):
    @app.errorhandler(500)
    def application_error(error):
        return 'Unexpected error: {}'.format(error), 500
