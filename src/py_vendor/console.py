from __future__ import annotations

import logging
import pathlib
import shutil

import click
import yaml

import py_vendor
from py_vendor.run import do_vendor

logger = logging.getLogger(__name__)


@click.group()
def main():
    logging.basicConfig(level=logging.INFO)


@main.command()
def version():
    click.secho("Version", fg="blue", nl=False)
    click.echo(": ", nl=False)
    click.secho(py_vendor.__version__, fg="green")


@main.command()
@click.option("-c", "--config", help="The path of the config file.")
@click.option("-n", "--name", default=None, help="The name of the vendor to pull")
@click.option("-f", "--force", is_flag=True)
def run(config: str, name: str | None, force: bool):
    with open(config) as fh:
        config = yaml.safe_load(fh.read())

    vendor_dir = config["params"]["vendor_dir"]
    logger.info(f"target dir: %s", vendor_dir)
    for vendor_name, cfg in config["vendors"].items():
        if name is not None and vendor_name != name:
            continue
        url = cfg.get("url")
        ref = cfg.get("ref")
        logger.info("vendoring %s %s @ %s", vendor_name, url, ref)
        target = pathlib.Path(vendor_dir, vendor_name)
        if target.exists():
            if force:
                shutil.rmtree(target)
            else:
                raise RuntimeError(
                    f'Target directory "{target.resolve().as_uri()}" not empty. '
                    "Use -f to remove it."
                 )
        do_vendor(url, target, ref, cfg.get("files"))
