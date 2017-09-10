from distutils.core import setup


from setuptools import setup
import sys
import os

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

setup(
    name='appurl',
    version='0.1.1',
    url='https://github.com/CivicKnowledge/appurl',
    license='MIT',
    author='Eric Busboom',
    author_email='eric@busboom.org',
    description='Url manipulation for extended application urls',
    zip_safe=True,
    install_requires=[
        'fs >= 2',
        'boto',
        'requests'
        ],
    entry_points = {
        'appurl.urls' : [
            "* = appurl.url:Url",

            #
            "http: = appurl.web.web:WebUrl",
            "https: = appurl.web.web:WebUrl",
            "s3: = appurl.web.s3:S3Url",
            "socrata+ = appurl.web.socrata:SocrataUrl",
            #
            # Archive Urls
            ".zip = appurl.archive.zip:ZipUrl",
            #
            # File Urls
            ".csv = appurl.file.csv:CsvFileUrl",
            ".xlsx = appurl.file.excel:ExcelFileUrl",
            ".xls = appurl.file.excel:ExcelFileUrl",
            "file: = appurl.file.file:FileUrl",
        ]
    }
)