# -*- coding: utf-8 -*-
from flask import Blueprint, request, render_template
from google.appengine.ext import ndb
from app.kernel.cache import cache

X_APPENGINE_REGION = 'X-AppEngine-Region'
X_APPENGINE_CITY = 'X-AppEngine-City'
X_APPENGINE_CITYLATLONG = 'X-AppEngine-CityLatLong'
DEFAULT_COORDINATES = '0,0'

site = Blueprint('site', __name__, template_folder='templates')


def geolocation_cache_key():
    args = str(hash(request.headers.get(X_APPENGINE_CITYLATLONG)))
    return (request.path + args).encode('utf-8')


@site.route('/')
@cache.cached(timeout=3600, key_prefix=geolocation_cache_key)
def index():
    import logging
    lat, lng = request.headers.get(X_APPENGINE_CITYLATLONG, DEFAULT_COORDINATES).split(',')
    return render_template('map.html', **locals())


@site.route('/upload')
@cache.cached(timeout=3600, key_prefix=geolocation_cache_key)
def upload():
    lat, lng = request.headers.get(X_APPENGINE_CITYLATLONG, DEFAULT_COORDINATES).split(',')
    return render_template('upload.html', **locals())


@site.route('/nude/<string:key>')
@cache.cached(timeout=600)
def nude(key):
    nude = ndb.Key(urlsafe=key).get()
    return render_template('nude.html', nude=nude)


@site.route('/tag/<string:key>')
@cache.cached(timeout=600)
def tag(key):
    return render_template('tag.html')


@site.route('/admin/')
def admin():
    return render_template('admin.html')
