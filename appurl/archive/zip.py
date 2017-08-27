# Copyright (c) 2017 Civic Knowledge. This file is licensed under the terms of the
# MIT, included in this distribution as LICENSE

""" """


from appurl.url import Url, parse_app_url
from appurl.util import file_ext
from zipfile import ZipFile
import io
from os.path import join, dirname
from appurl.util import copy_file_or_flo, ensure_dir

def real_files_in_zf(zf):
    """Return a list of internal paths of real files in a zip file, based on the 'external_attr' values"""
    from os.path import basename

    for e in zf.infolist():

        # Get rid of __MACOS and .DS_whatever
        if basename(e.filename).startswith('__') or basename(e.filename).startswith('.'):
            continue

        # I really don't understand external_attr, but no one else seems to either,
        # so we're just hacking here.
        # e.external_attr>>31&1 works when the archive has external attrs set, and a dir heirarchy
        # e.external_attr==0 works in cases where there are no external attrs set
        # e.external_attr==32 is true for some single-file archives.
        if bool(e.external_attr >> 31 & 1 or e.external_attr == 0 or e.external_attr == 32):
            yield e.filename


def get_file_from_zip(url):
    """Given a file name that may be a regular expression, return the full name for the file
    from a zip archive"""

    from zipfile import ZipFile
    import re

    zf = ZipFile(url.path)

    nl = list(real_files_in_zf(zf)) # Old way, but maybe gets links? : list(zf.namelist())

    # the target_file may be a string, or a regular expression
    if url.target_file:
        names = list([e for e in nl if re.search(url.target_file, e)
                      and not (e.startswith('__') or e.startswith('.'))
                      ])
        if len(names) > 0:
            return names[0]

    # The segment, if it exists, can only be an integer, and should probably be
    # '0' to indicate the first file. This clause is probably a bad idea, since
    # andy other integer is probably meaningless.
    if url.target_segment:
        try:
            return nl[int(url.target_segment)]

        except (IndexError, ValueError):
            pass

    # Just return the first file in the archive.
    return nl[0]


class ZipUrl(Url):

    match_priority = 40

    def __init__(self, url=None, downloader=None, **kwargs):
        kwargs['resource_format'] = 'zip'
        super().__init__(url, downloader=downloader, **kwargs)

    @classmethod
    def match(cls, url, **kwargs):

       return url.resource_format == 'zip' or kwargs.get('force_archive')

    def _process_fragment(self):

        if self.fragment:
            self.target_file, self.target_segment = self.decompose_fragment(self.fragment, self.is_archive)

        else:
            self.target_file = self.target_segment = None

    def _process_target_file(self):

        # Handles the case of file.csv.zip, etc.
        for ext in ('csv', 'xls', 'xlsx'):
            if self.resource_file.endswith('.' + ext + '.zip'):
                self.target_file = self.resource_file.replace('.zip', '')

        if self.target_file and not self.target_format:
            self.target_format = file_ext(self.target_file)

    def get_resource(self, downloader=None):
        """Get the contents of resource and save it to the cache, returning a file-like object"""

        return self

    @property
    def zip_dir(self):
        return self.path.replace('.zip','_zip') # Hope that the '.zip is only at the end

    def get_target(self, mode=None):
        """Get the contents of the target, and save it to the cache, returning a file-like object
        :param downloader:
        :param mode:
        """


        target_path = join(self.zip_dir, self.target_file)

        zf = ZipFile(self.path)

        filename = get_file_from_zip(self)

        if (mode and 'b' in mode) or (not self.encoding):
            flo = zf.open(filename, mode.replace('b', '') if mode else 'r' )
        else:
            flo = io.TextIOWrapper(zf.open(filename, mode or 'r'),
                                   encoding=self.encoding if self.encoding else 'utf8')


        ensure_dir(dirname(target_path))

        with io.open(target_path, 'wb') as f:
            copy_file_or_flo(flo, f)

        return parse_app_url(target_path)
