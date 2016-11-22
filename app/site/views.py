# -*- coding: utf-8 -*-
from flask import render_template, abort
from flask import Blueprint

site = Blueprint('site', __name__, template_folder='templates')


@site.route('/')
def index():
    return render_template('map.html')


@site.route('/upload')
def upload():
    return render_template('upload.html')


@site.route('/nude/<string:key>')
def nude():
    return render_template('nude.html')
