# Copyright (c) 2017 Civic Knowledge. This file is licensed under the terms of the
# MIT, included in this distribution as LICENSE

""" """

from .util import reparse_url, unparse_url_dict, file_ext, parse_url_to_dict
from os.path import basename, join, dirname
from pkg_resources import iter_entry_points



def match_url_classes(u_str, **kwargs):
    """
    Return the classes for which the url matches an entry_point specification, sorted by priority

    :param u_str: Url string
    :param kwargs: arguments passed to Url constructor
    :return:
    """

    u = Url(str(u_str), downloader=None, **kwargs)

    classes = sorted([ep.load() for ep in iter_entry_points(group='appurl.urls') if u.match_entry_point(ep.name)],
                     key=lambda cls: cls.match_priority)

    return classes

def parse_app_url(u_str, downloader = 'default', **kwargs):
    """
    Parse a URL string and return a constructed Url object, with the class based on the highest priority
    entry point that matches the Url and which of the entry point classes pass the match() test.

    :param u_str: Url string
    :param downloader: Downloader() to use for downloading objects.
    :param kwargs: Args passed to the Url constructor.
    :return:
    """

    if not u_str:
        return None

    if isinstance(u_str, Url):
        return u_str

    if downloader == 'default':
        from appurl import get_cache, Downloader
        downloader = Downloader(get_cache())

    classes = match_url_classes(u_str,**kwargs)

    u = Url(str(u_str), downloader=None, **kwargs)

    for cls in classes:
        if cls.match(u):
            return cls(str(u_str) if u_str else None, downloader=downloader, **kwargs)



