# Copyright (c) 2017 Civic Knowledge. This file is licensed under the terms of the
# MIT, included in this distribution as LICENSE

""" """



url_handlers = [
    NotebootUrl,
    ProgramUrl,
    MetatabPackageUrl,
    CkanUrl,
    SocrataUrl,
    GoogleProtoCsvUrl,
    ZipUrl,
    ExcelUrl,
    S3Url,
    ApplicationUrl,
    GeneralUrl
]


def get_handler(url, **kwargs):
    for handler in url_handlers:
        if handler.match(url, **kwargs):
            return handler

    return GeneralUrl