
# Copyright (c) 2017 Civic Knowledge. This file is licensed under the terms of the
# MIT, included in this distribution as LICENSE

""" """

from .file import FileUrl
from os.path import basename
from appurl.util import unparse_url_dict, file_ext

class ExcelFileUrl(FileUrl):

    @classmethod
    def match(cls, url, **kwargs):
        return url.proto == 'file' and url.target_format in ('xlsx', 'xls')

    @property
    def resource_url(self):
        from os.path import join
        return unparse_url_dict(self.dict,
                                scheme_extension=False,
                                fragment=False)

    @property
    def target_file(self):
        tf, ts = self.decompose_fragment(self.fragment, self.is_archive)
        if  ts or tf:
            return ts or tf

        return None

    @property
    def target_format(self):
        return 'xlsx'






