from __future__ import print_function

import unittest
from copy import deepcopy
from csv import DictReader, DictWriter
import platform
from csv import DictReader
from os.path import exists

from appurl.util import nuke_cache
from appurl.web.download import Downloader
from appurl.util import get_cache
from appurl.url import Url, parse_app_url
from appurl.web.s3 import S3Url
from appurl.web.web import WebUrl
from appurl.archive.zip import ZipUrl
from appurl.file.csv import CsvFileUrl

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


def sources():
    import csv
    with open(data_path('sources.csv')) as f:
        r = csv.DictReader(f)
        return list(r)


def cache_fs():
    from fs.tempfs import TempFS

    return TempFS('rowgenerator')


class BasicTests(unittest.TestCase):

    def compare_dict(self, name, a, b):
        from rowgenerators.util import flatten
        fa = set('{}={}'.format(k, v) for k, v in flatten(a));
        fb = set('{}={}'.format(k, v) for k, v in flatten(b));

        # The declare lines move around a lot, and rarely indicate an error
        fa = {e for e in fa if not e.startswith('declare=')}
        fb = {e for e in fb if not e.startswith('declare=')}

        errors = len(fa - fb) + len(fb - fa)

        if errors:
            print("=== ERRORS for {} ===".format(name))

        if len(fa - fb):
            print("In a but not b")
            for e in sorted(fa - fb):
                print('    ', e)

        if len(fb - fa):
            print("In b but not a")
            for e in sorted(fb - fa):
                print('    ', e)

        self.assertEqual(0, errors)


    def test_entry_points(self):



        self.assertIsInstance(parse_app_url('s3://bucket.com/foo/bar/baz.zip'), S3Url)
        self.assertIsInstance(parse_app_url('http://bucket.com/foo/bar/baz.zip'), WebUrl)
        self.assertIsInstance(parse_app_url('file://bucket.com/foo/bar/baz.zip'), ZipUrl)

    def test_entry_point_priorities(self):
        from pkg_resources import iter_entry_points

        for ep in iter_entry_points(group='appurl.urls'):
            c = ep.load()
            print(c, c.match_priority)

    def test_zip_basic(self):

        def callback(code, url, size):
            if code == 'download':
                print(code, url, size)

        dldr = Downloader(get_cache(), callback=callback)

        nuke_cache(get_cache())

        u_s = 'http://public.source.civicknowledge.com/example.com/sources/test_data.zip#simple-example.csv'

        u = parse_app_url(u_s)
        self.assertIsInstance(u, WebUrl)
        self.assertEqual(u_s, str(u))

        r = u.get_resource(dldr)
        self.assertIsInstance(r, ZipUrl)
        self.assertEqual('file', r.proto)
        self.assertTrue(exists(r.path))

        t = r.get_target()
        self.assertIsInstance(t, CsvFileUrl)
        self.assertEqual('file', r.proto)
        self.assertTrue(exists(r.path))

        self.assertEqual('e4732aa75d0e3f712653e718851f64b8', md5(t.path))

        self.assertEqual('e4732aa75d0e3f712653e718851f64b8', md5(parse_app_url(u_s).get_resource(dldr).get_target().path))

        self.assertEqual('e4732aa75d0e3f712653e718851f64b8',
                         md5(parse_app_url(u_s, dldr).get_resource().get_target().path))


    def test_two_extensions(self):

        u_s = 'http://public.source.civicknowledge.com/example.com/sources/simple-example.csv.zip'

        u = parse_app_url(u_s, Downloader(get_cache()))
        print(type(u), u, u.target_file)

        r = u.get_resource()
        self.assertEqual('simple-example.csv.zip', r.resource_file)
        self.assertEqual('simple-example.csv', r.target_file)



    def test_download(self):
        """Test all three stages of a collection of downloadable URLS"""

        dldr = Downloader(get_cache())

        with open(data_path('sources.csv')) as f:
            for e in DictReader(f):
                u = parse_app_url(e['url'])

                if not e['resource_class']:
                    continue

                self.assertEqual(e['url_class'], u.__class__.__name__)

                r = u.get_resource(dldr)
                self.assertEqual(e['resource_class'],r.__class__.__name__)

                t = r.get_target()
                self.assertEqual(e['target_class'], t.__class__.__name__)
                self.assertTrue(exists(t.path))


    def test_base_url(self):
        """Simple test of splitting and recombining"""

        for u_s in ('http://server.com/a/b/c/file.csv','http://server.com/a/b/c/file.csv#a',
                    'http://server.com/a/b/c/file.csv#a;b', 'http://server.com/a/b/c/archive.zip#file.csv'):
            self.assertEqual(u_s, str(Url(u_s)))

        self.assertEqual('file.csv', Url('http://server.com/a/b/c/file.csv').target_file)
        self.assertEqual('file.csv', Url('http://server.com/a/b/c/file.csv').resource_file)
        self.assertEqual('http://server.com/a/b/c/file.csv', Url('http://server.com/a/b/c/file.csv').resource_url)

        self.assertEqual('file.csv', Url('http://server.com/a/b/c/resource.zip#file.csv').target_file)
        self.assertEqual('resource.zip', Url('http://server.com/a/b/c/resource.zip#file.csv').resource_file)

    def test_urls(self):

        headers = "in_url class url resource_url resource_file target_file scheme proto resource_format target_format " \
                  "is_archive encoding target_segment".split()

        import tempfile
        tf = tempfile.NamedTemporaryFile(prefix="rowgen", delete=False)
        temp_name = tf.name
        tf.close()

        # S3 URLS have these fields which need to be removed before writing to CSV files.
        def clean(do):

            for f in ['_orig_url', '_key', '_orig_kwargs', '_bucket_name']:
                try:
                    del do[f]
                except KeyError:
                    pass

        with open(data_path('url_classes.csv')) as f, open(temp_name, 'w') as f_out:
            w = None
            r = DictReader(f)
            errors = 0
            for i, d in enumerate(r):

                url = d['in_url']

                o = Url(url)

                do = dict(o.__dict__.items())

                if w is None:
                    w = DictWriter(f_out, fieldnames=headers)
                    w.writeheader()
                do['in_url'] = url
                do['is_archive'] = o.is_archive
                do['class'] = o.__class__.__name__
                clean(do)
                w.writerow(dict( (k,v) for k,v in do.items() if k in headers) )

                d = {k: v if v else None for k, v in d.items()}
                do = {k: str(v) if v else None for k, v in do.items()}  # str() turns True into 'True'

                # a is the gague data from url_classes.csv
                # b is the test object.

                try:  # A, B
                    self.compare_dict(url, d, do)
                except AssertionError as e:
                    errors += 1
                    print(e)
                    # raise

            self.assertEqual(0, errors)

        with open(data_path('url_classes.csv')) as f:

            r = DictReader(f)
            for i, d in enumerate(r):
                u1 = Url(d['in_url'])

        with open(data_path('url_classes.csv')) as f:

            r = DictReader(f)
            for i, d in enumerate(r):
                u1 = Url(d['in_url'])
                d1 = u1.__dict__.copy()
                d2 = deepcopy(u1).__dict__.copy()

                # The parts will be different Bunch objects
                clean(d1)
                clean(d2)
                del d1['parts']
                del d2['parts']

                self.assertEqual(d1, d2)

                self.assertEqual(d1, u1.dict)

        for us in ("http://example.com/foo.zip", "http://example.com/foo.zip#a;b"):
            u = Url(us, encoding='utf-8')
            u2 = u.update(target_file='bingo.xls', target_segment='1')

            self.assertEqual('utf-8', u2.dict['encoding'])
            self.assertEqual('bingo.xls', u2.dict['target_file'])
            self.assertEqual('1', u2.dict['target_segment'])

    def test_url_update(self):

        u1 = Url('http://example.com/foo.zip')

        self.assertEqual('http://example.com/foo.zip#bar.xls', u1.rebuild_url(target_file='bar.xls'))
        self.assertEqual('http://example.com/foo.zip#0', u1.rebuild_url(target_segment=0))
        self.assertEqual('http://example.com/foo.zip#bar.xls%3B0',
                         u1.rebuild_url(target_file='bar.xls', target_segment=0))

        u2 = u1.update(target_file='bar.xls')

        self.assertEqual('bar.xls', u2.target_file)
        self.assertEqual('xls', u2.target_format)

        self.assertEqual('http://example.com/foo.zip', u1.rebuild_url(False, False))

        self.assertEqual('file:metatadata.csv', Url('file:metatadata.csv').rebuild_url())

    def test_parse_file_urls(self):
        from rowgenerators.util import parse_url_to_dict, unparse_url_dict, reparse_url
        urls = [
            ('file:foo/bar/baz', 'foo/bar/baz', 'file:foo/bar/baz'),
            ('file:/foo/bar/baz', '/foo/bar/baz', 'file:/foo/bar/baz'),
            ('file://example.com/foo/bar/baz', '/foo/bar/baz', 'file://example.com/foo/bar/baz'),
            ('file:///foo/bar/baz', '/foo/bar/baz', 'file:/foo/bar/baz'),
        ]

        for i, o, u in urls:
            p = parse_url_to_dict(i)
            self.assertEqual(o, p['path'])
            self.assertEqual(u, unparse_url_dict(p))
            # self.assertEqual(o, parse_url_to_dict(u)['path'])

        return

        print(reparse_url("metatab+http://library.metatab.org/cdph.ca.gov-county_crosswalk-ca-2#county_crosswalk",
                          scheme_extension=False, fragment=False))

        d = {'netloc': 'library.metatab.org', 'params': '', 'path': '/cdph.ca.gov-county_crosswalk-ca-2',
             'password': None, 'query': '', 'hostname': 'library.metatab.org', 'fragment': 'county_crosswalk',
             'resource_format': 'gov-county_crosswalk-ca-2', 'port': None, 'scheme_extension': 'metatab',
             'proto': 'metatab', 'username': None, 'scheme': 'http'}

        print(unparse_url_dict(d, scheme_extension=False, fragment=False))

    def test_metatab_url(self):

        urlstr = 'metatab+http://s3.amazonaws.com/library.metatab.org/cdss.ca.gov-residential_care_facilities-2017-ca-7.csv#facilities'

        u = Url(urlstr)

        self.assertEqual('http', u.scheme)
        self.assertEqual('metatab', u.proto)
        self.assertEqual('http://s3.amazonaws.com/library.metatab.org/cdss.ca.gov-residential_care_facilities-2017-ca-7.csv', u.resource_url)
        self.assertEqual('cdss.ca.gov-residential_care_facilities-2017-ca-7.csv', u.target_file)
        self.assertEqual('facilities', u.target_segment)


    @unittest.skipIf(platform.system() == 'Windows','ProgramSources don\'t work on Windows')
    def test_program(self):
        from rowgenerators import parse_url_to_dict

        urls = (
            ('program:rowgen.py', 'rowgen.py'),
            ('program:/rowgen.py', '/rowgen.py'),
            ('program:///rowgen.py', '/rowgen.py'),
            ('program:/a/b/c/rowgen.py', '/a/b/c/rowgen.py'),
            ('program:/a/b/c/rowgen.py', '/a/b/c/rowgen.py'),
            ('program:a/b/c/rowgen.py', 'a/b/c/rowgen.py'),
            ('program+http://foobar.com/a/b/c/rowgen.py', '/a/b/c/rowgen.py'),
        )

        for u, v in urls:
            url = Url(u)

            self.assertEquals(url.path, v, u)

        cache = cache_fs()

        options = {
            '-a': 'a',
            '-b': 'b',
            '--foo': 'foo',
            '--bar': 'bar'
        }

        options.update({'ENV1': 'env1', 'ENV2': 'env2', 'prop1': 'prop1', 'prop2': 'prop2'})

        gen = RowGenerator(cache=cache, url='program:rowgen.py', working_dir=script_path(),
                           generator_args=options)

        rows = list(gen)

        for row in rows:
            print(row)


    def test_notebook(self):
        from rowgenerators.fetch import download_and_cache

        urls = (
            'ipynb+file:foobar.ipynb',
            'ipynb+http://example.com/foobar.ipynb',
            'ipynb:foobar.ipynb'

        )




    def test_component_url(self):

        with open(data_path('components.csv')) as f:
            for l in DictReader(f):
                base_url = Url(l['base_url'])
                component_url = l['component_url']
                curl = base_url.component_url(component_url)

                self.assertEquals(l['final_url'], curl )


    def test_windows_urls(self):

        url = 'w:/metatab36/metatab-py/metatab/templates/metatab.csv'

        print(parse_url_to_dict(url))

        url = 'N:/Desktop/metadata.csv#renter_cost'

        print(parse_url_to_dict(url))

    def test_query_urls(self):

        url='https://s3.amazonaws.com/private.library.civicknowledge.com/civicknowledge.com-rcfe_health-1/metadata.csv?AWSAccessKeyId=AKIAJFW23EPQCLXRU7DA&Signature=A39XhRP%2FTKAxv%2B%2F5vCubwWPDag0%3D&Expires=1494223447'

        u = Url(url)

        print(u.resource_file, u.resource_format)
        print(u.target_file, u.target_format)


    def test_s3_url(self):

        from rowgenerators.urls import S3Url

        url_str = 's3://bucket/a/b/c/file.csv'

        u = Url(url_str)

        self.assertEquals(S3Url, type(u))




if __name__ == '__main__':
    unittest.main()
