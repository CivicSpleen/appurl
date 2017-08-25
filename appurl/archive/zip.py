# Copyright (c) 2017 Civic Knowledge. This file is licensed under the terms of the
# MIT, included in this distribution as LICENSE

""" """


from appurl.url import Url
from appurl.util import file_ext

class ZipUrl(Url):

    match_priority = 50

    def __init__(self, url=None, **kwargs):
        kwargs['resource_format'] = 'zip'
        super().__init__(url, **kwargs)

    @classmethod
    def match(cls, url, **kwargs):

       return url.resource_format == 'zip' or kwargs.get('force_archive')

    def _process_fragment(self):

        if self.fragment:
            self.target_file, self.target_segment = self.decompose_fragment(self.fragment, self.is_archive)

        else:
            self.target_file = self.target_segment = None

    def _process_target_file(self):

        # Handles the case of file.csv.zip, etc.
        for ext in ('csv', 'xls', 'xlsx'):
            if self.resource_file.endswith('.' + ext + '.zip'):
                self.target_file = self.resource_file.replace('.zip', '')

        if self.target_file and not self.target_format:
            self.target_format = file_ext(self.target_file)



