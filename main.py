from google.appengine.ext import db
from google.appengine.ext import blobstore
from google.appengine.api import mail
from tempfile import TemporaryFile
import base64
import os
import re
import hashlib
import jinja2
import datetime
import logging
import time
import datetime 
import random
import copy
from utils import *
from models import * 

#Load jinja2 environment:
jinja_environment = jinja2.Environment(
  loader=jinja2.FileSystemLoader(os.path.dirname(__file__)+'/tmpl/'))



def index(environ,start_response):
  adv_list = ["Anderson","Beck","Collet-Jarard","Franke","Granzyk","Horton","Janda","Jurisson","Lopez","Martonffy"] 
  col_list = ["Kovacs","Wagner","Warehall"] 
  counselor_list = ["Tunis","Graham","Cunningham"]
  start_response('200 Okay', [ ])
  return [ jinja_environment.get_template('login.html').render(**locals()).encode('utf-8') ]
  

"""
WSGI handler to create a user (endpoint /api/create)
"""
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
  if not passwd == passwd_conf or passwd == "":
    fail = True
  
  # If either uniqueness or pass fails, do not create account.
  if fail == True:
    msg = "There was an error during account creation! Please try again."
    html = '<div class="alert alert-danger alert-dismissable"> <button type="button" class="close" data-dismiss="alert" aria-hidden="true">&times;</button>'+msg+'</div>'
    adv_list = ["Anderson","Beck","Collet-Jarard","Franke","Granzyk","Horton","Janda","Jurisson","Lopez","Martonffy"] 
    col_list = ["Kovacs","Wagner","Warehall"] 
    counselor_list = ["Tunis","Graham","Cunningham"]
    start_response('200 Okay', [ ])
    return [ jinja_environment.get_template('login.html').render(**locals()).encode('utf-8') ]

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
   proposal = None,
   status = user_status
  )
  new_user.put()

  headers = [ ]
  headers.extend(gen_session_cookie(new_user))
  headers.extend([('Location','/user')])

  # Redirect to user page.
  start_response('302 Redirect', headers)
  return [ ]


"""
WSGI handler to authenticate user.
"""
def authenticate_user(environ,start_response):
  fs = make_field_storage(environ)

  email = form_input(fs,'login-email')
  password = pass_hash(form_input(fs,'login-pass'))
  
  #Check if user exists.
  query = User.all().filter('email',email)

  if query.count() < 1:
    msg = "Account not found! Please try again."
    html = '<div class="alert alert-warning alert-dismissable"> <button type="button" class="close" data-dismiss="alert" aria-hidden="true">&times;</button>'+msg+'</div>'
    adv_list = ["Anderson","Beck","Collet-Jarard","Franke","Granzyk","Horton","Janda","Jurisson","Lopez","Martonffy"] 
    col_list = ["Kovacs","Wagner","Warehall"] 
    counselor_list = ["Tunis","Graham","Cunningham"]
    start_response('200 Okay', [ ])
    return [ jinja_environment.get_template('login.html').render(**locals()).encode('utf-8') ]

  for user in query:
    if password == user.password:
      headers = [ ]
      headers.extend(gen_session_cookie(user))
      headers.extend([('Location','/user')])

      start_response('302 Redirect',headers)
      return []
    else:
      adv_list = ["Anderson","Beck","Collet-Jarard","Franke","Granzyk","Horton","Janda","Jurisson","Lopez","Martonffy"] 
      col_list = ["Kovacs","Wagner","Warehall"] 
      counselor_list = ["Tunis","Graham","Cunningham"]
      msg = "Incorrect password! Please try again."
      html = '<div class="alert alert-danger alert-dismissable"> <button type="button" class="close" data-dismiss="alert" aria-hidden="true">&times;</button>'+msg+'</div>'
      start_response('200 Okay', [ ])
      return [ jinja_environment.get_template('login.html').render(**locals()).encode('utf-8') ]

