# Copyright (c) 2017 Civic Knowledge. This file is licensed under the terms of the
# MIT, included in this distribution as LICENSE

""" """

from appurl.web import WebUrl
from os.path import basename
from appurl.util import file_ext

class S3Url(WebUrl):
    """Convert an S3 proto url into the public access form"""

    def __init__(self, url=None, downloader=None, **kwargs):
        # Save for auth_url()
        self._orig_url = url
        self._orig_kwargs = dict(kwargs.items())

        kwargs['proto'] = 's3'
        super().__init__(url,downloader=downloader, **kwargs)


    @classmethod
    def match(cls, url, **kwargs):
        return url.proto == 's3';

    def _process_resource_url(self):

        url_template = 'https://s3.amazonaws.com/{bucket}/{key}'

        self._bucket_name = self.netloc
        self._key = '' if not self.path else self.path.strip('/')

        # noinspection PyUnresolvedReferences
        self.resource_url = url_template.format(bucket=self._bucket_name, key=self._key)

        self.resource_file = basename(self.resource_url)

        if self.resource_format is None:
            self.resource_format = file_ext(self.resource_file)

    @property
    def auth_resource_url(self):
        """Return the orginal S3: version of the url, with a resource_url format that will trigger boto auth"""
        return 's3://{bucket}/{key}'.format(bucket=self._bucket_name, key=self._key)

    def component_url(self, s, scheme_extension=None):
        sp = parse_url_to_dict(s)

        new_key = join(dirname(self.key), sp['path'])

        return 's3://{bucket}/{key}'.format(bucket=self._bucket_name.strip('/'), key=new_key.lstrip('/'))

    @property
    def bucket_name(self):
        return self._bucket_name

    @property
    def key(self):
        return self._key

    @property
    def object(self):
        """Return the boto object for this source"""
        import boto3

        s3 = boto3.resource('s3')

        return s3.Object(self.bucket_name, self.key)

    @property
    def signed_resource_url(self):
        import boto3

        s3 = boto3.client('s3')

        url = s3.generate_presigned_url(
            ClientMethod='get_object',
            Params={
                'Bucket': self.bucket_name,
                'Key': self.key
            }
        )

        return url

