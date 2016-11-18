from flask import render_template, abort
from flask import Blueprint

site_blueprint = Blueprint('site', __name__, template_folder='templates')


@site_blueprint.route('/')
def index():
    return render_template('index.html')
