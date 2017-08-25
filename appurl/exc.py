# Copyright (c) 2017 Civic Knowledge. This file is licensed under the terms of the
# MIT, included in this distribution as LICENSE

""" """

class AppUrlError(Exception):
    pass

class DownloadError(AppUrlError):
    pass

class AccessError(DownloadError):
    """Got an acess error on download"""
    pass

class SourceError(AppUrlError):
    """Got an acess error on download"""
    pass