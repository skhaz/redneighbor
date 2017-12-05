# -*- coding: utf-8 -*-
import logging
from datetime import date
from google.appengine.ext import deferred
from google.appengine.ext import ndb
from google.appengine.api import search


class User(ndb.Model):
    name = ndb.TextProperty()
    email = ndb.StringProperty()
    avatar = ndb.TextProperty()
    bio = ndb.TextProperty()
    birthday = ndb.DateProperty()
    gender = ndb.StringProperty()
    admin = ndb.BooleanProperty(default=False)
    created = ndb.DateTimeProperty(auto_now_add=True)
    updated = ndb.DateTimeProperty(auto_now=True)
    deleted = ndb.BooleanProperty(default=False)

    @property
    def nudes(self):
        return Nude.query(Nude.owner == self.key).order(-Nude.updated)

    @property
    def age(self):
        today = date.today()
        years_difference = today.year - self.birthday.year
        before_birthday = (today.month, today.day) < (self.birthday.month, self.birthday.day)
        elapsed_years = years_difference - int(before_birthday)
        return elapsed_years

    def owns(self, nude):
        if nude is None:
            return False
        if self.admin:
            return True
        return nude.owner == self.key

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, self.key.id())
        # TODO     def __repr__(self):
        #  return '<User(email={self.email!r})>'.format(self=self)



class Nude(ndb.Model):
    _INDEX_NAME = 'nude_index_666'
    _QUEUE_NAME = 'index'

    url = ndb.TextProperty()
    location = ndb.GeoPtProperty(required=True, indexed=False)
    public = ndb.BooleanProperty(default=False)
    version = ndb.IntegerProperty(default=0)
    owner = ndb.KeyProperty(kind=User, required=True)
    likes = ndb.KeyProperty(kind=User, repeated=True)  # or in User's model?
    tags = ndb.StringProperty(repeated=True, indexed=True)
    created = ndb.DateTimeProperty(auto_now_add=True)
    updated = ndb.DateTimeProperty(auto_now=True)
    fake = ndb.BooleanProperty(default=False)

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, self.key.id())
        # TODO return '<Nude(name={self.name!r})>'.format(self=self)

    def _pre_put_hook(self):
        self.version = self.version + 1

    def _post_put_hook(self, future):
        deferred.defer(
            Nude._update_index,
            self.key,
            self.version,
            _queue=self._QUEUE_NAME,
            _transactional=ndb.in_transaction())

    @classmethod
    def _update_index(cls, key, version):
        entity = key.get()
        if entity:
            if version < entity.version:
                logging.warning('Attempting to write stale data. Ignore')
                return
            if version > entity.version:
                msg = 'Attempting to write future data. Retry to await consistency.'
                logging.warning(msg)
                raise Exception(msg)
            index = search.Index(name=cls._INDEX_NAME)
            if not entity.public:
                index.delete(key.urlsafe())
                return
            point = search.GeoPoint(entity.location.lat, entity.location.lon)
            index.put(search.Document(
                doc_id=key.urlsafe(),
                fields=[
                    search.GeoField(name='location', value=point),
                    search.DateField(name='updated', value=entity.updated),
                ]))
