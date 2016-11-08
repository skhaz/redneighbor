# -*- coding: utf-8 -*-
from marshmallow import Schema, post_dump, fields


class BaseSchema(Schema):
    """
    TODO:
    http://marshmallow.readthedocs.io/en/latest/extending.html#example-enveloping
    """

    pass


class UserSchema(BaseSchema):
    key = fields.Function(lambda obj: obj.key.urlsafe())
    name = fields.String()
    email = fields.String()
    avatar = fields.String()
    bio = fields.String()
    age = fields.Integer()
    gender = fields.String()
    last_seen = fields.DateTime(load_from='updated')


class NudeSchema(BaseSchema):
    key = fields.Function(lambda obj: obj.key.urlsafe())
    lat = fields.Function(lambda obj: obj.location.lat)
    lng = fields.Function(lambda obj: obj.location.lon)
    url = fields.String()
    gender = fields.String(load_from='owner.gender')
    updated = fields.DateTime()

    @post_dump(pass_many=True)
    def wrap_if_many(self, data, many):
        if many:
            return {'nudes': data}
        return data


class TagSchema(BaseSchema):
    key = fields.Function(lambda obj: obj.key.urlsafe())

    @post_dump(pass_many=True)
    def wrap_if_many(self, data, many):
        if many:
            return {'nudes': data}
        return data
