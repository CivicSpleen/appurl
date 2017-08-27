# Application Urls

This library defines a structure for URLs to specify how to access file, particularly row-oriented data, that may be contained in archives or spredsheets, and may be stored on remote servers that expect particular ways of accessing files, or require credentials. The URL structure is designed to full-specify how to access data that is:

    * Stored on the web: http://examples.com/file.csv
    * Inside a zip file on the web: http://example.com/archive.zip#file.csv
    * A worksheet in an Excel file: http://example.com/excel.xls#worksheet
    * A worksheet in an Ecel file in a ZIP Archive: http://example.com/archive.zip#excel.xls;worksheet
    * An API: socrata+http://chhs.data.ca.gov/api/views/tthg-z4mf

These AppUrls have these components in addition to standard URLS:

    * A scheme extension, which preceedes the scheme with a '+'
    * A target_file, the first part of the URL fragment
    * A target_segment, the second part of a URL fragement, delineated by a ';'


The ``scheme_extension`` specifies the protocol to use with a sthadard web scheme, inspired by github URLs like ``git+http://github.com/example``. The ``target_file`` is usually the file within an archive. It is interpreted as a regular expression. The ``target_segment`` may be either a name or a number, and is usually interpreted as the name or number of a worksheet in a spreadsheet file. Combining these extensions: 

```
    ckan+http://example.com/dataset/archive.zip#excel.xlsx;worksheet
```

This url may indicate that to fetch a ZIP file from an CKAN server, using the CKAN protocol, extract the ``excel.xls`` file from the ZIP archive, and open the ``worksheet`` worksheet. 

The URLs define a few important concepts: 

* resource_url: the portion of the URl that defines only the resource to be access or downloaded. In the eample above, the resource url is 'http://example.com/dataset/archive.zip'
* resource_file: The basename of the resource URL: `archive.zip'
* resource_format: Usually, the extension of the resource_file: 'zip'
* target_file: The name of the target_file: 'excel.xlsx'
* target_format: The extension of the target_file: 'xlsx'

# Using AppUrls

The primary interface is ``appurls.parse_url``, which will and construct a ``appurl.url.Url`` for a string. The function will select a Url class using two selection criteria. The first is the ``appurl.urls`` entry point. Here is the entrypoint configuration for the ``appurl`` package: 

```
        entry_points = {
        'appurl.urls' : [
            "* = appurl.url:Url",

            #
            "http: = appurl.web.web:WebUrl",
            "https: = appurl.web.web:WebUrl",
            "s3: = appurl.web.s3:S3Url",
            "socrata+ = appurl.web.socrata:SocrataUrl",
            #
            # Archive Urls
            ".zip = appurl.archive.zip:ZipUrl",
            #
            # File Urls
            ".csv = appurl.file.csv:CsvFileUrl",
            "file: = appurl.file.file:FileUrl",
        ]
    }
    
 ```
 
The key of each configuration like is a string the indicate the first round of matching, and the value is the class to use for that matcher. The match strings are: 

* 'proto:' The URL protocol, which is based on either the URL scheme or scheme extension. 
* '.format' The target file format
* 'schemeext+' The URL scheme extension. 
* '*' Any URL. 

Because these configurations are in the entry pointy, you can extend the AppUrls by including these entry points in Python packages. 

The ``appurls.parse_url`` collects all of the URL classes that pass the initial matchers and sorts them by the ``Url.match_priority`` class property. Then, it iterates through the matched classes in priority order, calling the ``Url.match`` method. The function contructs and returns the first match. 
