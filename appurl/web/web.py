# Copyright (c) 2017 Civic Knowledge. This file is licensed under the terms of the
# MIT, included in this distribution as LICENSE

"""Base class for Web URLs. These are URLs that can be fetched to the local filesystem. """

from appurl.url import Url
from appurl.util import parse_url_to_dict

class WebUrl(Url):

    match_priority = 10

    def __init__(self, url=None, **kwargs):
        super().__init__(url, **kwargs)

    @classmethod
    def match(cls, url, **kwargs):
        """Return True if this handler can handle the input URL"""
        return url.proto == 'http'

    @property
    def auth_resource_url(self):
        """Return An S3: version of the url, with a resource_url format that will trigger boto auth"""

        # This is just assuming that the url was created as a resource from the S2Url, and
        # has the form 'https://s3.amazonaws.com/{bucket}/{key}'

        parts = parse_url_to_dict(self.resource_url)

        return 's3://{}'.format(parts['path'])


    def download(self, downloader):

        return downloader.download(Url(self.resource_url))


