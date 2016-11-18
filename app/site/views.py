from flask import render_template, abort
from flask import Blueprint

site_blueprint = Blueprint('site', __name__, template_folder='templates')


@site_blueprint.route('/')
def index():
    return render_template('index.html')


@site_blueprint.route('/upload')
def upload():
    return render_template('upload.html')


@site_blueprint.route('/nudes/<string:key>')
def nude():
    return render_template('upload.html')
