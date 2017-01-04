# -*- coding: utf-8 -*-
import json
import datetime
from flask import request
from flask.ext.restful import Resource, abort

from google.appengine.api import search
from google.appengine.ext import ndb
from google.appengine.ext import deferred

from app.api.v1.auth import requires_auth, current_user
from app.models import User, Nude
from app.schemas import NudeSchema
from app.kernel.cache import cache, args_cache_key
from app.bot import moderate as bot_moderate

X_APPENGINE_CITY = 'X-AppEngine-City'


class NudeResource(Resource):
    def __init__(self):
        self.schema = NudeSchema()

    def _get(self, key):
        return ndb.Key(urlsafe=key).get()

    @cache.cached(timeout=3600)
    def get(self, key):
        return self.schema.dump(self._get(key)).data

    @requires_auth
    def patch(self, key):
        pass

    @requires_auth
    def delete(self, key):
        nude = self._get(key)
        if current_user.owns(nude):
            nude.public = False
            nude.put()
        else:
            abort(403)


class NudeListResource(Resource):
    def __init__(self):
        self.schema = NudeSchema()

    @cache.cached(timeout=3600, key_prefix=args_cache_key)
    def get(self):
        lat = request.args.get('lat', default=0, type=float)
        lng = request.args.get('lng', default=0, type=float)
        distance = request.args.get('distance', default=1000, type=int)
        limit = request.args.get('limit', default=10, type=int)
        offset = request.args.get('offset', default=0, type=int)

        query_string = 'distance(location, geopoint(%.3f, %.3f)) < %f' % (lat, lng, distance)
        sort1 = search.SortExpression(
            expression='updated',
            direction=search.SortExpression.DESCENDING,
            default_value=datetime.date(year=1970, month=1, day=1))
        sort_opts = search.SortOptions(expressions=[sort1])
        query_options = search.QueryOptions(
            limit=limit,
            offset=offset,
            sort_options=sort_opts)
        query = search.Query(query_string=query_string, options=query_options)
        results = search.Index(name=Nude._INDEX_NAME).search(query)

        nudes = ndb.get_multi([ndb.Key(urlsafe=result.doc_id) for result in results])
        return self.schema.dump(nudes, many=True).data

    @requires_auth
    def post(self):
        self.schema.context = {'user': current_user}
        result, errors = self.schema.load(request.get_json(), partial=True)

        import logging
        logging.warn(result)
        nude = Nude()
        nude.owner = current_user.key
        nude.location = result['location']
        nude.url = result['url']
        nude.tags = result['tags']
        nude.put()

        args = {
            'url': nude.url,
            'lat': nude.location.lat,
            'lon': nude.location.lon,
            'city': request.headers.get(X_APPENGINE_CITY),
            'ip_addr': request.remote_addr,
            'email': current_user.email,
        }

        deferred.defer(
            bot_moderate,
            nude.key.urlsafe(),
            args
        )

        return self.schema.dump(nude).data
