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


  # Check that the password and confirmation agree.
  passwd = form_input(fs,'signup-pass')
  passwd_conf = form_input(fs,'signup-pass-confirm')

  if not passwd == passwd_conf:
    start_response('403 Forbidden',[('Location','/')]) #TODO Failure splash screen
    return [ ]

  # Determines user status depending on whether or not a parent was supplied.
  user_status = None
  if form_input(fs,'signup-parent1_name') is not '':
    user_status = 'student'
  else:
    user_status = 'reviewer'

  # Create the user.

  new_user = User(
   fullname = form_input(fs,'signup-name'),
   address = form_input(fs,'signup-address'),
   phone = form_input(fs,'signup-phone'),
   email = form_input(fs,'signup-email'),
   password = pass_hash(passwd),
   parent1_name = form_input(fs,'signup-parent1_name'),
   parent1_email = form_input(fs,'signup-parent1_email'),
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
   status = user_status
  )
  new_user.put()
  start_response('302 Redirect', [('Location', '/user')])
  return [ ]

def authenticate_user(environ,start_response):
  fs = make_field_storage(environ)

  email = form_input(fs,'login-email')
  password = pass_hash(form_input(fs,'login-pass'))
  
  #Check if user exists.
  query = User.all().filter('email',email)

  for user in query:
    if password == user.password:
      print '-----------'+user.fullname+' authenticated --------' #TODO For debugging, take out.

      headers = [ ]
      headers.extend(gen_session_cookie(user))

      headers.extend([('Location','/user')])
      print headers

      start_response('302 Redirect',headers)
      return []
    else:
      start_response('403 Forbidden',[('Location','/')])
      return []

def user_view(environ,start_response):
  return "basd;ofijasdofij"
