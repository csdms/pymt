import posixpath

def length (ns):
  """
  Returns the number of components in the namespace

  >>> length ('Var')
  1
  >>> length ('Var.Name')
  2
  >>> length ('')
  0
  >>> length ('Var.Name')
  2
  >>> length ('Var.Name')
  2
  >>> length ('Var.Name')
  2
  """
  return ns.count ('.')+1

def join (*args):
  """
  Returns the concatenation of multiple namespaces

  >>> join ('Sedflux', 'Output.Grid')
  'Sedflux.Output.Grid'
  >>> join ('Sedflux', 'Output.Grid', 'Var', 'Depth')
  'Sedflux.Output.Grid.Var.Depth'
  >>> join ('Sedflux')
  'Sedflux'
  >>> join ('Sedflux', 'Var')
  'Var'
  >>> join ('', 'Var')
  'Var'
  """
  #return posixpath.normpath (posixpath.join (*args))
  return '.'.join (*args)

def basename (ns):
  """
  Returns the final component of a namespace

  >>> basename ('Var.Name.Depth')
  'Depth'
  >>> basename ('Depth')
  'Depth'
  >>> basename ('')
  ''
  """
  #return posixpath.basename (posixpath.normpath (ns))
  items = ns.rsplit ('.')
  return items[-1:]

def split (ns):
  """
  Split a namespace.  Returns tuple "(head, tail)" where "tail" is
  everything after the final slash.  Either part may be empty.

  >>> split ('Var.Name.Depth')
  ('Var.Name', 'Depth')
  >>> split ('NotANamespace')
  ('', 'NotANamespace')
  """
  return ns.rsplit ('.')

def lsplit (ns):
  """
  Split a namespace.  Returns tuple "(head, tail)" where "tail" is
  everything after the first slash.  Either part may be empty.

  >>> lsplit ('Var.Name.Depth')
  ('Var', 'Name.Depth')
  >>> lsplit ('NotANamespace')
  ('NotANamespace')
  >>> lsplit (lsplit ('/Var/Name/Depth')[1])
  ('Var', 'Name.Depth')
  """
  return ns.split ('.')

def lstrip (ns, prefix):
  """
  Strip a base from from the start of a namespace.

  >>> lstrip ('Var.Name.Depth', 'Var.Name')
  'Depth'
  >>> lstrip ('Var.Name.Depth', 'BadVar.Name')
  'Var.Name.Depth'
  >>> lstrip ('Var.Name.Depth', '')
  'Var.Name.Depth'
  """
  if ns.startswith (prefix):
    return ns[len (prefix)+1:]
  else:
    return ns

def rstrip (ns, postfix):
  """
  Strip a base from from the end of a namespace.

  >>> rstrip ('Var.Name.Depth', 'Depth')
  'Var.Name'
  >>> rstrip ('Var.Name.Depth', 'BadVar.Name')
  'Var.Name.Depth'
  >>> rstrip ('Var.Name.Depth', '')
  'Var.Name.Depth'
  >>> rstrip ('Var.Name.Depth', '')
  'Var.Name.Depth'
  """
  if ns.endswith (postfix):
    return ns[-len (postfix):]
  else:
    return ns

def ischild (ns, base):
  """
  Test if a namespace is a child of another namespace.

  >>> ischild ('Var.Name.Depth', 'Var')
  True
  >>> ischild ('Var.Name.Depth', 'Var.Name')
  True
  >>> ischild ('Var.Name.Depth', 'Var.Name.Depth')
  False
  >>> ischild ('Var.Name.Depth', '')
  True

  """
  if ns==base:
    return False
  else:
    return ns.startswith (base)

def commonprefix (list):
  """
  Return the longest namespace prefix for the list of namespaces.

  >>> commonprefix (['/Var/Name/Depth','/Var/Name/Elevation'])
  '/Var/Name/'
  >>> commonprefix (['/Var/Name/','/Var/Name/'])
  '/Var/Name/'
  >>> commonprefix (['/Var//Name/','/Var/Name/'])
  '/Var/Name/'
  >>> commonprefix (['/', '/Var/Name'])
  '/'
  >>> commonprefix (['/Component/Port/Elevation', '/Component/Port/Depth'])
  '/Component/Port/'
  """
  fixed_list = []
  for item in list:
    fixed_list.append (norm (item))
  return posixpath.commonprefix (fixed_list)

def unique_roots (list):
  """
  Return the set of unique roots from a list of namespaces.

  >>> unique_roots (['/Var/Name/Depth', '/Var/Name/Elevation'])
  ['/']
  >>> roots = unique_roots (['Depth/ToVar', 'Depth/FromVar', 'Elevation/ToVar'])
  >>> sorted (roots)
  ['Depth/', 'Elevation/']
  """
  bases = set ()
  for item in list:
    bases.add (root (item))
  return [base for base in bases]

def root (ns):
  """
  Return the root part of a namespace.

  >>> root ('/Var/Name/Depth')
  '/'
  >>> root ('Var/Name/Depth')
  'Var/'
  >>> root ('')
  '.'
  """
  norm_ns = norm (ns)
  i = norm_ns.find ('/')+1
  if i>0:
    return norm_ns[:i]
  else:
    return norm_ns

def extract_base (mapping, base):
  """
  Return a dictionary with keys that are children of a base namespace.

  >>> mapping = {'/BaseName/Var/Depth': 24, '/BaseName/Var/Pi': 3.}
  >>> d = sorted (extract_base (mapping, '/BaseName/Var').items ())
  >>> d
  [('/Depth', 24), ('/Pi', 3.0)]
  >>> unique_roots ([item[0] for item in d])
  ['/']
  >>> d = sorted (extract_base (mapping, '/BaseName/Var/').items ())
  >>> d
  [('Depth', 24), ('Pi', 3.0)]
  >>> unique_roots ([item[0] for item in d])
  ['Depth', 'Pi']
  >>> d = sorted (extract_base (mapping, '/BaseName').items ())
  >>> d
  [('/Var/Depth', 24), ('/Var/Pi', 3.0)]
  >>> d = sorted (extract_base (mapping, '/').items ())
  >>> d
  [('BaseName/Var/Depth', 24), ('BaseName/Var/Pi', 3.0)]
  """
  stripped_mapping = {}

  base = norm (base)
  for key in mapping.keys ():
    if ischild (key, base):
      stripped_mapping[lstrip (key, base)] = mapping[key]

  return stripped_mapping

if __name__ == "__main__":
    import doctest
    doctest.testmod()


