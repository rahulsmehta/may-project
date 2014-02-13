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
  third_rev_needed = db.BooleanProperty()
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
  reviewer = db.StringProperty() #stringified id of reviewer
  reviewer_fullname = db.StringProperty()
  submitter = db.StringProperty()
  scores = db.ListProperty(item_type=int)
  comments = db.StringListProperty()
  summary_comments = db.TextProperty()
  complete = db.BooleanProperty(default=False)

  def proposal_score(self):
    if self.scores is None:
      return "not_reviewed"
    total = 0
    for num in self.scores:
      total+=num
    return total

  def proposal_status(self):
    total = self.proposal_score()

    if total > 90:
      return "approved"
    elif total > 75:
      return "revisions"
    elif total > 55:
      return "rewrite"
    else:
      return "not_approved"

  def status_pretty(self):
    total = self.proposal_score()

    if total > 90:
      return "Proposal Approved"
    elif total > 75:
      return "Needs Revisions"
    elif total > 55:
      return "Rewrite Required"
    else:
      return "Proposal Denied"



