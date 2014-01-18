from google.appengine.ext import db
import hashlib
import json


class User(db.Model):
  """
   This class represents any user that can access the system; a student, a reviewer (teacher), 
   coordinator, or system admin. This entity manages privileges of all users and limits actions
   that each individual is permitted to take.
  """
  fullname = db.StringProperty()
  address = db.StringProperty()
  phone = db.StringProperty()
  email = db.StringProperty()
  password = db.StringProperty()          # Stores a sha1 hash of the password.
  parent1_name = db.StringProperty()
  parent1_email = db.StringProperty()
  advisor = db.StringProperty()
  college_counselor = db.StringProperty()
  class_counselor = db.StringProperty()
  account_approved = db.BooleanProperty()
  assigned_proposals = db.StringListProperty() # List of uid's of users' proposals to review
  reviewed = db.BooleanProperty()
  proposal_submitted = db.BooleanProperty()
  forms = db.ListProperty(item_type=bool)
  proposal_approved = db.BooleanProperty()
  revisions_requested = db.BooleanProperty()
  revisions_submitted = db.BooleanProperty()
  proposal_url = db.StringProperty()
  status = db.StringProperty() # Can ONLY be one of the following: 'student,' 'reviewer,' 'coordinator,' 'admin'
