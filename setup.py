from setuptools import setup, find_packages

import versioneer


setup(
    name="pymt-core",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description="The CSDMS Python Modeling Toolkit",
    long_description=open("README.rst").read(),
    author="Eric Hutton",
    author_email="huttone@colorado.edu",
    url="http://csdms.colorado.edu",
    setup_requires=["setuptools"],
    install_requires=[
        "cfunits",
        "deprecated",
        # "esmpy",
        "jinja2",
        "landlab",
        "matplotlib",
        "model_metadata",
        "netcdf4",
        "numpy",
        "pyyaml",
        "scipy",
        "py-scripting",
        "shapely",
        "six",
        "xarray",
    ],
    packages=find_packages(exclude=("tests*",)),
    entry_points={"console_scripts": ["cmt-config=cmt.cmd.cmt_config:main"]},
)
