import cgi
import hashlib
from Cookie import SimpleCookie
from google.appengine.ext import db

def make_field_storage(environ):
  """
  Builds a cgi.FieldStorage given the containing WSGI environment.
  """
  
  fs = cgi.FieldStorage()
  copied_env = environ.copy()
  copied_env['QUERY_STRING'] = ''
  
  return cgi.FieldStorage (
    fp = environ['wsgi.input'],
    environ = copied_env,
    keep_blank_values=True
  )

def escape(s):
  """
  Escapes a string so that non-alphanumeric characters are escaped with HTML
  entities.
  """
  
  return re.sub(r'[^a-zA-Z0-9]', lambda x: '&#{0}'.format(ord(x.group(0))), str(s or ''))


def form_input(fs_in,fieldname):
  """
  Pulls form values from an html form within a handler. Used for constructing objects quickly.
  """
  result = fs_in.getfirst(fieldname,'').strip()
  return result

def pass_hash(pwd):
  """
  Creates a sha1 hash of a password to store in the database.
  """
  h = hashlib.sha1()
  h.update(pwd)
  result = h.hexdigest()
  return result


def gen_session_cookie(user):
  session_cookie = SimpleCookie()
  session_cookie['session'] = db.Model.key(user).id()
  session_cookie['session']["Path"] = '/'

  new_headers = [ ]
  new_headers.extend(("set-cookie",morsel.OutputString())
                  for morsel
                  in  session_cookie.values())
  return new_headers
