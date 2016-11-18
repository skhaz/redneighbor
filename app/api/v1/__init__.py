# -*- coding: utf-8 -*-
from flask import Blueprint
from flask.ext.restful import Api
from flask.ext.restful.reqparse import RequestParser

pagination = RequestParser()
pagination.add_argument('limit', type=int, default=10)
pagination.add_argument('offset', type=int, default=0)

nearby = pagination.copy()
nearby.add_argument('lat', type=float, default=0.0)
nearby.add_argument('lng', type=float, default=0.0)
nearby.add_argument('distance', type=int, default=1000)


api_blueprint = Blueprint("api", __name__, url_prefix='/api/v1')
api = Api(api_blueprint)

from . import auth, users, nudes, tags  # noqa

api.add_resource(nudes.NudeResource, '/nudes/<string:key>')
api.add_resource(nudes.NudeListResource, '/nudes')

api.add_resource(users.UserResource, '/users/<string:key>')
api.add_resource(users.UserListResource, '/users')

api.add_resource(tags.TagResource, '/tags/<string:key>')
api.add_resource(tags.TagListResource, '/tags')
