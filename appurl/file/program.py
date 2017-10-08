# Copyright (c) 2017 Civic Knowledge. This file is licensed under the terms of the
# MIT, included in this distribution as LICENSE

""" """

from appurl.file import FileUrl

class ProgramUrl(FileUrl):
    """URL that references an executable file"""

    def __init__(self, url=None, downloader=None, **kwargs):
        super().__init__(url, downloader, **kwargs)
        kwargs['proto'] = 'program'

    @classmethod
    def _match(cls, url, **kwargs):
        return url.proto == 'program'

    def get_resource(self):
        return super().get_resource()

    def get_target(self, mode=None):
        return super().get_target(mode)





