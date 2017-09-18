from __future__ import print_function

import unittest

from appurl.url import parse_app_url, Url
from appurl.util import get_cache
from appurl.web.download import Downloader
from appurl.archive.zip import ZipUrl
from appurl.file.csv import CsvFileUrl
from appurl.web import WebUrl

# From https://stackoverflow.com/a/3431838
def md5(fname):
    import hashlib
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def data_path(v):
    from os.path import dirname, join
    d = dirname(dirname(__file__))
    return join(d, 'test_data', v)


def script_path(v=None):
    from os.path import dirname, join
    d = dirname(__file__)
    if v is not None:
        return join(d, 'scripts', v)
    else:
        return join(d, 'scripts')



class TestIssues(unittest.TestCase):

    def test_spec_resource_format(self):



        us='http://public.source.civicknowledge.com/example.com/sources/test_data.foo#simple-example.csv&resource_format=zip'

        u = parse_app_url(us)

        self.assertEqual('zip', u.resource_format)
        self.assertEqual('csv',u.target_format)

        r = u.get_resource()
        self.assertIsInstance(r, ZipUrl)

        t = r.get_target()
        self.assertIsInstance(t, CsvFileUrl)


    def test_csv_no_csv(self):
        u = parse_app_url('http://public.source.civicknowledge.com/example.com/sources/simple-example.foo#&target_format=csv')

        self.assertIsInstance(u, WebUrl)
        self.assertEqual('foo', u.resource_format)
        self.assertEqual('csv', u.target_format)

        r = u.get_resource()
        self.assertEqual('foo', r.resource_format)
        self.assertEqual('csv', r.target_format)

        t = r.get_resource()
        self.assertEqual('csv', t.target_format)


    def test_excel_renter07(self):

        u = parse_app_url('http://public.source.civicknowledge.com/example.com/sources/renter_cost_excel07.zip#target_format=xlsx')

        r = u.get_resource()
        self.assertEqual('file', r.proto)
        self.assertTrue(r.exists())

        print(u.target_file)


        t = r.get_target()
        self.assertEqual('file', t.proto)
        self.assertTrue(t.exists())


    def test_mz_with_zip_xl(self):
        u = parse_app_url(
            'http://public.source.civicknowledge.com/example.com/sources/test_data.zip#renter_cost_excel07.xlsx')

        self.assertIsInstance(u, WebUrl)
        self.assertEquals('zip', u.resource_format)
        self.assertEqual('xlsx', u.target_format)

        r = u.get_resource()
        self.assertIsInstance(r, ZipUrl)
        self.assertEquals('zip', r.resource_format)
        self.assertEqual('file', r.proto)
        self.assertTrue(r.exists())


        t = r.get_target()
        print(t)
        self.assertEqual('xlsx', t.target_format)
        self.assertEqual('file', t.proto)
        self.assertTrue(t.exists())


    def test_fragement_ts_tf(self):

        url = Url('http://example.com/foo.csv#a;b&encoding=utf8')

        print(url.dict)

        return

        url = parse_app_url('http://example.com/foo.csv#a;b&encoding=utf8')

        print(url.dict)

        self.assertEquals('utf8', url.encoding)

        url.encoding = 'ascii'
        url.start = 5

        self.assertEquals('http://example.com/foo.csv#a;b&encoding=ascii&start=5', str(url))

    def test_xlsx_fragment(self):

        url = parse_app_url('http://example.com/renter_cost_excel07.xlsx#2')

        print(url.dict)

    def test_xsx_zip_fragment(self):

        url = parse_app_url('http://public.source.civicknowledge.com/example.com/sources/test_data.zip#renter_cost_excel07.xlsx;Sheet1')

        print(url.fragment)

    def test_join_target_xls(self):
        u = parse_app_url('file:/a/file.xlsx')

        jt = u.join_target('target')
        print(jt.dict)
        self.assertEquals('file:/a/file.xlsx#target', str(jt))

    def test_join_target_xls(self):
        u = parse_app_url('file:/a/file.xlsx#foobnar')

        print(type(u))

    def test_parse_s3(self):

        u = parse_app_url(('s3://library.metatab.org'))

        print(u)

    def test_join_file_urls(self):

        us1 = 'file:documentation.md'
        us2 = ''



if __name__ == '__main__':
    unittest.main()