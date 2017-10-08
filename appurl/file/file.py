# Copyright (c) 2017 Civic Knowledge. This file is licensed under the terms of the
# MIT, included in this distribution as LICENSE

"""Base class for file URLs, URLs on a local file system. These are URLs that can be opened and read"""

from appurl.url import Url
from appurl.util import ensure_dir
from os.path import exists, isdir, dirname


class FileUrl(Url):
    """FileUrl is the baseclass for URLs that reference a general file, assumed to be
    local to the file system.

    This documentation only describes the differences in implementation from the super class.
    See the documentation for the superclass, :py:class:`appurl.Url` for the default implementations.

    """

    def __init__(self, url=None, downloader=None,**kwargs):
        """
        """
        super().__init__(url, downloader=downloader, **kwargs)

    match_priority = 50

    def exists(self):
        return exists(self.path)

    def isdir(self):
        return isdir(self.path)

    def dirname(self):
        return dirname(self.path)

    def ensure_dir(self):
        ensure_dir(self.path)

    def list(self):
        """This function does something.

        :param name: The name to use.
        :type name: str.
        :param state: Current state to be in.
        :type state: bool.
        :returns:  int -- the return code.
        :raises: AttributeError, KeyError

        """

        if self.isdir():
            from os import listdir

            return [u for e in listdir(self.path) for u in self.join(e).list()]

        else:
            return [self]

    def get_resource(self):
        """Return a url to the resource, which for FileUrls is always ``self``."""

        return self

    def get_target(self):
        """Return the url of the target file in the local file system.
        """

        return self.clear_fragment()


    def read(self, mode='rb'):
        """Return contents of the target file"""
        with open(self.get_target().path, mode=mode) as f:
            return f.read()

    def join_target(self, tf):
        """For normal files, joining a target assumes the target is a child of the current target's
        directory, so this just passes through the :py:meth:`Url.join_dir`"""

        try:
            tf = tf.path
        except:
            pass

        return self.clone().join_dir(tf)


