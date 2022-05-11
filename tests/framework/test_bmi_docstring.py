from pymt.framework.bmi_docstring import bmi_docstring

DOCSTRING = """Basic Model Interface for Model.




Version: None
License: None
DOI: None
URL: None


Examples
--------
>>> from pymt.models import Model
>>> model = Model()
>>> (fname, initdir) = model.setup()
>>> model.initialize(fname, dir=initdir)  # doctest: +SKIP
>>> for _ in range(10):  # doctest: +SKIP
...     model.update()
>>> model.finalize()  # doctest: +SKIP
""".strip()


def test_empty_docstring():
    docstring = bmi_docstring("Model")
    assert docstring == DOCSTRING


def test_full_docstring():
    docstring = bmi_docstring(
        "DirtyHarry",
        author="Clint Eastwood",
        summary="The Good, The Bad, and the Ugly",
        version="0.1",
        license="To kill",
        doi="1977.12.23",
        url="welldoyapunk.org",
    )
    assert (
        docstring
        == """
Basic Model Interface for DirtyHarry.

The Good, The Bad, and the Ugly

Author:
- Clint Eastwood
Version: 0.1
License: To kill
DOI: 1977.12.23
URL: welldoyapunk.org


Examples
--------
>>> from pymt.models import DirtyHarry
>>> model = DirtyHarry()
>>> (fname, initdir) = model.setup()
>>> model.initialize(fname, dir=initdir)  # doctest: +SKIP
>>> for _ in range(10):  # doctest: +SKIP
...     model.update()
>>> model.finalize()  # doctest: +SKIP
""".strip()
    )


def test_cite_as():
    docstring = bmi_docstring(
        "DirtyHarry",
        author="Clint Eastwood",
        summary="The Good, The Bad, and the Ugly",
        version="0.1",
        license="To kill",
        doi="1977.12.23",
        url="welldoyapunk.org",
        cite_as=["ref1", "ref2"],
    )

    assert (
        docstring
        == """
Basic Model Interface for DirtyHarry.

The Good, The Bad, and the Ugly

Author:
- Clint Eastwood
Version: 0.1
License: To kill
DOI: 1977.12.23
URL: welldoyapunk.org

Cite as:

    ref1

    ref2

Examples
--------
>>> from pymt.models import DirtyHarry
>>> model = DirtyHarry()
>>> (fname, initdir) = model.setup()
>>> model.initialize(fname, dir=initdir)  # doctest: +SKIP
>>> for _ in range(10):  # doctest: +SKIP
...     model.update()
>>> model.finalize()  # doctest: +SKIP
""".strip()
    )
