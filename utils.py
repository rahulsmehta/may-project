import cgi

def make_field_storage(environ):
  """
  Builds a cgi.FieldStorage given the containing WSGI environment.
  Author: Jeremy Archer
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
  Author: Jeremy Archer
  """
  
  return re.sub(r'[^a-zA-Z0-9]', lambda x: '&#{0}'.format(ord(x.group(0))), str(s or ''))
