from distutils.core import setup



from setuptools import setup
import sys
import os

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

setup(
    name='metatabdecl',
    version='0.2',
    packages=['metatabdecl'],
    package_data={'metatabdecl': ['*.csv','*.json']},
    url='https://github.com/CivicKnowledge/metatab-declarations',
    license='MIT',
    author='Eric Busboom',
    author_email='eric@busboom.org',
    description='Url manipulation for extended application urls',
    zip_safe=True
)