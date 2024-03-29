# -*- coding: utf-8 -*-
import os
import cloudstorage as gcs
from flask import Blueprint, abort, request, render_template, make_response

from google.appengine.ext import ndb
from google.appengine.api import app_identity

from app.schemas import NudeSchema
from app.kernel.cache import cache

X_APPENGINE_REGION = 'X-AppEngine-Region'
X_APPENGINE_CITY = 'X-AppEngine-City'
X_APPENGINE_CITYLATLONG = 'X-AppEngine-CityLatLong'
DEFAULT_COORDINATES = '-14.1014211,-50.7475316'

site = Blueprint('site', __name__, template_folder='templates')

bucket_name = os.environ.get('BUCKET_NAME',
                             app_identity.get_default_gcs_bucket_name())


def geolocation_cache_key():
    args = str(hash(request.headers.get(X_APPENGINE_CITYLATLONG)))
    return (request.path + args).encode('utf-8')


@site.route('/')
@cache.cached(timeout=3600, key_prefix=geolocation_cache_key)
def index():
    import logging
    lat, lng = request.headers.get(X_APPENGINE_CITYLATLONG, DEFAULT_COORDINATES).split(',')
    return render_template('map.html', **locals())


@site.route('/login')
@cache.cached(timeout=600)
def login():
    return render_template('login.html', **locals())


@site.route('/upload')
@cache.cached(timeout=3600, key_prefix=geolocation_cache_key)
def upload():
    lat, lng = request.headers.get(X_APPENGINE_CITYLATLONG, DEFAULT_COORDINATES).split(',')
    return render_template('upload.html', **locals())


@site.route('/nude/<string:key>')
@cache.cached(timeout=600)
def nude(key):
    nude = ndb.Key(urlsafe=key).get()
    schema = NudeSchema()
    return render_template('nude.html', nude=schema.dump(nude).data)


@site.route('/tag/<string:key>')
@cache.cached(timeout=600)
def tag(key):
    return render_template('tag.html')


@site.route('/admin/')
def admin():
    return render_template('admin.html')


@site.errorhandler(404)
def page_not_found(err):
    return render_template('404.html')


@site.route('/robots.txt', defaults={'filename': 'robots.txt'})
@site.route('/sitemap.xml', defaults={'filename': 'sitemap.xml'})
@cache.cached(timeout=3600)
def webcrawler(filename):
    fullpath = '/{}/static/{}'.format(bucket_name, filename)
    try:
        stat = gcs.stat(fullpath)
    except gcs.NotFoundError:
        return abort(404)
    gcs_file = gcs.open(fullpath)
    response = make_response(gcs_file.read())
    gcs_file.close()
    response.mimetype = stat.content_type
    return response
