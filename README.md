# book-grab

OpenSpending book projects are hosted as Markdown documents (with a tiny bit of special formatting) on Google Docs. This script grabs such a document, processes it, and splits it up into separate files. The result is ready to be published in various formats using [easybook](http://easybook-project.org) (or any other Markdown-driven publishing system).

This script requires [gdata](https://pypi.python.org/pypi/gdata), so make sure to install that first:

    pip install gdata

To use this script, first rename `config.ini.template` to `config.ini` and enter your Google account credentials and the ID of your doc (the long, distinctive alphanumeric string in your doc's URL). Then simply run the script like so:

    python grab.py

The script will put the files it extracts from your doc in */Contents*, and it will put local copies of the doc's images in */Contents/images*.
