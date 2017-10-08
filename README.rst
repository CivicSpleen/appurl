Application Urls
****************

Application Urls provide structure and operations on URLS where the file the
URL refers to can't, in general, simply be downloaded. For instance, you may
want to refer to a CSV file inside a ZIP archive, or a worksheet in an Excel
file. In conjunction with `Row Generators
<https://github.com/CivicKnowledge/rowgenerators>`_, Application Urls are often
used to refer to tabular data stored on data repositories. For instance:

-  Stored on the web: ``http://examples.com/file.csv``
-  Inside a zip file on the web: ``http://example.com/archive.zip#file.csv``
-  A worksheet in an Excel file: ``http://example.com/excel.xls#worksheet``
-  A worksheet in an Excel file in a ZIP Archive:
   ``http://example.com/archive.zip#excel.xls;worksheet``
-  An API: ``socrata+http://chhs.data.ca.gov/api/views/tthg-z4mf``


Install
=======

.. code-block:: bash

    $ pip isntall appurl

Documentation
=============

See the documentation in the `/docs directory of this repo <http://civicknowledge.org/appurl/>`_

