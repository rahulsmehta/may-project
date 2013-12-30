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
from models import * 


 
def create_user(environ,start_response):
  fs = make_field_storage(environ)

  new_user = User(
   fullname = form_input(fs,'signup-name'),
   address = form_input(fs,'signup-address'),
   phone = form_input(fs,'signup-phone'),
   email = form_input(fs,'signup-email'),
   password = pass_hash(form_input(fs,'signup-pass')),
   parent1_name = form_input(fs,'signup-parent1_name'),
   parent1_email = form_input(fs,'signup-parent1_email'),
   parent2_name = form_input(fs,'signup-parent2_name'),
   parent2_email = form_input(fs,'signup-parent2_email'),
   advisor = form_input(fs,'signup-advisor'),
   college_counselor = form_input(fs,'signup-college'),
   class_counselor = form_input(fs,'signup-class'),
   account_approved = False,
   assigned_proposals = [],
   reviewed = False,
   proposal_submitted = False,
   proposal_approved = False,
   revisions_requested = False,
   revisions_submitted = False,
   proposal_url = None,
   status = 'student' #INITIALIZE THIS TO STUDENT RIGHT NOW, DO **NOT** LEAVE THIS HARD-CODED IN TODO FIX
  )
  new_user.put()
  start_response('302 Redirect', [('Location', '/')])
  return [ ]

def authenticate_user(environ,start_response):
  fs = make_field_storage(environ)

  email = form_input(fs,'login-email')
  password = pass_hash(form_input(fs,'login-pass'))
  
  #Check if this user is actually a thing
  query = User.all().filter('email',email)

  for user in query:
    print user.fullname

  start_response('302 Redirect',[('Location','/')])
  return []
