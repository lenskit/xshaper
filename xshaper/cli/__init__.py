import logging
import sys

import click

_log = logging.getLogger(__name__)


@click.group()
@click.option("-v", "--verbose", is_flag=True)
def xshaper(verbose: bool):
    "eXperiment Shaperate command-line tool."
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, stream=sys.stderr)
    _log.debug("starting xshaper cli")


# import the subpackages to record their commands
from . import init  # type: ignore # noqa: E402, F401
