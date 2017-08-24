from __future__ import print_function

import unittest
from copy import deepcopy
from csv import DictReader, DictWriter
import platform

from appurl import Url, parse_app_url



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
