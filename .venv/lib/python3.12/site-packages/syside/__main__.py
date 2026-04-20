"""
Entrypoint of Syside Pro Python CLI
"""

import logging

from .cli import cli

if __name__ == "__main__":
    logging.basicConfig(format="%(message)s", level=logging.WARNING)
    cli()  # pylint:disable=no-value-for-parameter
