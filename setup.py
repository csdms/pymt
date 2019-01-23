from setuptools import setup, find_packages

import versioneer


def read_requirements():
    import os


    path = os.path.dirname(os.path.abspath(__file__))
    requirements_file = os.path.join(path, 'requirements.txt')
    try:
        with open(requirements_file, 'r') as req_fp:
            requires = req_fp.read().split()
    except IOError:
        return []
    else:
        return [require.split() for require in requires]


setup(name='PyMT',
      version=versioneer.get_version(),
      cmdclass=versioneer.get_cmdclass(),
      description='The CSDMS Python Modeling Toolkit',
      author='Eric Hutton',
      author_email='huttone@colorado.edu',
      url='http://csdms.colorado.edu',
      setup_requires=['setuptools', ],
      packages=find_packages(exclude=("tests*", "cmt")),
      entry_points={
          'console_scripts': [
              'cmt-config=cmt.cmd.cmt_config:main',
          ],
      },
)
