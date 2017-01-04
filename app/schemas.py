# -*- coding: utf-8 -*-
import re
from google.appengine.ext import ndb
from marshmallow import Schema, fields, post_dump, pre_load
from cloudinary.utils import cloudinary_url
from cloudinary import CloudinaryImage


class BaseSchema(Schema):

    @post_dump(pass_many=True)
    def wrap_with_envelope(self, data, many):
        return {'result': data} if many else data


class LatLngField(fields.Field):

    def _serialize(self, value, attr, obj):
        return {'lat': value.lat, 'lng': value.lon}

    def _deserialize(self, value, attr, ob):
        return ndb.GeoPtProperty(value['lat'], value['lng'])


class UserSchema(BaseSchema):
    key = fields.Function(lambda obj: obj.key.urlsafe())
    name = fields.String()
    email = fields.String()
    avatar = fields.String()
    bio = fields.String()
    age = fields.Integer()
    gender = fields.String()
    last_seen = fields.DateTime(dump_only=True, load_from='updated')


class NudeSchema(BaseSchema):
    key = fields.Function(lambda obj: obj.key.urlsafe())
    location = LatLngField()
    tags = fields.List(fields.String)
    gender = fields.String(load_from='owner.gender')
    updated = fields.DateTime(dump_only=True)
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
