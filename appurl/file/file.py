# Copyright (c) 2017 Civic Knowledge. This file is licensed under the terms of the
# MIT, included in this distribution as LICENSE

"""Base class for file URLs, URLs on a local file system. These are URLs that can be opened and read"""

from appurl.url import Url
from os.path import exists

class FileUrl(Url):
    def __init__(self, url=None, downloader=None,**kwargs):
        super().__init__(url, downloader=downloader, **kwargs)

    match_priority = 50

    def exists(self):
        return exists(self.path)

    def get_resource(self):
        """Get the contents of resource and save it to the cache, returning a file-like object"""

        return self

    def get_target(self, mode=None):
        """Get the contents of the target, and save it to the cache, returning a file-like object
        :param downloader:
        :param mode:
        """

        return self.clear_fragment()


    def read(self, mode='rb'):
        """Return contents of file"""
        with open(self.path, mode=mode) as f:
            return f.read()