"""
WSGI handler for user views. Corresponds to '/user' endpoint.
"""
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

    elif status == "coordinator":
      pending_users = User.all().filter('account_approved',False)
      if pending_users.count() < 1:
        pending_users = None
      approved_students = User.all().filter('account_approved',True).filter('status','student').order('fullname')

      form_list = [ ]
      
      form_a_list = [ ]
      form_b_list = [ ]
      form_c_list = [ ]
      form_d_list = [ ]
      prop_list = [ ]

      submitted_students = [ ]

      for user in approved_students:
        user_form = user.forms
        if user_form[0] == False:
          form_a_list.append(user)
        if user_form[1] == False:
          form_b_list.append(user)
        if user_form[2] == False:
          form_c_list.append(user)
        if user_form[3] == False:
          form_d_list.append(user)
        if user.proposal_submitted == False:
          prop_list.append(user)
        if user.proposal_submitted == True:
          submitted_students.append(user)
          
      
      form_list.append(form_a_list)
      form_list.append(form_b_list)
      form_list.append(form_c_list)
      form_list.append(form_d_list)
      form_list.append(prop_list)


    elif status == "reviewer":
      assigned_proposals = user.assigned_proposals

      if len(assigned_proposals) > 0:
        assigned_users = [ ]
        assigned_secret = [ ]
        for i in range(len(assigned_proposals)):
          temp_user = User.get_by_id(int(assigned_proposals[i]))
          temp_user.secret = "Student "+str(i+1)
          assigned_users.append(temp_user)

      

    start_response('200 Okay', [ ])
    return [ jinja_environment.get_template('user.html').render(**locals()).encode('utf-8') ]

"""
WSGI handler for updating the user form data (Form A, B, etc.)
"""
def forms_update(environ,start_response):
  fs = make_field_storage(environ)
  try:
    email = form_input(fs,'coordinator-student').split('(')[1].strip(')')
    user = User.all().filter('email',email).get()
    form_id = form_input(fs,'coordinator-form').split(':')[0].split(' ')[1]
    user_forms = user.forms 
    if form_id == "A":
      user_forms[0]=True
    elif form_id == "B":
      user_forms[1]=True
    elif form_id == "C":
      user_forms[2] = True
    elif form_id == "D":
      user_forms[3] = True

    user.forms=user_forms
    user.put()
  except:
    logging.error("No such user found.")

  start_response('302 Redirect',[('Location','/user')])
  return [ ]  



"""
WSGI handler for log out. Clears session cookie and redirects to '/'
"""
def logout(environ,start_response):
  headers = [ ]
  headers.extend(clear_cookie())
  headers.extend([('Location','/')])
  print str(headers)
  start_response('302 Redirect',headers)

  return [ ]

"""
WSGI handler for proposal submission.
"""
def submit_view(environ,start_response):
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
    start_response('200 Okay', [ ])
    return [ jinja_environment.get_template('submit.html').render(**locals()).encode('utf-8') ]
  else:
    start_response('302 Redirect',[('Location','/user')])
    return [ ]


'''
WSGI handler for account approval.
'''
def account_auth(environ,start_response):
  parts = environ.get('PATH_INFO')[1:].split('/')
  user = User.get_by_id(int(parts[1]))
  
  if parts[0] == "approve":
    user.account_approved = True
    user.put()
  else:
    user.delete()

  start_response('302 Redirect',[('Location','/user')])
  return [ ]

def upload(environ, start_response):
  user = None
  try:
    key = environ.get("HTTP_COOKIE").split('=')[1]
    user = User.get(key)
  except:
    logging.error("No user authenticated.")
  if user is None:
    start_response('302 Redirect',[('Location','/')])
    return []

  fs = make_field_storage(environ)
  user.proposal = None
  user.put()

  user.proposal = db.Blob(fs['upload-file'].file.read())
  
  fn = fs['upload-file'].filename.split(".")
  user.proposal_filetype = fn[len(fn)-1]
  user.proposal_title = form_input(fs,'upload-title')
  user.proposal_authors = form_input(fs,'upload-author')
  user.proposal_summary = form_input(fs,'upload-summary')
  user.proposal_submitted = True
  user.put()

  start_response('302 Redirect',[('Location','/user')])
  return []

