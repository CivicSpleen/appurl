
# Copyright (c) 2017 Civic Knowledge. This file is licensed under the terms of the
# MIT, included in this distribution as LICENSE

""" """

from .file import FileUrl
from os.path import basename
from appurl.util import unparse_url_dict, file_ext

class ExcelFileUrl(FileUrl):

    @classmethod
    def match(cls, url, **kwargs):
        return url.proto == 'file' and url.resource_format in ('xlsx', 'xls')

    @property
    def resource_url(self):
        from os.path import join
        return unparse_url_dict(self.dict,
                                scheme_extension=False,
                                fragment=False)

    @property
    def target_file(self):
        return self.fragment[0]

    @property
    def target_segment(self):
        return self.fragment[0]

    @property
    def target_format(self):
        return 'xlsx'

    def join(self, s, scheme_extension=None):
        return super().join(s, scheme_extension)

    def join_dir(self, s, scheme_extension=None):
        return super().join_dir(s, scheme_extension)

    def join_target(self, tf):

        try:
            tf = tf.path
        except:
            pass

        u = self.clone()
        u.fragment = [tf,None] # In case its a tuple, don't edit in place
        return u

    def get_target(self, mode=None):
        return self # Like super method, but don't clear the fragment; it's needed in the row generator








