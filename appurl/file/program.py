# Copyright (c) 2017 Civic Knowledge. This file is licensed under the terms of the
# MIT, included in this distribution as LICENSE

""" """

from appurl.url import Url

class ProgramUrl(Url):
    def __init__(self, url, downloader=None, **kwargs):
        kwargs['proto'] = 'program'

        super(ProgramUrl, self).__init__(url, downloader=downloader,**kwargs)

    @classmethod
    def match(cls, url, **kwargs):
        return extract_proto(url) == 'program'

    def _extract_parts(self, url, kwargs):
        parts = self.url_parts(url, **kwargs)

        self.url = reparse_url(url, assume_localhost=True,
                               scheme=parts.scheme if parts.scheme != 'program' else 'file',
                               scheme_extension='program')

        self.parts = self.url_parts(self.url, **kwargs)

    @property
    def path(self):
        return self.parts.path

    def _process_resource_url(self):
        self.resource_url = unparse_url_dict(self.parts.__dict__,
                                             scheme=self.parts.scheme if self.parts.scheme else 'file',
                                             scheme_extension=False,
                                             fragment=False)

        self.resource_file = basename(self.resource_url)

        if not self.resource_format:
            self.resource_format = file_ext(self.resource_file)

