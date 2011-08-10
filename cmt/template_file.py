from string import Template
import types
import namespace as ns
import os.path

class Error (Exception):
  """Base class for exceptions in this module"""
  pass

class FileTypeError (Error):
  """Exception raised for bad template file"""
  def __init__ (self, file):
    self.file = file
    self.msg = '%s: Not a template file.' % file
  def __str__ (self):
    return self.msg

class TemplateFile (object):
  def __init__ (self):
    self._dict = {}
    self._template = None
    self._contents = None

  def set_template (self, template):
    self._template = Template (template)
    self._contents = None

  def scan_template (self, file):
    #if (not os.path.isabs (file) and
    #    os.environ.has_key ('CMT_PROJECT_TEMPLATE_PATH')):
    #  file = os.path.join (os.environ['CMT_PROJECT_TEMPLATE_PATH'], file)

    if type (file) in types.StringTypes:
      if (not os.path.isabs (file) and
          os.environ.has_key ('CMT_PROJECT_TEMPLATE_PATH')):
        paths = os.environ['CMT_PROJECT_TEMPLATE_PATH'].split (':')
        for path in paths:
          test_file = os.path.join (path, file)
          if (os.path.isfile (test_file)):
            file = test_file
            break

    if type (file) in types.StringTypes:
      f = open (file)
      self._template = Template (f.read ())
    else:
      self._template = Template (file.read ())
    self._contents = None
    
  def substitute (self, mapping):
    return self._template.safe_substitute (mapping)

  def tofile (self, file, mapping):
    f = open (file, 'w')
    f.write (self.tostr (mapping))
    f.close ()

  def tostr (self, mapping):
    return self.substitute (mapping)

class TemplateFiles (object):
  """
  >>> import os

  Create a file to use as a template.  Template files should have a '.in'
  extension.

  >>> f = open ('file1.txt.in', 'w')
  >>> f.write ('Depth = ${Depth}, Gravity = ${Gravity}')
  >>> f.close ()

  Define a dictionary to fill values of the template

  >>> mapping = {'Depth': 12, 'Gravity': 9}

  Create a list of template files and add our template to it.

  >>> t = TemplateFiles ()
  >>> t.add_file ('file1.txt.in')

  Substitute values from the dictionary to the new file based on the template.
  The name of the new file is the name of the template minus the '.in'
  extension.

  >>> t.substitute (mapping)

  Check the output file to make sure it matches the template.

  >>> f = open ('file1.txt', 'r')
  >>> f.read ()
  'Depth = 12, Gravity = 9'
  >>> f.close ()

  Adding a file that isn't a template is a FileTypeError.

  >>> t.add_file ('file1.txt.out') #doctest: +IGNORE_EXCEPTION_DETAIL
  Traceback (most recent call last):
  FileTypeError: file1.txt: Not a template file.

  Rename the output file to something other than the default.

  >>> t.substitute (mapping, rename='file1.ini')

  >>> f = open ('file1.ini', 'r')
  >>> f.read ()
  'Depth = 12, Gravity = 9'
  >>> f.close ()

  You can also do this when adding files.

  >>> t.add_file ('file1.txt.in', rename='file1.cfg')
  >>> t.substitute (mapping)

  >>> f = open ('file1.cfg', 'r')
  >>> f.read ()
  'Depth = 12, Gravity = 9'
  >>> f.close ()

  >>> f = open ('file2.txt.in', 'w')
  >>> f.write ('Depth = ${Depth}')
  >>> f.close ()

  >>> t.add_file ('file2.txt.in')
  >>> t.substitute (mapping, todir='test')

  >>> f = open ('test/file1.txt', 'r')
  >>> f.read ()
  'Depth = 12, Gravity = 9'
  >>> f.close ()

  >>> f = open ('test/file2.txt', 'r')
  >>> f.read ()
  'Depth = 12'
  >>> f.close ()

  >>> os.remove ('file1.ini')
  >>> os.remove ('file1.cfg')
  >>> os.remove ('file1.txt.in')
  >>> os.remove ('test/file1.txt')
  >>> os.remove ('file2.txt.in')
  >>> os.remove ('test/file2.txt')

  """
  def __init__ (self):
    self._files = []

  def add_file (self, src, rename=None):
    (root, ext) = os.path.splitext (src)
    print 'source file is %s' % src
    if rename is None and ext != '.in':
      raise FileTypeError (src)

    if rename is None:
      (root, ext) = os.path.splitext (src)
      dest = root
    else:
      dest = rename
    print 'dest file is %s' % dest

    self._files.append ((src, dest))

  def substitute (self, mapping, todir='.', rename=None):
    for (src, dest) in self._files:
      t = TemplateFile ()
      t.scan_template (src)
      if rename is None:
        dest = os.path.join (todir, dest)
      else:
        dest = os.path.join (todir, rename)
      t.tofile (dest, mapping)

