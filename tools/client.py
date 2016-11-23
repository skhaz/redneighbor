import os
import sys
import argparse

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

os.environ['HTTP_HOST'] = "%s.appspot.com" % 'redneighbor-b'
sys.path.insert(1, '..')


def main(project_id):
    remote_api_stub.ConfigureRemoteApiForOAuth(
        '{}.appspot.com'.format(project_id),
        '/_ah/remote_api')

    # if flush:
    #from app.models import Nude
    #nudes = Nude.query()
    #for nude in nudes:
    #    nude.deleted = True
    #    nude.public = False
    #    nude.put()

    memcache.flush_all()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('project_id', help='Your Project ID.')

    args = parser.parse_args()

    main(args.project_id)
