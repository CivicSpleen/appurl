# Copyright (c) 2017 Civic Knowledge. This file is licensed under the terms of the
# MIT, included in this distribution as LICENSE

""" """


class ZipUrl(Url):
    def __init__(self, url, **kwargs):
        kwargs['resource_format'] = 'zip'
        super(ZipUrl, self).__init__(url, **kwargs)

    @classmethod
    def match(cls, url, **kwargs):
        parts = parse_url_to_dict(url)
        return file_ext(parts['path']) in ('zip',) or kwargs.get('force_archive')

    def _process_fragment(self):

        if self.parts.fragment:
            self.target_file, self.target_segment = self.decompose_fragment(self.parts.fragment, self.is_archive)

        else:
            self.target_file = self.target_segment = None

    def _process_target_file(self):

        # Handles the case of file.csv.zip, etc.
        for ext in ('csv', 'xls', 'xlsx'):
            if self.resource_file.endswith('.' + ext + '.zip'):
                self.target_file = self.resource_file.replace('.zip', '')

        if self.target_file and not self.target_format:
            self.target_format = file_ext(self.target_file)

    def component_url(self, s):

        if url_is_absolute(s):
            return s

        return reparse_url(self.url, fragment=s)

