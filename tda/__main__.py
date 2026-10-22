import sys

if sys.version_info < (3, 12):
    sys.exit("This tool needs Python 3.12 or newer, and this is Python "
             f"{sys.version_info.major}.{sys.version_info.minor}. "
             "Install the latest Python from https://www.python.org/downloads/ and try again.")

from tda.cli import main  # noqa: E402

sys.exit(main())
