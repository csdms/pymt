#! /usr/bin/env python

import time

_attrs = {
    'reset': '39;49;00m',
    'bright': '01m',
    'dim': '02m',
    'standout': '03m',
    'underline': '04m',
    'blink': '05m',
    'fast': '06m',
    'reverse': '07m',
    'hidden': '08m',
    'xout': '09m'
}

_colors = [
    ('black', 'darkgray'),
    ('red', 'lightred'),
    ('green', 'lightgreen'),
    ('brown', 'yellow'),
    ('blue', 'lightblue'),
    ('purple', 'lightpurple'),
    ('cyan', 'lightcyan'),
    ('lightgray', 'white')]

codes = {}

for (_attr, _val) in _attrs.items ():
    codes[_attr] = '\x1b[' + _val

for (i, (dark, light)) in enumerate (_colors):
    codes[dark] = '\x1b[%im' % (i+30)
    codes[light] = '\x1b[%i;01m' % (i+30)

def format (name, text):
    return codes.get (name, '') + text + codes.get ('reset', '')

def create_color_func (name):
    def f (text):
        return format (name, text)
    globals()[name] = f

for _name in codes:
    create_color_func (_name)

def camel_case (text):
    return ''.join (text.title ().split ())

QUICKSTART_BMI = """#! /usr/bin/env python

\"\"\"

'${name}' (version ${version})

Implementation of the Basic Modeling Interface

Copyright: ${copyright}
License: ${license}, see LICENSE for details

\"\"\"

from cmt.bmi import BMI

class Error (Exception):
    pass
class NotImplementedError (Error):
    def __init__ (self, name):
        self._name = name
    def __str__ (self):
        return 'Method not implemented: %s' % self._name

class ${class_name} (BMI):
    def __init__ (self):
        self._input_items = []
        for _item in "${input_items}".split (','):
            self._input_items.append (_item.strip ())

        self._output_items = []
        for _item in "${output_items}".split (','):
            self._output_items.append (_item.strip ())

    def initialize (self, file):
        raise NotImplementedError ('initialize')
    def run (self, time):
        raise NotImplementedError ('run')
    def finalize (self):
        raise NotImplementedError ('finalize')

    def get_input_var_names (self):
        return self._input_items
    def get_output_var_names (self):
        return self._output_items
    def get_name (self):
        return "${name}"
    def get_version (self):
        return "${version}"

    def get_var_type (self, var_name):
        raise NotImplementedError ('get_var_type')
    def get_var_units (self, var_name):
        raise NotImplementedError ('get_var_units')
    def get_var_rank (self, var_name):
        raise NotImplementedError ('get_var_rank')
    def get_time_step (self):
        raise NotImplementedError ('finalize')
    def get_start_time (self):
        pass
    def get_current_time (self):
        pass
    def get_end_time (self):
        pass

    def get_grid_spacing (self, var_name):
        pass
    def get_grid_lower_left_corner (self, var_name):
        pass
    def get_grid_shape (self, var_name):
        pass

    def get_grid_x (self, var_name):
        pass
    def get_grid_y (self, var_name):
        pass
    def get_grid_z (self, var_name):
        pass

    def get_grid_connectivity (self, var_name):
        pass
    def get_grid_offset (self, var_name):
        pass

if __name__ == '__main__':
    bmi = ${class_name} ()

    print 'Model name: %s' % bmi.get_name ()
    print 'Model version: %s' % bmi.get_version ()
    print 'Input items: %s' % ', '.join (bmi.get_input_var_names ())
    print 'Output items: %s' % ', '.join (bmi.get_output_var_names ())

"""

def prompt_for_val (d, key, text, default=None, prefix='> '):
    while True:
        if default is not None:
            prompt = dim (lightgreen (prefix + '%s [%s]: ' % (text, default)))
        else:
            prompt = dim (lightgreen (prefix + '%s: ' % (text)))
        val = raw_input (prompt)
        if default and not val:
            val = default
        break
    d[key] = val

