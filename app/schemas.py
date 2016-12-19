# -*- coding: utf-8 -*-
import re
from marshmallow import Schema, fields, post_dump, pre_load
from cloudinary.utils import cloudinary_url
from cloudinary import CloudinaryImage


class BaseSchema(Schema):

    @post_dump(pass_many=True)
    def wrap_with_envelope(self, data, many):
        return {'result': data} if many else data


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
    tags = fields.List(fields.String)
    gender = fields.String(load_from='owner.gender')
    updated = fields.DateTime()
    url = fields.Method('compose_url')

    def compose_url(self, data):
        return CloudinaryImage(data.url, type='fetch').build_url(
            width=640,
            quality=90,
            crop='scale',
            format='jpg',
            angle='exif',
            effect='trim',
            flags='strip_profile',
            secure=True
        )

    @pre_load
    def parse_tags(self, data):
        lowered = data.get('tags', '').lower()
        splitted = re.sub(r'[^a-zA-Z0-9 ]', r'', lowered).split()
        data['tags'] = [tag[:32] for tag in set(splitted)]


class TagSchema(BaseSchema):
    key = fields.Function(lambda obj: obj.key.urlsafe())
