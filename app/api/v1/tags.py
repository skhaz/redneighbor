# -*- coding: utf-8 -*-
from flask.ext.restful import Resource
from app.schemas import TagSchema


class TagResource(Resource):
    def __init__(self):
        self.schema = TagSchema()

    def get(self, key):
        """Return a tag with a list of nudes
        """


class TagListResource(Resource):
    def __init__(self):
        self.schema = TagSchema()

    def get(self, key):
        """Return all tags, with pagination"""
        pass
