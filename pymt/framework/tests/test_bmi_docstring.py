from nose.tools import assert_equal

from pymt.framework.bmi_docstring import bmi_docstring

DOCSTRING = u"""Basic Model Interface for Model.



Author: None
Version: None
License: None
DOI: None
URL: None
Examples
--------
>>> from pymt.components import Model
>>> model = Model()
>>> (fname, initdir) = model.setup()
>>> model.initialize(fname, dir=initdir)
>>> for _ in xrange(10):
...     model.update()
>>> model.finalize()
""".strip()


def test_empty_docstring():
    docstring = bmi_docstring('Model')
    assert_equal(docstring, DOCSTRING)


def test_full_docstring():
    docstring = bmi_docstring('DirtyHarry', author='Clint Eastwood',
                              summary='The Good, The Bad, and the Ugly',
                              version='0.1', license='To kill',
                              doi='1977.12.23', url='welldoyapunk.org')
    assert_equal(docstring, """
Basic Model Interface for DirtyHarry.

The Good, The Bad, and the Ugly

Author: Clint Eastwood
Version: 0.1
License: To kill
DOI: 1977.12.23
URL: welldoyapunk.org
Examples
--------
>>> from pymt.components import DirtyHarry
>>> model = DirtyHarry()
>>> (fname, initdir) = model.setup()
>>> model.initialize(fname, dir=initdir)
>>> for _ in xrange(10):
...     model.update()
>>> model.finalize()
""".strip())
