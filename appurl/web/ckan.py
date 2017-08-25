# Copyright (c) 2017 Civic Knowledge. This file is licensed under the terms of the
# MIT, included in this distribution as LICENSE

""" """

class CkanUrl(Url):
    def __init__(self, url, **kwargs):
        kwargs['proto'] = 'ckan'
        super(CkanUrl, self).__init__(url, **kwargs)

    @classmethod
    def match(cls, url, **kwargs):
        return extract_proto(url) == 'ckan'