class Url(object):
    """Base class for URL Managers

    url: The input URL
    proto: The extension of the scheme (git+http://, etc), if there is one, otherwise the scheme.

    """

    match_priority = 100

    downloader = None

    archive_formats = ['zip']

    # Basic URL components
    scheme = None
    scheme_extension = None
    netloc = None
    hostname = None
    path = None
    params = None
    query = None
    fragment = None
    fragment_query = None
    username = None
    password = None
    port = None

    # Application components
    scheme = None
    proto = None
    resource_url = None
    resource_file = None
    resource_format = None
    target_file = None
    target_format = None
    target_segment = None

    encoding = None # target encoding
    headers = None # line number of headers
    start = None # start line for data
    end = None # end line for data


    def __init__(self, url=None, downloader = None, **kwargs):

        assert 'is_archive' not in kwargs

        if url is not None:

            parts = parse_url_to_dict(url)
            parts['resource_format'] = file_ext(parts['path'])

            for k, v in parts.items():
                setattr(self, k, v)
        else:
            for k in "scheme scheme_extension netloc hostname path params query fragment fragment_query username password port".split():
                setattr(self, k, kwargs.get(k))

        self.fragment_query = kwargs.get('fragment_query', self.fragment_query or {})
        self.fragment = kwargs.get('fragment', self.fragment)
        self.scheme_extension = kwargs.get('scheme_extension', self.scheme_extension)

        self.scheme = kwargs.get('scheme', self.scheme)
        self.proto = kwargs.get('proto', self.proto)
        self.resource_url = kwargs.get('resource_url', self.resource_url)
        self.resource_file = kwargs.get('resource_file', self.resource_file)
        self.resource_format = kwargs.get('resource_format', self.fragment_query.get('resource_format',self.resource_format))
        self.target_file = kwargs.get('target_file', self.target_file)
        self.target_format = kwargs.get('target_format', self.fragment_query.get('target_format', self.target_format))
        self.target_segment = kwargs.get('target_segment', self.target_segment)

        self.encoding = kwargs.get('encoding', self.fragment_query.get('encoding',self.encoding))
        self.headers = kwargs.get('headers', self.fragment_query.get('headers',self.headers))
        self.start = kwargs.get('start', self.fragment_query.get('start',self.start))
        self.end = kwargs.get('end', self.fragment_query.get('end',self.end))

        try:
            self.target_format = self.target_format.lower()
        except AttributeError:
            pass

        self._downloader = downloader

        self._process()



    def _process(self):
        self._process_proto()
        self._process_resource_url()
        self._process_fragment()
        self._process_target_file()

    def _process_proto(self):
        """Determine the protocol, which is often just the scheme, if it is not specified.

        The protocol is the first non-empty value of, in this order:
            proto
            scheme_extension
            'http' for https scheme
            'file' for no scheme
            scheme
        """

        self.proto = self.proto or \
                     self.scheme_extension or \
                     {'https': 'http', '': 'file'}.get(self.scheme) or \
                     self.scheme

    def _process_fragement_query(self):
        """Set fragment query values"""

        # These are copied from the URl with setarrt in the constructor
        pass


    def _process_fragment(self):
        """Reassign the fragment values to one or both of the target_file and target_segment"""

        if self.fragment:
            target_file, self.target_segment = self.decompose_fragment(self.fragment, self.is_archive)
        else:
            target_file = self.target_segment = None

        if not self.target_file and target_file:
            self.target_file = target_file

    def _process_resource_url(self):
        """Set the resource_url, resource_file and resource_format"""

        self.resource_url = unparse_url_dict(self.__dict__,
                                             scheme=self.scheme if self.scheme else 'file',
                                             scheme_extension=False,
                                             fragment_query=False,
                                             fragment=False)

        self.resource_file = basename(self.path)

        if not self.resource_format:
            self.resource_format = file_ext(self.resource_file)

    def _process_target_file(self):
        """Set the target_file and target_format"""

        if not self.target_file:
            self.target_file = basename(self.path)

        if not self.target_format:
            self.target_format = file_ext(self.target_file)

        if not self.target_format:
            self.target_format = self.resource_format

    @property
    def is_archive(self):
        """Return true if this URL is for an archive. Currently only ZIP is recognized"""
        return self.resource_format in self.archive_formats

    # property
    def archive_file(self):
        """Return the name of the archive file, if there is one."""
        return self.target_file if self.is_archive and self.resource_file != self.target_file else None

    @classmethod
    def decompose_fragment(cls, frag, is_archive):

        from urllib.parse import unquote_plus

        frag_parts = unquote_plus(frag).split(';')

        file = segment = None

        # An archive file might have an inner Excel file, and that file can have
        # a segment.

        if is_archive and frag_parts:

            if len(frag_parts) == 2:
                file = frag_parts[0]
                segment = frag_parts[1]

            else:
                file = frag_parts[0]
        elif frag_parts:
            # If it isn't an archive, then the only possibility is a spreadsheet with an
            # inner segment
            segment = frag_parts[0]

        return file, segment

    def match_entry_point(self, name):
        """Return true if this URL matches the entrypoint pattern

        Entrypoint patterns:

            'scheme:' Match the URL scheme
            'proto+' Matches the protocol / scheme_extension
            '.ext' Match the resource extension
            '#.ext' Match the target extension
        """

        if '&' in name:
            return all(self.match_entry_point(n) for n in name.split('&'))

        try:
            name = name.name  # Maybe it's an entrypoint entry, not the name
        except AttributeError:
            pass

        if name == '*':
            return True
        elif name.endswith(":"):
            return name[:-1] == self.scheme
        elif name.endswith('+'):
            return name[:-1] == self.proto
        elif name.startswith('.'):
            return name[1:] == self.resource_format
        elif name.startswith('#.'):
            return name[2:] == self.target_format
        else:
            return False

    @classmethod
    def match(cls, url, **kwargs):
        """Return True if this handler can handle the input URL"""
        return True; # raise NotImplementedError("Match is not implemented for class '{}' ".format(str(cls)))


    def component_url(self, s, scheme_extension=None):
        """
        :param s:
        :param scheme_extension:
        :return:
        """

        from copy import copy

        try:
            path = s.path
            netloc = s.netloc
            u = s
        except AttributeError:
            u = parse_app_url(s)
            path = u.path
            netloc = u.netloc

        # If there is a netloc, it's an absolute URL
        if netloc:
            return u

        url = copy(self)
        url.path = join(dirname(self.path), path)

        return url

    @property
    def inner(self):
        """Return the URL whouth the scheme extension and fragment. Re-parses the URL, so it should return
        the correct class for the inner URL. """
        if not self.scheme_extension:
            return self

        return parse_app_url(str(self.clone(scheme_extension=None)))

    def abspath(self, s):
        raise NotImplementedError()

        sp = parse_url_to_dict(s)

        if sp['netloc']:
            return s

        url = reparse_url(self.url, path=join(dirname(self.parts.path), sp['path']), fragment=sp['fragment'])

        assert url
        return url

    def prefix_path(self, base):
        raise NotImplementedError()
        """Prefix the path with a base, if the path is relative"""

        url = reparse_url(self.url, path=join(base, self.parts.path))

        assert url
        return url

    def dirname(self):
        """Return the dirname of the path"""
        return dirname(self.path)

    def clear_fragment(self):
        """Return a copy of the URL with no fragment components"""

        c =  self.clone()
        c.fragment = None
        c.fragment_query = {}
        c.encoding = None
        c.start = None
        c.end = None
        c.headers = None
        return c


    def update(self, **kwargs):
        """Returns a new Url object, possibly with some of the properties replaced"""

        o = Url(
            self.rebuild_url(target_file=kwargs.get('target_file', self.target_file),
                             target_segment=kwargs.get('target_segment', self.target_segment)),
            scheme=kwargs.get('scheme', self.scheme),
            proto=kwargs.get('proto', self.proto),
            resource_url=kwargs.get('resource_url', self.resource_url),
            resource_file=kwargs.get('resource_file', self.resource_file),
            resource_format=kwargs.get('resource_format', self.resource_format),
            target_file=kwargs.get('target_file', self.target_file),
            target_format=kwargs.get('target_format', self.target_format),
            encoding=kwargs.get('encoding', self.encoding),
            target_segment=kwargs.get('target_segment', self.target_segment)
        )

        o._process_resource_url()
        o._process_fragment()
        o._process_target_file()

        return o

    def rebuild_url(self, target_file=None, target_segment=None, **kw):

        url = self.__deepcopy__(self)

        if target_file:
            url.target_file = target_file
        elif target_file is False:
            url.target_file = None
        else:
            # What's this for?
            self.target_file = self.archive_file()

        if target_segment is False:
            self.target_segment = None
        elif target_segment or target_segment == 0:
            self.target_segment = target_segment

    def rebuild_fragment(self):

        second_sep = ''
        frag = ''

        if self.target_file:
            frag = self.target_file
            second_sep = ';'

        if self.target_segment or self.target_segment == 0:
            frag += second_sep
            frag += str(self.target_segment)

        self.fragment = frag

    @property
    def dict(self):
        self._update_parts()
        keys = "url scheme scheme_extension netloc hostname path params query fragment fragment_query username password port " \
               "proto resource_url resource_file resource_format target_file target_format " \
               "encoding target_segment"

        return dict((k, v) for k, v in self.__dict__.items() if k in keys)

    def _update_parts(self):
        """Update the fragement_query. Set the attribute for the query value to False to delete it from
        the fragment query"""

        for k in "encoding headers start end".split():
            if getattr(self, k):
                self.fragment_query[k] = getattr(self, k)
            elif getattr(self, k) == False and k in self.fragment_query:
                del self.fragment_query[k]

        #if self.fragment:
        #    self.rebuild_fragment()



    def get_resource(self):
        """Get the contents of resource and save it to the cache, returning a file-like object"""
        raise NotImplementedError("get_resource not implemented in "+self.__class__.__name__)

    def get_target(self, mode=None):
        """Get the contents of the target, and save it to the cache, returning a file-like object
        :param mode:
        """
        raise NotImplementedError("get_target not implemented in "+self.__class__.__name__)

    def __deepcopy__(self, memo):
        d = self.__dict__.copy()
        return type(self)(None, downloader=self._downloader, **d)

    def __copy__(self):
        d = self.__dict__.copy()
        return type(self)(None, downloader=self._downloader, **d,)

    def clone(self, **kwargs):
        from copy import copy

        d = self.__dict__.copy()
        c = type(self)(None, downloader=self._downloader, **d)

        c._update_parts()

        for k, v in kwargs.items():
            setattr(c, k, v )

        return c


    def __repr__(self):
        return "<{} {}>".format(self.__class__.__name__, str(self))

    def __str__(self):
        self._update_parts()
        return unparse_url_dict(self.__dict__)

