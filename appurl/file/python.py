# Copyright (c) 2017 Civic Knowledge. This file is licensed under the terms of the
# MIT, included in this distribution as LICENSE

"""
URLS for referencing python code.
"""

from appurl.file import FileUrl


class PythonUrl(FileUrl):
    """
    URL to reference python code
    """

    def __init__(self, url=None, downloader=None, **kwargs):

        super().__init__(url, downloader, **kwargs)
        kwargs['scheme'] = 'python'

    @classmethod
    def match(cls, url, **kwargs):
        return url.proto == 'python'

    def get_resource(self):
        return self

    def get_target(self, mode=None):
        return self

    @property
    def object(self):

        components = self.path.replace('/','.').split('.') + [self.target_file]

        mod = __import__(components[0])
        for comp in components[1:]:
            mod = getattr(mod, comp)

        return mod

    def __call__(self, *args, **kwargs):

        return self.object(*args, **kwargs)



