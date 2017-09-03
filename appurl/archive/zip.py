# Copyright (c) 2017 Civic Knowledge. This file is licensed under the terms of the
# MIT, included in this distribution as LICENSE

""" """


from appurl.url import Url, parse_app_url
from appurl.util import file_ext
from appurl.file import FileUrl
from appurl.exc import AppUrlError
from zipfile import ZipFile
import io
from os.path import join, dirname
from appurl.util import copy_file_or_flo, ensure_dir

class ZipUrlError(AppUrlError):
    pass


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

    tf = url.target_file
    ts = url.target_segment

    if not nl:
        # sometimes real_files_in_zf doesn't work at all. I don't know why it does work,
        # so I certainly don't know why it does not.
        nl = list(zf.namelist())

    # the target_file may be a string, or a regular expression
    if tf:
        names = list([e for e in nl if re.search(tf, e)
                      and not (e.startswith('__') or e.startswith('.'))
                      ])
        if len(names) > 0:
            return names[0]

    # The segment, if it exists, can only be an integer, and should probably be
    # '0' to indicate the first file. This clause is probably a bad idea, since
    # andy other integer is probably meaningless.
    if ts:
        try:
            return nl[int(ts)]

        except (IndexError, ValueError):
            pass

    # Just return the first file in the archive.
    if not tf and not ts:
        return nl[0]
    else:
        raise ZipUrlError("Could not find file in Zip for target='{}' nor segment='{}'".format(url.target_file, url.target_segment))



class ZipUrl(FileUrl):

    match_priority = 40

    def __init__(self, url=None, downloader=None, **kwargs):
        kwargs['resource_format'] = 'zip'
        super().__init__(url, downloader=downloader, **kwargs)

    @classmethod
    def match(cls, url, **kwargs):

       return url.resource_format == 'zip' or kwargs.get('force_archive')

    def _process(self):
        super()._process()

    @property
    def target_file(self):

        if self._target_file:
            return self._target_file

        if self.fragment:
            tf, ts = self.decompose_fragment(self.fragment, self.is_archive)
            if tf:
                return tf

        for ext in ('csv', 'xls', 'xlsx'):
            if self.resource_file.endswith('.' + ext + '.zip'):
                return self.resource_file.replace('.zip', '')

        # Want to return none, so get_files_from-zip can assume to use the first file in the archive.
        return None


    def get_resource(self):
        """Get the contents of resource and save it to the cache, returning a file-like object"""

        return self

    @property
    def zip_dir(self):
        return self.path+'_d'

    def get_target(self, mode=None):
        """Get the contents of the target, and save it to the cache, returning a file-like object
        :param downloader:
        :param mode:
        """

        assert self.zip_dir

        zf = ZipFile(self.path)

        self._target_file = get_file_from_zip(self)

        target_path = join(self.zip_dir, self.target_file)
        ensure_dir(dirname(target_path))

        #if self.encoding:
        #    pass
        #    flo = io.TextIOWrapper(flo, encoding=self.encoding if self.encoding else 'utf8')


        with io.open(target_path, 'wb') as f, zf.open(self.target_file) as flo:
            copy_file_or_flo(flo, f)

        return parse_app_url(target_path,
                             fragment_query=self.fragment_query,
                             fragement=self.fragment,
                             scheme_extension=self.scheme_extension,
                             # Clear out the resource info so we don't get a ZipUrl
                             resource_file=False,
                             resource_format=False,
                             resource_url=False
                             )
