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

    def test_spec_resource_format(self):

        from appurl.archive.zip import ZipUrl
        from appurl.file.csv import CsvFileUrl

        us='http://public.source.civicknowledge.com/example.com/sources/test_data.foo#simple-example.csv&resource_format=zip'

        u = parse_app_url(us)

        self.assertEqual('zip', u.resource_format)
        self.assertEqual('csv',u.target_format)

        r = u.get_resource()
        self.assertIsInstance(r, ZipUrl)

        t = r.get_target()
        self.assertIsInstance(t, CsvFileUrl)


if __name__ == '__main__':
    unittest.main()