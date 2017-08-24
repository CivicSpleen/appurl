from distutils.core import setup



from setuptools import setup
import sys
import os

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

setup(
    name='appurl',
    version='0.0.1',
    url='https://github.com/CivicKnowledge/appurl',
    license='MIT',
    author='Eric Busboom',
    author_email='eric@busboom.org',
    description='Url manipulation for extended application urls',
    zip_safe=True,
    entry_points = {
        'appurl.urls' : [
            "* = appurl.url:GeneralUrl",
            ".zip = appurl.zip:ZipUrl",
            "s3: = appurl.s3:S3Url"
        ]
    }
)