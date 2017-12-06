import os
import sys
import shutil

import glob
import argparse
import pandas as pd

import glob2
import md5
import random
from os.path import dirname, join, realpath, split, abspath

import logging
logging.basicConfig(filename='debug.log',level=logging.DEBUG)


sys.path.insert(1, '/Users/skhaz/google-cloud-sdk/platform/google_appengine')
if 'google' in sys.modules:
    del sys.modules['google']

try:
    import dev_appserver
    from google.appengine.ext import vendor
    dev_appserver.fix_sys_path()
    vendor.add('lib')

    from google.appengine.ext import ndb
    from google.appengine.ext.remote_api import remote_api_stub
    from google.appengine.api import memcache
    from google.cloud import storage

except ImportError:
    print('Please make sure the App Engine SDK is in your PYTHONPATH.')
    raise

os.environ['HTTP_HOST'] = "%s.appspot.com" % 'redneighbor-g'
sys.path.insert(1, '..')


def remove_all_nudes():
    from app.models import Nude
    for nude in Nude.query():
        nude.deleted = True
        nude.public = False
        nude.put()
        nude.key.delete()
    memcache.flush_all()


def populate_with_fakes():
    from app import models

    storage_client = storage.Client()

    bucket_name = 'the-cake-is'
    # bucket = storage_client.get_bucket('thecakeis')
    bucket = storage_client.get_bucket(bucket_name)

    user_key = 'ag9zfnJlZG5laWdoYm9yLWdyJgsSBFVzZXIiHDdsTklCNVZ4dXJZNGRNTzA2OFZhM2U4T21jcDEM'
    fake_user = ndb.Key(urlsafe=user_key).get()

    csv_files = glob.glob(join(dirname(realpath(sys.argv[0])), '*.csv'))
    df = pd.concat((pd.read_csv(csv, header=None, usecols=[1, 3])) for csv in csv_files)

    photos = glob2.glob('/Users/skhaz/Workspace/RedditImageGrab/**/*.jpg')
    random.shuffle(photos)

    nudes = []
    for index, row in df.iterrows():
        try:
            fullpath = photos.pop()
            path, filename = split(fullpath)
            rest, parent = split(path)

            blob = bucket.blob('%s/%s' % (parent, filename))
            blob.upload_from_filename(fullpath)
            blob.make_public()

            nude = models.Nude(id=md5.new(fullpath).hexdigest())
            nude.fake = True
            nude.public = True
            nude.deleted = False
            nude.location = ndb.GeoPt(row[1], row[3])
            nude.url = blob.public_url
            nude.owner = fake_user.key
            # TODO nude.tags = ?

            nude.put()
            print(nude)
        except Exception as e:
            print(e)

        # nudes.append(nude)

    # ndb.put_multi(nudes)


def main(project_id):
    remote_api_stub.ConfigureRemoteApiForOAuth(
        '{}.appspot.com'.format(project_id),
        '/_ah/remote_api')

    remove_all_nudes()
    populate_with_fakes()



if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('project_id', help='Your Project ID.')

    args = parser.parse_args()

    main(args.project_id)
