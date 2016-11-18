# -*- coding: utf-8 -*-
import datetime
from flask import request
from flask.ext.restful import Resource

from google.appengine.ext import ndb

from app.api.v1.auth import requires_auth, current_user
from app.models import User
from app.schemas import UserSchema


class UserResource(Resource):
    def __init__(self):
        self.schema = UserSchema()

    def _get(self, key):
        return ndb.Key(urlsafe=key).get()

    def get(self, key):
        return self.schema.dump(self._get(key)).data

    def put(self, key):
        data, errors = self.schema.load(request.get_json(), partial=True)

    def delete(self, key):
        pass


class UserListResource(Resource):
    def __init__(self):
        self.schema = UserSchema()