def prompt_for_vals (d, key, text, default=None, prefix='> '):
    vals = []
    while True:
        if default is not None:
            prompt = dim (lightgreen (prefix + '%s [%s]: ' % (text, default)))
        else:
            prompt = dim (lightgreen (prefix + '%s: ' % (text)))
        val = raw_input (prompt)
        if default and not val:
            val = default
        if len (val.strip ()) > 0:
            vals.append (val)
        else:
            break
    d[key] = vals
    return vals
    
def generate (vals):

    vals['class_name'] = camel_case (vals['name'])
    vals['license'] = 'MIT'
    vals['copyright'] = ', '.join ([time.strftime ('%Y'), vals['author']])

    file = vals['class_name'].lower ()+'.py'

    from string import Template
    with open (file, 'w') as f:
        bmi_file = Template (QUICKSTART_BMI)
        f.write (bmi_file.substitute (vals))

def main ():
    print bright ('Welcome to the BMI quickstart utility')
    print """
Please enter values for the following settings (press Enter to accept a
default, if one is given in square brackets)."""

    vals = {}

    print """
Enter name of your model."""
    prompt_for_val (vals, 'name', 'Model name')
    prompt_for_val (vals, 'author', 'Author name')
    prompt_for_val (vals, 'version', 'Version')

    print """
List of output variable names. These are the names of variarbles that your
model is able to provide through a 'getter' function."""
    prompt_for_val (vals, 'output_items', 'Output items', default='')

    print """
List of input variable names. These are the names of variarbles that another
model is able to set through a 'setter' function."""
    prompt_for_val (vals, 'input_items', 'Input items', default='')

    print """
Grid type:
    [0] = Uniform rectilinear
    [1] = Rectilinear
    [2] = Structured
    [4] = Unstructured"""
    prompt_for_val (vals, 'gridtype', 'Grid type', default='0')

    generate (vals)

    print bright ('Finished: An initial BMI class has been created for your model.')
    print """
You should now populate your BMI file (%s) with implementation for each of the
class methods.""" % (vals['class_name'].lower ()+'.py')


prm_intro_template = """
#@model ${model_short_name}
#    @longname ${model_long_name}
#    @author ${model_author}
#    @version ${model_version}
"""
def generate_prm (vals):

    optionals = ['email', 'url']
    file = '_'.join (vals['model_short_name'].lower ().split ()) + '.prm'

    from string import Template
    with open (file, 'w') as f:
        prm_file = Template (prm_intro_template)
        f.write (prm_file.substitute (vals))
        for opt in optionals:
            if not vals[opt] is None:
                f.write ('#    @%s %s\n' % (opt, vals[opt]))

        f.write ('#\n')
        for param in vals['params']:
            f.write ('#    @param %s\n' % param)
            f.write ('#        @brief \n')
            f.write ('#        @description \n')
            f.write ('#        @range \n')
            f.write ('#        @units \n')

        f.write ('#\n')
        for param in vals['outparams']:
            f.write ('#    @param[out] %s\n' % param)

def make_prm ():
    print bright ('Welcome to the BMI quickstart utility')
    print """
Please enter values for the following settings (press Enter to accept a
default, if one is given in square brackets)."""

    vals = {}

    print """
Model information ."""

    prompt_for_val (vals, 'model_long_name', 'Model name')
    prompt_for_val (vals, 'model_short_name', 'Model nick name', vals['model_long_name'])
    prompt_for_val (vals, 'model_author', 'Author name')
    prompt_for_val (vals, 'model_version', 'Version')
    prompt_for_val (vals, 'url', 'URL', default=None)
    prompt_for_val (vals, 'email', 'Author email', default=None)

    prompt_for_vals (vals, 'params', 'Input parameters', default=None)

    prompt_for_vals (vals, 'outparams', 'Output parameters', default=None)

    generate_prm (vals)

if __name__ == '__main__':
    make_prm ()

