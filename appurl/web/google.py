# Copyright (c) 2017 Civic Knowledge. This file is licensed under the terms of the
# MIT, included in this distribution as LICENSE

""" """


class GoogleProtoCsvUrl(Url):
    """Access a Google spreadheet as a CSV format download"""

    csv_url_template = 'https://docs.google.com/spreadsheets/d/{key}/export?format=csv'

    def __init__(self, url, **kwargs):
        kwargs['resource_format'] = 'csv'
        kwargs['encoding'] = 'utf8'
        kwargs['proto'] = 'gs'
        super(GoogleProtoCsvUrl, self).__init__(url, **kwargs)

    @classmethod
    def match(cls, url, **kwargs):
        return extract_proto(url) == 'gs'

    def _process_resource_url(self):

        self._process_fragment()

        # noinspection PyUnresolvedReferences
        self.resource_url = self.csv_url_template.format(
            key=self.parts.netloc)  # netloc is case-sensitive, hostname is forced lower.

        self.resource_file = self.parts.netloc

        if self.target_segment:
            self.resource_url += "&gid={}".format(self.target_segment)
            self.resource_file += '-' + self.target_segment

        self.resource_file += '.csv'

        if self.resource_format is None:
            self.resource_format = file_ext(self.resource_file)

        self.target_file = self.resource_file  # _process_target() file will use this self.target_file

    def component_url(self, s):

        sp = parse_url_to_dict(s)

        if sp['netloc']:
            return s

        return reparse_url(self.url, fragment=s)

        url = reparse_url(self.resource_url, query="format=csv&gid=" + s)
        assert url
        return url