class CMTTemplateFiles (TemplateFiles):
  def substitute (self, mapping, todir='.', base=None):
    if base is not None:
      mapping = ns.extract_base (mapping, base)
    TemplateFiles.substitute (self, mapping, todir)

class CMTTemplateFile (TemplateFile):
  """
  >>> import namespace as ns
  >>> template = "Depth = ${Depth}, Gravity = ${Gravity}"
  >>> f = CMTTemplateFile ()
  >>> f.set_template (template)
  >>> mapping = {'/Base/Var/Depth': 12, '/Base/Var/Gravity': 9}
  >>> f.tostr (mapping, base='/Base/Var/')
  'Depth = 12, Gravity = 9'
  >>> f.tofile ('test.txt', mapping, base='/Base/Var/')

  >>> mapping = {'/Base/Var/Depth': 12}
  >>> f.tostr (mapping, base='/Base/Var/')
  'Depth = 12, Gravity = ${Gravity}'

  >>> f.tostr (mapping, base='/Base/Var')
  'Depth = ${Depth}, Gravity = ${Gravity}'

  >>> f.tostr ({}, base='/Base/Var')
  'Depth = ${Depth}, Gravity = ${Gravity}'
  """
  def substitute (self, mapping, base=None):
    if base is not None:
      mapping = ns.extract_base (mapping, base)
    return TemplateFile.substitute (self, mapping)
  def tofile (self, file, mapping, base=None):
    if base is not None:
      mapping = ns.extract_base (mapping, base)
    TemplateFile.tofile (self, file, mapping)
  def tostr (self, mapping, base=None):
    if base is not None:
      mapping = ns.extract_base (mapping, base)
    return TemplateFile.tostr (self, mapping)

hydrotrend_template = """
Waipaoa 50yrs present
ON				2) Write output to ASCII files (ON/OFF)
./HYDRO_OUTPUT/		3) Location where the output data will be stored (not optional for web)
1				4) No. of epochs to run (leave 1 line blank between epochs; start copying from nr 5)
-62 ${RunDuration} d		5) Start year; no. of years to run; averaging interval: D,M,S or Y
4				6) Number of suspended sed. grain sizes to simulate (max 10)
.2 .2 .25 .35	7) Proportion of sediment in each grain size (sum=1)
14.26 0.0 0.55 	 8) Yrly Tbar: start (C), change/yr (C/a), std dev
1.59 0.0 0.3 	9) Yrly P sum: start (m/a), change/yr (m/a/a), std. dev (m).
1. 1.9 7	10) Rain: Mass Balance Coef, Distribution Exp, Distribution Range
0.0				11) Constant annual base flow (m^3/s)
Jan  19.14 1.05 103.91 62.07		12-23) monthly climate variables
Feb  18.85 1.32 101.22 69.90 	column  variable	description
Mar  17.49 1.07 121.90 71.12 	------  --------	-----------
Apr  14.76 0.88 147.96 56.59 	1	moname  	month name (not used)
May  12.08 0.86 125.50 71.91 	2	tmpinm  	monthly mean T. (C)
Jun  9.99 1.08 151.81 67.80 	3	tmpstd  	within month Std Dev. of T
Jul  9.43 0.95 176.36 63.04 	4	raininm 	monthly total Precip. (mm)
Aug  10.13 0.74 147.82 49.38 	5	rainstd 	Std Dev of the monthly P.
Sep  11.92 0.94 132.03 64.54		.
Oct  13.91 1.14 127.39 60.39		.
Nov  15.82 1.08 114.85 60.34		.
Dec  17.93 1.03 116.84 70.08		.
6.16			24) Lapse rate to calculate freezing line (degC/km)
3269.93 0.0 	25) Starting glacier ELA (m) and ELA change per year (m/a)
0.3				26) Dry precip (nival and ice) evaporation fraction
-0.1 0.85                       26a) canopy interception alphag(-0.1(mm/d)), betag(0.85(-))
10 1                            26b) groundwater pole evapotranspiration alpha_gwe (common 10 (mm/d)), beta_gwe (common 1 (-))
0.0001			27) Delta plain gradient (m/m)
1.0                             27a) Bedload rating term (-)(typically 1.0; if set to -9999, 1.0 will be used)
100				28) River basin length (km)
0 d1000			29) Mean volume, (a)ltitude or (d)rainage area of reservoir (km^3)(m) or (km^2)
0.87 0.1		30) River mouth velocity coef. (k) and exponent (m); v=kQ^m, w=aQ^b, d=cQ^f
3.0 0.5			31) River mouth width coef.(a) and exponent (b); Q=wvd so ack=1 and b+m+f=1
1.1				32) Average river velocity (m/s)
7.1e9 4.2e9		33) Maximum/minimum groundwater storage (m^3)
4.2e9			34) Initial groundwater storage (m^3)
20000 	1.4		35) Groundwater (subsurface storm flow) coefficient (m^3/s) and exp (unitless)
110				36) Saturated hydraulic conductivity (mm/day)
355 -39.5		37) Longitude, latitude position of the river mouth (decimal degrees)
1				38) Nr. of outlets in a delta, 1 =  no outlets; 
1				39) Fraction Q for each outlet
n1				40)	Certain Qpeak, above this, it change the nr of outlets or the Q fr. distribution
${TrappingEfficiency}				41) Fraction sediment trapped in delta (0 - 0.9; only if 39 > 1 or u or r)
2                               42) 0)=QRT;  1) =ART)   2) =BQART
0.3                             43) if line 42 is 2: Lithology factor from hard - weak material (0.3 - 3)^M
6	                        44) if line 42 is 2: Anthropogenic factor (0.5 - 8), human disturbance of the landscape
"""
class HydrotrendTemplate (TemplateFile):
  def __init__ (self):
    TemplateFile.__init__ (self)
    TemplateFile.set_template (self, hydrotrend_template)

  def set_template (self, template):
    pass
  def scan_template (self, file):
    pass

