import sys
import logging
logging.basicConfig(stream=sys.stderr)

sys.path.insert(0,"/var/www/simpleapp/")

from simpleapp import simpleapp as applicationp