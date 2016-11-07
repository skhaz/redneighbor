import dev_appserver
from google.appengine.ext import vendor

dev_appserver.fix_sys_path()

vendor.add('lib')
