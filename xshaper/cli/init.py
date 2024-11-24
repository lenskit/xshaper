import logging
from pathlib import Path

import click

from . import xshaper

_log = logging.getLogger(__name__)


@xshaper.command()
@click.argument("log_dir", type=click.Path(file_okay=False, dir_okay=True, path_type=Path))
def init(log_dir: Path):
    "Initialize a shaperate log directory."

    if not log_dir.exists():
        _log.info("creating log dir %s", log_dir)
        log_dir.mkdir(exist_ok=True, parents=True)

    ignore = log_dir / ".gitignore"
    if ignore.exists():
        _log.warning("%s already exists, not updating", ignore)
    else:
        _log.info("writing %s", ignore)
        with ignore.open("w") as ignf:
            print("# lobby holds the in-progress run files", file=ignf)
            print("/lobby/", file=ignf)
            print("# dvc will add its ignores below here", file=ignf)

    (log_dir / "lobby").mkdir(exist_ok=True)
