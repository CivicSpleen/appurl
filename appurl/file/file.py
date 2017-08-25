# Copyright (c) 2017 Civic Knowledge. This file is licensed under the terms of the
# MIT, included in this distribution as LICENSE

"""Base class for file URLs, URLs on a local file system. These are URLs that can be opened and read"""

from appurl.url import Url

class FileUrl(Url):
    def __init__(self, url=None, **kwargs):
        super().__init__(url, **kwargs)

