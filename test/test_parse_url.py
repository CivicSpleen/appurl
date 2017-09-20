from __future__ import print_function

import unittest

from appurl.url import parse_app_url
from appurl.util import get_cache
from appurl.web.download import Downloader


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



class TestUrlParse(unittest.TestCase):

    def test_fragment(self):

        def u(frag):
            return parse_app_url("http://example.com/foo.csv#"+frag)

        self.assertEqual({}, u('a').fragment_query)
        self.assertEqual({}, u('a;b').fragment_query)
        self.assertEqual({'foo': 'bar'}, u('a;b&foo=bar').fragment_query)
        self.assertEqual({'foo': 'bar'}, u('a;&foo=bar').fragment_query)
        self.assertEqual({'foo': 'bar'}, u('a&foo=bar').fragment_query)
        self.assertEqual({'foo': 'bar'}, u('&foo=bar').fragment_query)
        self.assertEqual({'foo': 'bar'}, u(';&foo=bar').fragment_query)

        url = u('a;b&encoding=utf8')

        self.assertEquals('utf8', url.encoding)

        url.encoding = 'ascii'
        url.start = 5


        self.assertEquals('http://example.com/foo.csv#a;b&encoding=ascii&start=5', str(url))

        url = u('a;b&target_format=foo&resource_format=bar')

        self.assertEquals('foo', url.target_format)
        self.assertEquals('bar', url.resource_format)

        print(parse_app_url('http://public.source.civicknowledge.com/example.com/sources/unicode-utf8.csv#encoding=utf8'))

        us = 'http://public.source.civicknowledge.com/example.com/sources/test_data.zip#unicode-latin1.csv&encoding=latin1'

        url = parse_app_url(us)

        self.assertEquals('latin1',url.encoding)
        self.assertEquals('latin1', url.get_resource().encoding)
        self.assertEquals('latin1', url.get_resource().get_target().encoding)

    def test_fragment_2(self):

        url = parse_app_url(
            'http://public.source.civicknowledge.com/example.com/sources/renter_cost_excel07.zip#target_format=xlsx')

        self.assertEqual('zip', url.resource_format)
        self.assertEqual('renter_cost_excel07.zip', url.target_file)
        self.assertEqual('xlsx', url.target_format)

        r = url.get_resource()

        self.assertEqual('xlsx', r.target_format)
        self.assertEqual('zip',r.resource_format)

    def test_two_extensions(self):
        u_s = 'http://public.source.civicknowledge.com/example.com/sources/simple-example.csv.zip'

        u = parse_app_url(u_s, Downloader())

        self.assertEqual('simple-example.csv.zip', u.resource_file)
        self.assertEqual('simple-example.csv.zip', u.target_file)
        self.assertEqual('zip', u.target_format)

        r = u.get_resource()
        self.assertEqual('simple-example.csv.zip', r.resource_file)
        self.assertEqual('simple-example.csv', r.target_file)
        self.assertEqual('csv', r.target_format)

    def test_parse_app_args(self):

        url = parse_app_url('/foo/bar/file.csv', fragment='target_file.foo', fragment_query={'target_format':'foo1'})

        print (url)

    def test_shapefile_url(self):

        u_s = 'shapefile+http://public.source.civicknowledge.com.s3.amazonaws.com/example.com/geo/Parks_SD.zip'

        u = parse_app_url(u_s)

        print(type(u))

        r = u.get_resource()

        self.assertTrue(str(r).startswith('shapefile+'))

    def test_s3_url(self):

        from appurl.web.s3 import S3Url

        url_str = 's3://bucket/a/b/c/file.csv'

        u = parse_app_url(url_str)

        self.assertIsInstance(u, S3Url)

    def test_queries(self):

        u =  parse_app_url('https://data.lacounty.gov/api/views/8rdv-6nb6/rows.csv?accessType=DOWNLOAD#resource_file=rows.csv')

        print (u.proto)
        print(u.get_resource())


    def test_python_url(self):

        from appurl.file import python
        from rowgenerators import get_generator
        from types import ModuleType

        import sys

        foo = ModuleType('foo')
        sys.modules['foo'] = foo
        foo.bar = ModuleType('bar')
        sys.modules['foo.bar'] = foo.bar
        foo.bar.baz = ModuleType('baz')
        sys.modules['foo.bar.baz'] = foo.bar.baz

        def foobar(*args, **kwargs):
            for i in range(10):
                yield i

        foo.bar.baz.foobar = foobar

        u = parse_app_url("python:foo.bar.baz#foobar")

        g = get_generator(u)

        self.assertEqual(45, sum(list(g)))

if __name__ == '__main__':
    unittest.main()