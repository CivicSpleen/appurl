Application Urls
****************

.. image:: https://travis-ci.org/Metatab/appurl.svg?branch=master
    :target: https://travis-ci.org/Metatab/appurl

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

    $ pip install appurl

Documentation
=============

See the documentation at http://appurl.readthedocs.io/

Development Notes
=================

Running tests
+++++++++++++

Run ``python setup.py tests`` to run normal development tests. You can also run ``tox``, which will
try to run the tests with python 3.4, 3.5 and 3.6, ignoring non-existent interpreters.


Development Testing with Docker
+++++++++++++++++++++++++++++++

Testing during development for other versions of Python is a bit of a pain, since you have
to install the alternate version, and Tox will run all of the tests, not just the one you want.

One way to deal with this is to install Docker locally, then run the docker test container
on the source directory. This is done automatically from the Makefile in appurl/tests


.. code-block:: bash

    $ cd appurl/test
    $ make build # to create the container image
    $ make shell # to run bash the container

You now have a docker container where the /code directory is the appurl source dir.

Now, run tox to build the tox virtual environments, then enter the specific version you want to
run tests for and activate the virtual environment.

.. code-block:: bash

    # tox
    # cd .tox/py34
    # source bin/activate # Activate the python 3.4 virtual env
    # cd ../../
    # python setup.py test # Cause test deps to get installed
    #
    # python -munittest appurl.test.test_basic.BasicTests.test_url_classes  # Run one test




