from google.appengine.ext import db
from google.appengine.api import mail
import base64
import os
import re
import hashlib
import jinja2
import datetime
import logging
import time
import datetime

from utils import *
 
def create_user(environ,start_response):
  fs = make_field_storage(environ)
  print fs.getfirst('signup-name','').strip()
  start_response('302 Redirect', [('Location', 'http://www.google.com/')])
  return [ ]

