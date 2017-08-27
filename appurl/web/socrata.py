# Copyright (c) 2017 Civic Knowledge. This file is licensed under the terms of the
# MIT, included in this distribution as LICENSE

""" """
from appurl.util import parse_url_to_dict, unparse_url_dict, file_ext
from os.path import basename, join
from appurl.web import WebUrl

class SocrataUrl(WebUrl):


    def __init__(self, url=None,downloader=None, **kwargs):

        kwargs['resource_format'] = 'csv'
        kwargs['encoding'] = 'utf8'
        kwargs['proto'] = 'socrata'

        super().__init__(url,downloader=downloader, **kwargs)



    @classmethod
    def match(cls, url, **kwargs):
        return url.proto == 'socrata'

    def _process_resource_url(self):
        self.resource_url = unparse_url_dict(self.__dict__,
                                             scheme_extension=False,
                                             fragment=False,
                                             path=join(self.path, 'rows.csv'))

        self.resource_file = basename(self.path)+'.csv'

        if self.resource_format is None:
            self.resource_format = file_ext(self.resource_file)

        self.target_file = self.resource_file  # _process_target() file will use this self.target_file

    def get_resource(self, downloader=None):
        """Get the contents of resource and save it to the cache, returning a file-like object"""
        raise NotImplementedError()

    def get_target(self, mode=None):
        """Get the contents of the target, and save it to the cache, returning a file-like object
        :param downloader:
        :param mode:
        """
        raise NotImplementedError()
