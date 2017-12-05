import os
import sys

import glob
import argparse
import pandas as pd

try:
    import dev_appserver
    from google.appengine.ext import vendor
    dev_appserver.fix_sys_path()
    vendor.add('lib')

except ImportError:
    print('Please make sure the App Engine SDK is in your PYTHONPATH.')
    raise

from google.appengine.ext import ndb
from google.appengine.ext.remote_api import remote_api_stub
from google.appengine.api import memcache

os.environ['HTTP_HOST'] = "%s.appspot.com" % 'redneighbor-g'
sys.path.insert(1, '..')



def populate_with_fakes():
    from app import models

    # df = pd.DataFrame(data=d)

    entities = []
    user_key = 'ag9zfnJlZG5laWdoYm9yLWdyJgsSBFVzZXIiHDdsTklCNVZ4dXJZNGRNTzA2OFZhM2U4T21jcDEM'
    fake_user = ndb.Key(urlsafe=user_key).get()
    for data in df:
        nude = models.Nude()
        nude.fake = True
        nude.public = True
        nude.deleted = False

        nude.location = ndb.GeoPt(data['lat'], data['lng'])

        # upload
        # TODO nude.url = ?
        # TODO nude.tags = ?

        nude.owner = fake_user
        nudes.append(nude)
    # nude.put()

    # end
    ndb.put_multi(entities)
    memcache.flush_all()


def main(project_id):
    remote_api_stub.ConfigureRemoteApiForOAuth(
        '{}.appspot.com'.format(project_id),
        '/_ah/remote_api')

    # populate_with_fakes()
    from os.path import dirname, join, realpath
    csv_files = glob.glob(join(dirname(realpath(sys.argv[0])), '*.csv'))
    df = pd.concat((pd.read_csv(csv) for csv in csv_files), header=None)
    print(df)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('project_id', help='Your Project ID.')

    args = parser.parse_args()

    main(args.project_id)
