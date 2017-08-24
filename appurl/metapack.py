# Copyright (c) 2017 Civic Knowledge. This file is licensed under the terms of the
# MIT, included in this distribution as LICENSE

""" """

class MetatabPackageUrl(Url):
    """"""

    def __init__(self, url, **kwargs):
        kwargs['proto'] = 'metatab'
        super(MetatabPackageUrl, self).__init__(url, **kwargs)

    @classmethod
    def match(cls, url, **kwargs):
        return extract_proto(url) == 'metatab'

    def _process_resource_url(self):

        # Reminder: this is the HTTP resource, not the Metatab resource
        self.resource_url = unparse_url_dict(self.parts.__dict__, scheme_extension=False, fragment=False)

        self.resource_format = file_ext(self.resource_url)

        if self.resource_format not in ('zip', 'xlsx', 'csv'):
            self.resource_format = 'csv'
            self.resource_file = 'metadata.csv'
            self.resource_url += '/metadata.csv'
        else:
            self.resource_file = basename(self.resource_url)

        if self.resource_format == 'xlsx':
            self.target_file = 'meta'
        elif self.resource_format == 'zip':
            self.target_file = 'metadata.csv'
        else:
            self.target_file = self.resource_file

        self.target_format = 'metatab'

    def component_url(self, s, scheme_extension=None):
        return super().component_url(s, scheme_extension)

    def _process_fragment(self):
        self.target_segment = self.parts.fragment

