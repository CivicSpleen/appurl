# Copyright (c) 2017 Civic Knowledge. This file is licensed under the terms of the
# MIT, included in this distribution as LICENSE

""" """


class WebPageUrl(Url):
    """A URL for webpages, not for data"""

    def __init__(self, url, **kwargs):
        super(GeneralUrl, self).__init__(url, **kwargs)

    @classmethod
    def match(cls, url, **kwargs):
        return True

    def component_url(self, s):
        sp = parse_url_to_dict(s)

        if sp['netloc']:
            return s

        return reparse_url(self.url, path=join(dirname(self.parts.path), sp['path']))

