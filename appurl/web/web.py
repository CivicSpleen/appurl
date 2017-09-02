# Copyright (c) 2017 Civic Knowledge. This file is licensed under the terms of the
# MIT, included in this distribution as LICENSE

"""Base class for Web URLs. These are URLs that can be fetched to the local filesystem. """

from appurl.url import Url
from appurl.util import parse_url_to_dict

class WebUrl(Url):

    match_priority = 20

    def __init__(self, url=None, downloader=None, **kwargs):
        super().__init__(url,downloader=downloader, **kwargs)

        self._resource = None # return value from the downloader

    @classmethod
    def match(cls, url, **kwargs):
        """Return True if this handler can handle the input URL"""
        return url.scheme.startswith('http')

    @property
    def auth_resource_url(self):
        """Return An S3: version of the url, with a resource_url format that will trigger boto auth"""

        # This is just assuming that the url was created as a resource from the S2Url, and
        # has the form 'https://s3.amazonaws.com/{bucket}/{key}'

        parts = parse_url_to_dict(self.resource_url)

        return 's3://{}'.format(parts['path'])

    def get_resource(self):
        """Get the contents of resource and save it to the cache, returning a file-like object"""


        from appurl import parse_app_url

        self._resource = self._downloader.download(self.inner)

        ru = parse_app_url(self._resource.sys_path,
                           fragment=self.fragment,
                           fragment_query=self.fragment_query,
                           scheme_extension=self.scheme_extension
                           )


        return ru

    def component_url(self, s, scheme_extension=None):


        if self.resource_format in ('zip','xlsx'):
            u = Url(s)
            return self.clone(fragment=u.path)
        else:
            return super().component_url(s, scheme_extension)