sedflux_template = """
[global]
margin name:            Small
vertical resolution:    ${VerticalResolution}
x resolution:           ${XResolution}
y resolution:           ${YResolution}
bathymetry file:        small_bathy.csv
sediment file:          small_sediment.kvf

[epoch]
number:           1
duration:         ${RunDuration}y
time step:        .25y
process file:     small_epoch.kvf
"""
class SedfluxTemplate (TemplateFile):
  """
  >>> mapping = {'VerticalResolution': .5, 'XResolution': 1000.,
  ...            'YResolution': 1000., 'RunDuration': 500}
  >>> f = SedfluxTemplate ()
  >>> print f.tostr (mapping) #doctest: +NORMALIZE_WHITESPACE
  [global]
  margin name:            Small
  vertical resolution:    0.5
  x resolution:           1000.0
  y resolution:           1000.0
  bathymetry file:        small_bathy.csv
  sediment file:          small_sediment.kvf
  <BLANKLINE>
  [epoch]
  number:           1
  duration:         500y
  time step:        .25y
  process file:     small_epoch.kvf
  """
  def __init__ (self):
    TemplateFile.__init__ (self)
    TemplateFile.set_template (self, sedflux_template)

  def set_template (self, template):
    pass
  def scan_template (self, file):
    pass

class IniTemplate (TemplateFile):
  """
  >>> mapping = {'/Section1/Depth': 42, '/Section2/Var': 5}
  >>> f = IniTemplate ()
  >>> print f.tostr (mapping)
  [Section2]
  Var=5
  [Section1]
  Depth=42

  >>> mapping = {'/Base/Section1/Depth': 42, '/Base/Section2/Var': 5,
  ...            '/Base/Section2/Vars': [1,2,3.],
  ...            '/Base/Section1/File': 'file.txt'}
  >>> f = IniTemplate ()
  >>> print f.tostr (mapping, base='/Base')
  [Section2]
  Var=5
  Vars=1; 2; 3.0
  [Section1]
  Depth=42
  File=file.txt

  >>> mapping = {'Depth': 42, 'Var': 'file.txt'}
  >>> f = IniTemplate ()
  >>> print f.tostr (mapping)
  Var=file.txt
  Depth=42
  """
  def set_template (self, template):
    pass
  def scan_template (self, file):
    pass

  def tostr (self, mapping, base=''):
    # Find section names
    sections = set ()
    for key in mapping.keys ():
      (section, val_name) = ns.split (key)
      sections.add (ns.basename (ns.lstrip (section, base)))

    # Initialize dictionaries for each section
    section_values = {}
    for section in sections:
      section_values[section] = {}

    # Set section values
    for (key, value) in mapping.items ():
      (section, val_name) = ns.split (key)
      section_values[ns.basename (ns.lstrip (section, base))][val_name] = value

    # Create an ini file
    contents = []
    for section in sections:
      if section != '.':
        contents.append ('[%s]' % section)
      for (val_name, value) in section_values[section].items ():
        if hasattr (value, '__iter__'):
          val_str = '; '.join ([str (val) for val in value])
        else:
          val_str = str (value)
        contents.append ('%s=%s' % (val_name, val_str))

    return '\n'.join (contents)

if __name__ == "__main__":
    import doctest
    doctest.testmod()