def download_proposal(environ,start_response):
  parts = environ.get('PATH_INFO')[1:].split('/')
  student = User.get_by_id(int(parts[1]))
  
  proposal = student.proposal
  print dir(proposal)
  block_size = 4096

  status = "200 Okay"
  fn = str(student.key().id())+"."+student.proposal_filetype
  headers = [('Content-Type','application/text'),('Content-Disposition','attachment; filename='+str(fn))]
  start_response(status,headers)

  return [proposal]

#TODO NEED TO ADD 2 REVIEWERS BY DEFAULT AND A THIRD IF THERE'S A DISCREPANCY
def start_review(environ,start_response):
  students = User.all().filter('account_approved',True).filter('status','student').filter('proposal_submitted',True).order('fullname')
  reviewers = User.all().filter('account_approved',True).filter('status','reviewer')

  #Copy students to an array
  student_list = [ ]
  reviewer_list = [ ]
  for user in students:
    student_list.append(user)
  for user in reviewers:
    reviewer_list.append(user)

  random.shuffle(student_list)
  random.shuffle(reviewer_list)

  while len(reviewer_list)>0:
    assigned_proposals = [ ]
    try:
      reviewer_a = reviewer_list.pop()
      reviewer_b = reviewer_list.pop()
    except:
      logging.error("No more reviewers.")
    try:
      for i in range(3):
        temp_student = student_list.pop()
        temp_student.reviewers = [ ]
        temp_student.reviewers.append(str(reviewer_a.key().id()))
        temp_student.reviewers.append(str(reviewer_b.key().id()))
        assigned_proposals.append(str(temp_student.key().id()))
        temp_student.put()
    except:
      logging.error("Reached end of list.")
    print assigned_proposals

    reviewer_a.assigned_proposals = assigned_proposals
    reviewer_b.assigned_proposals = assigned_proposals
    reviewer_a.put()
    reviewer_b.put()

  status = "302 Redirect"
  headers = [('Location','/user')]
  start_response(status,headers)
  return [ ]


"""
WSGI handler for the coordinator viewing proposals.
"""
def coordinator_view(environ,start_response):
  fs = make_field_storage(environ)
  try:
    email = form_input(fs,'coordinator-student').split('(')[1].strip(')')
    student = User.all().filter('email',email).get()

    prop_url = "/view/"+str(student.key().id())
    headers = [('Location',prop_url)]
  except:
    logging.error("No students found.")
    headers = [('Location','/user')]

  status = "302 Redirect"

  start_response(status,headers)
  return [ ]

"""
WSGI handler for viewing proposals on a page
"""
def view_proposal(environ,start_response):
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

  parts = environ.get('PATH_INFO')[1:].split('/')
  student = User.get_by_id(int(parts[1]))
  try:
    reviewers = [ ]
    for str_id in student.reviewers:
      int_id = int(str_id)
      temp_user = User.get_by_id(int_id)
      reviewers.append(temp_user)
  except:
    logging.error("Reviewer(s) not assigned yet.")
    reviewers = None

  start_response('200 Okay', [ ])
  return [ jinja_environment.get_template('view_prop.html').render(**locals()).encode('utf-8') ]

"""
WSGI handler for reviewing a proposal.
"""
def review_proposal(environ,start_response):
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

  parts = environ.get('PATH_INFO')[1:].split('/')
  student = User.get_by_id(int(parts[1]))

  start_response('200 Okay', [ ])
  return [ jinja_environment.get_template('review.html').render(**locals()).encode('utf-8') ]
  
