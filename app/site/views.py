# -*- coding: utf-8 -*-
from flask import render_template, abort
from app.kernel.cache import cache
from flask import Blueprint

site = Blueprint('site', __name__, template_folder='templates')


@site.route('/')
@cache.cached(timeout=3600)
def index():
    return render_template('map.html')


@site.route('/upload')
@cache.cached(timeout=3600)
def upload():
    return render_template('upload.html')


@site.route('/nude/<string:key>')
@cache.cached(timeout=600)
def nude():
    return render_template('nude.html')


@site.route('/tag/<string:key>')
@cache.cached(timeout=600)
def tag():
    return render_template('tag.html')
