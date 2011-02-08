from HTMLParser import HTMLParser
import urllib
import sys
import os

class Error (Exception):
  """Base class for exceptions in this module"""
  pass

class MissingEndTag (Error):
  """Exception raised for missing end tag"""
  def __init__ (self, pos, tag):
    self.tag = tag
    self.msg = '(l.%d, c.%d): Missing closing %s tag' % (pos[0], pos[1], tag)
  def __str__ (self):
    return self.msg

# List of empty tags
tags_without_end = ['br', 'hr', 'meta', 'link', 'base', 'img', 'embed',
                    'param', 'area', 'col', 'input']

class HTMLBlock (HTMLParser):
  def __init__ (self, url, tag='div', attr=None, link_prefix=None):
    HTMLParser.__init__ (self)
    self.stack = []
    self.tag = tag
    self.attr = attr
    self.data = []
    self.link_prefix = link_prefix
    self.src_url = url

    text = urllib.urlopen (url)
    self.feed (text.read ())

  def handle_starttag (self, tag, attrs):
    if not self._in_block ():
      if tag==self.tag:
        if self.attr[0] is not None:
          for attr in attrs:
            if (attr[0]==self.attr[0] and
                (self.attr[1] is None or attr[1]==self.attr[1])):
              self.stack.append (tag)
              self.data.append ('<!-- %s: Start of %s %s block -->\n' %
                                 (self.src_url, self.attr[1], tag))
              self.data.append (self.start_tag (tag, attrs))
        else:
          self.stack.append (tag)
          self.data.append ('<!-- %s: Start of %s block -->\n' %
                             (self.src_url, tag))
          self.data.append (self.start_tag (tag, attrs))
    else:
      if tag not in tags_without_end:
        self.stack.append (tag)
      self.data.append (self.start_tag (tag, attrs))
  def handle_startendtag (self, tag, attrs):
    if self._in_block ():
      self.data.append (self.start_tag (tag, attrs))
      self.data.append (self.end_tag (tag))

  def handle_data (self, data):
    if self._in_block ():
      self.data.append (data.strip ())

  def handle_endtag (self, tag):
    if self._in_block ():
      if self.stack [-1] == tag:
        self.stack.pop ()
        self.data.append (self.end_tag (tag))
        if len (self.stack)==0:
          if self.attr[1] is None:
            self.data.append ('\n<!-- %s: End of %s block -->\n' %
                                (self.src_url, self.tag))
          else:
            self.data.append ('\n<!-- %s: End of %s %s block -->\n' %
                                (self.src_url, self.attr[1], self.tag))
      else:
        raise MissingEndTag (self.getpos (), tag)
  def handle_entityref (self, name):
    if self._in_block ():
      self.data.append (''.join (['&', name, ';']))

  def start_tag (self, tag, attrs):
    return '<%s%s>\n' % (tag, self.attributes (attrs))

  def attributes (self, attrs):
    _attrs = ''
    if attrs:
      s = []
      for (key, value) in attrs:
        if value.startswith ('/') and self.link_prefix is not None:
          value = '/'.join ([self.link_prefix, value])
        value = "\"" + value + "\""
        s.append ('='.join ([key, value]))
      _attrs = ' ' + ' '.join (s)
    return _attrs

  def end_tag (self, tag):
    return '\n</%s>' % tag

  def to_file (self, file):
    if isinstance (file, str):
      with open (file, 'w') as f:
        for line in self.data:
          f.write (line)
    else:
      for line in self.data:
        file.write (line)

  def _in_block (self):
    return len (self.stack)>0
