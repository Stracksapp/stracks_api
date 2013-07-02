from setuptools import setup, find_packages
import sys, os

version = '0.2'

setup(name='stracks_api',
      version=version,
      description="API for Stracks service",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Ivo van der Wijk',
      author_email='stracks-api@in.m3r.nl',
      url='http://github.com/Stracksapp/stracks_api',
      license='',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'requests',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
