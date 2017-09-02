
# Copyright (c) 2017 Civic Knowledge. This file is licensed under the terms of the
# MIT, included in this distribution as LICENSE

""" """

from .file import FileUrl
from os.path import basename
from appurl.util import unparse_url_dict, file_ext

class ExcelFileUrl(FileUrl):

    @classmethod
    def match(cls, url, **kwargs):
        return url.proto == 'file' and url.target_format == 'xlsx'


    def _process_resource_url(self):

        self.resource_url = unparse_url_dict(self.__dict__,
                                             scheme=self.scheme if self.scheme else 'file',
                                             scheme_extension=False,
                                             fragment=False)

        self.resource_file = basename(self.resource_url)

        if not self.resource_format:
            self.resource_format = file_ext(self.resource_file)


