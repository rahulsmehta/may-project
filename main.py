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

#Load jinja2 environment:
jinja_environment = jinja2.Environment(
  loader=jinja2.FileSystemLoader(os.path.dirname(__file__)+'/tmpl/'))

 
def create_user(environ,start_response):
  fs = make_field_storage(environ)
  fail = False
  
  # Check if there exists an account with the specified email.
  u_email = form_input(fs,'signup-email')
  query = User.all().filter('email',u_email)
  if query.count() > 0:
    fail = True


  # Check that the password and confirmation agree.
  passwd = form_input(fs,'signup-pass')
  passwd_conf = form_input(fs,'signup-pass-confirm')
  if not passwd == passwd_conf:
    fail = True
  
  # If either uniqueness or pass fails, do not create account.
  if fail == True:
    start_response('403 Forbidden',[('Location','/')]) #TODO Failure splash screen
    return [ ]

  # Determines user status depending on whether or not a parent was supplied.
  user_status = None
  if not form_input(fs,'signup-parent1_name') == '':
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
   assigned_proposals = [ ],
   reviewed = False,
   proposal_submitted = False,
   forms = [False,False,False,False,False],
   proposal_approved = False,
   revisions_requested = False,
   revisions_submitted = False,
   proposal_url = None,
   status = user_status
  )
  new_user.put()

  headers = [ ]
  headers.extend(gen_session_cookie(new_user))
  headers.extend([('Location','/user')])

  # Redirect to user page.
  start_response('302 Redirect', headers)
  return [ ]

def authenticate_user(environ,start_response):
  fs = make_field_storage(environ)

  email = form_input(fs,'login-email')
  password = pass_hash(form_input(fs,'login-pass'))
  
  #Check if user exists.
  query = User.all().filter('email',email)

  if query.count() < 1:
    start_response('302 Redirect',[('Location','/')])
    return []

  for user in query:
    if password == user.password:
      headers = [ ]
      headers.extend(gen_session_cookie(user))
      headers.extend([('Location','/user')])

      start_response('302 Redirect',headers)
      return []
    else:
      start_response('403 Forbidden',[('Location','/')])
      return []

def user_view(environ,start_response):
  user = None
  try:
    key = environ.get("HTTP_COOKIE").split('=')[1]
    user = User.get(key)
  except:
    logging.error("No user authenticated.")
  if user is None:
    start_response('302 Redirect',[('Location','/')])
    return []
  else:
    user_name = user.fullname
    status = user.status

    if status == "student":
      proposal_submitted = user.proposal_submitted
      forms = user.forms

    elif status == "reviewer":
      assigned_proposals = user.assigned_proposals

      if len(assigned_proposals) > 0:
        assigned_users = [ ]
        for i in range(len(assigned_proposals)):
          temp_user = User.get(assigned_proposals[i])
          assigned_users.append(temp_user)
      

    start_response('200 Okay', [ ])
    return [ jinja_environment.get_template('user.html').render(**locals()).encode('utf-8') ]

def logout(environ,start_response):
  headers = [ ]
  headers.extend(clear_cookie())
  headers.extend([('Location','/')])
  print str(headers)
  start_response('302 Redirect',headers)

  return [ ]
