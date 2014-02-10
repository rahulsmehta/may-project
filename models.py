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
  reviews = db.StringListProperty() #Stringified integer "id" of the REVIEW objects
  reviewers = db.StringListProperty() #Stringified integer "id" of the reviewer(s)
  proposal_submitted = db.BooleanProperty()
  forms = db.ListProperty(item_type=bool)
  proposal_approved = db.BooleanProperty()
  revisions_requested = db.BooleanProperty()
  revisions_submitted = db.BooleanProperty()
  proposal = db.BlobProperty()
  proposal_filetype = db.StringProperty()
  proposal_title = db.StringProperty()
  proposal_authors = db.StringProperty()
  proposal_summary = db.TextProperty()
  status = db.StringProperty() # Can ONLY be one of the following: 'student,' 'reviewer,' 'coordinator,' 'admin'
  secret = db.StringProperty() # Student A, Student B, you get the point

class Review(db.Model):
  """
  This class represents a 'review' for the proposal in question.
  """
  submitting_user = db.StringProperty() #stringified id of reviewer
  scores = db.ListProperty(item_type=int)
  comments = db.StringListProperty()
  summary_comments = db.TextProperty()
  proposal_status = db.StringProperty() #Can be one of the following: 'approved','revisions','rewrite','not_approved'
  complete = db.BooleanProperty(default=False)

  def proposal_status(self):
    temp_scores = self.scores
    if temp_scores is None:
      return "not_reviewed"
    total = 0
    while len(temp_scores)>0:
      total+=temp_scores.pop()

    if total > 90:
      return "approved"
    elif total > 75:
      return "revisions"
    elif total > 55:
      return "rewrite"
    else:
      return "not_approved"


