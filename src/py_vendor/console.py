from __future__ import annotations

import logging
import pathlib
import shutil
import tempfile

import click
import yaml

import py_vendor
from py_vendor import shell
from py_vendor.run import clone_repo, copy, create, modify

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

    vendor_dir = pathlib.Path(config_path["params"]["vendor_dir"])
    vendor_dir.mkdir(exist_ok=True, parents=True)
    shell.echo_pair("Target dir", vendor_dir)
    for vendor_name, cfg in config_path["vendors"].items():
        if name is not None and vendor_name != name:
            continue
        url = cfg.get("url")
        ref = cfg.get("ref")
        shell.echo_pair("Vendoring", f"{vendor_name} {url} @ {ref}")
        dstdir = vendor_dir / vendor_name
        if dstdir.exists():
            if force:
                shell.echo_warning(
                    f"Removing the directory {dstdir.resolve().as_uri()} "
                    f"(--force option present)"
                )
                shutil.rmtree(dstdir)
            else:
                shell.echo_error(
                    f"Target directory {dstdir.resolve().as_uri()} not empty. "
                    "Use the --force option to force overwriting."
                )
                continue

        # Clone repo & copy files
        with tempfile.TemporaryDirectory() as srcdir:
            clone_repo(url, ref, srcdir)
            copy(cfg.get("copy"), pathlib.Path(srcdir), dstdir)

        # Modify
        modify(cfg.get("modify"), dstdir)

        # Create
        create(cfg.get("create"), dstdir)

    shell.echo("Done.")
