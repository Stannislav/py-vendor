from __future__ import annotations

import logging
import pathlib
import shutil

import click
import yaml

import py_vendor
from py_vendor.run import do_vendor
from py_vendor import shell

logger = logging.getLogger(__name__)


@click.group()
@click.option(
    "-v",
    "--verbose",
    count=True,
    help="The logging verbosity: 0=WARNING (default), 1=INFO, 2=DEBUG",
)
def main(verbose):
    if verbose >= 2:
        logging.basicConfig(level=logging.DEBUG)
    elif verbose == 1:
        logging.basicConfig(level=logging.INFO)
    else:
        logging.basicConfig(level=logging.WARNING)


@main.command()
def version():
    shell.echo_pair("Version", py_vendor.__version__)


@main.command()
@click.option(
    "-c",
    "--config",
    "config_path",
    help="The path of the config file.",
)
@click.option(
    "-n",
    "--name",
    default=None,
    help="The name of the vendor to pull",
)
@click.option("-f", "--force", is_flag=True)
def run(config_path: str, name: str | None, force: bool):
    with open(config_path) as fh:
        config_path = yaml.safe_load(fh.read())

    vendor_dir = config_path["params"]["vendor_dir"]
    shell.echo_pair("Target dir", vendor_dir)
    for vendor_name, cfg in config_path["vendors"].items():
        if name is not None and vendor_name != name:
            continue
        url = cfg.get("url")
        ref = cfg.get("ref")
        shell.echo_pair("Vendoring", f"{vendor_name} {url} @ {ref}")
        target = pathlib.Path(vendor_dir, vendor_name)
        if target.exists():
            if force:
                shell.echo_warning(
                    f"Removing the directory {target.resolve().as_uri()} "
                    f"(--force option present)"
                )
                shutil.rmtree(target)
            else:
                shell.echo_error(
                    f"Target directory {target.resolve().as_uri()} not empty. "
                    "Use the --force option to force overwriting."
                )
                continue
        do_vendor(url, target, ref, cfg.get("copy"))

        # Touch
        for filename in cfg.get("touch", []):
            path = target / filename
            logger.info("touching %s", path)
            path.parent.mkdir(exist_ok=True, parents=True)
            path.touch()

    shell.echo("Done.")
