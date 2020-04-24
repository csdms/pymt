from setuptools import setup, find_packages

import versioneer


setup(
    name="pymt",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description="The CSDMS Python Modeling Toolkit",
    long_description=open("README.rst", encoding="utf-8").read(),
    author="Eric Hutton",
    author_email="huttone@colorado.edu",
    url="http://csdms.colorado.edu",
    python_requires=">=3.6",
    install_requires=open("requirements.txt", "r").read().splitlines(),
    include_package_data=True,
    setup_requires=[],
    classifiers=[
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Cython",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Scientific/Engineering :: Physics",
    ],
    packages=find_packages(exclude=("tests*",)),
    entry_points={"console_scripts": ["cmt-config=cmt.cmd.cmt_config:main"]},
)
