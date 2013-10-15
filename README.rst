Recursive Deep Archive Iterator
===============================

A Python module to print text files from deeply nested compressed archives
recursively.

Useful for grep.

Requires Python 3.3 or greater.

Example::

    python3 rdai.py myfile.zip

Example with GNU parallel and grep::

    find -iname "*.zip" | parallel python3 rdai.py "{}" | grep hello

Use the ``--json`` option to parse JSON dumps such as the Archive Team Twitter
Stream scrapes: https://archive.org/details/twitterstream ::

    find -iname "*.zip" | parallel --ungroup --eta python3 rdai.py --json "{}" | grep -o -P "bit\.ly/[a-zA-Z0-9]+" > urls.txt


Bugs
++++

* Does not handle infinite recursion.
* No setup.py
* No PyPi package.
* No unit tests.
* Detects compressed files only by filename.
