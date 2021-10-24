from __future__ import annotations

import logging
import pathlib
import re
import shutil
import subprocess
import tempfile
from typing import Iterable

logger = logging.getLogger(__name__)


def clone_repo(url: str, ref: str, target: str | pathlib.Path):
    kwargs = {"cwd": target, "capture_output": True}
    commands = [
        ["git", "init"],
        ["git", "remote", "add", "origin", url],
        ["git", "fetch", "--depth", "1", "origin", ref],
        ["git", "reset", "--hard", "FETCH_HEAD"],
    ]
    for cmd in commands:
        proc = subprocess.run(cmd, **kwargs)
        stdout = proc.stdout.decode().strip()
        stderr = proc.stderr.decode().strip()
        if stdout:
            logger.debug(stdout)
        if stderr:
            logger.debug(stderr)


def apply_header_subs(
    header: str | None,
    subs: Iterable[tuple[str, str]] | None,
    srcpath: str | pathlib.Path,
    dstpath: str | pathlib.Path,
) -> None:
    with open(srcpath) as fh_in, open(dstpath, "w") as fh_out:
        if header:
            fh_out.write(header)
        if subs:
            lines = fh_in.readlines()
            for pattern, replacement in subs:
                pattern_c = re.compile(pattern)
                logger.info(
                    'applying sub "%s" ->  "%s" to %s',
                    pattern,
                    replacement,
                    dstpath,
                )
                lines = [pattern_c.sub(replacement, line) for line in lines]
            fh_out.writelines(lines)
        else:
            # maybe faster than writing line-by-line
            fh_out.write(fh_in.read())
    shutil.copymode(srcpath, srcpath)


def copy_item(item: str | dict, srcdir: pathlib.Path, dstdir: pathlib.Path):
    if isinstance(item, dict):
        pattern = item.get("pattern")
        target_str = item.get("dest", "")
        rel_dir = item.get("relative_to", "")
        header = item.get("header")
        subs = item.get("subs")
    else:
        pattern = item
        target_str = ""
        rel_dir = ""
        header = None
        subs = None
    logger.debug("header: %s", header)
    logger.debug("subs: %s", subs)
    target = dstdir / target_str

    srcpaths = list(srcdir.glob(pattern))
    if not srcpaths:
        logger.warning(f'The pattern "{pattern}" gave no results')
        return

    for srcpath in srcpaths:
        dstpath = target / srcpath.relative_to(srcdir).relative_to(rel_dir)
        logger.info(f"copying {srcpath.relative_to(srcdir)} to {dstpath}")
        if srcpath.is_dir():
            if header:
                logging.warning("header ignored for directory: %s", srcpath)
            if subs:
                logging.warning("subs ignored for directory: %s", srcpath)
            shutil.copytree(srcpath, dstpath)
        else:
            dstpath.parent.mkdir(parents=True, exist_ok=True)
            if header or subs:
                apply_header_subs(header, subs, srcpath, dstpath)
            else:
                shutil.copy2(srcpath, dstpath)


def copy(
    files: list[str | dict] | None,
    srcdir: pathlib.Path,
    dstdir: pathlib.Path,
) -> None:
    if files is None:
        logger.info("no files specified, copying everything to %s", dstdir)
        shutil.copytree(srcdir, dstdir)
    else:
        dstdir.mkdir()
        for item in files:
            copy_item(item, srcdir, dstdir)


def modify_item(item: dict, dstdir: pathlib.Path) -> None:
    pattern = item.get("pattern")
    header = item.get("header")
    subs = item.get("subs", [])

    if not header and not subs:
        logger.warning("no header nor subs provided, nothing to modify")
        return

    dstpaths = list(dstdir.glob(pattern))
    if not dstpaths:
        logger.warning(f'The pattern "{pattern}" gave no results')
        return

    if all(dstpath.is_dir() for dstpath in dstpaths):
        logger.warning(f'The pattern "{pattern}" matched only directories')

    with tempfile.TemporaryDirectory() as tempdir_s:
        tempdir = pathlib.Path(tempdir_s)
        for dstpath in dstpaths:
            # Check if dstpath is a directory
            if dstpath.is_dir():
                logger.warning(
                    "Can't modify a directory (%s, matched by %s), skipping",
                    dstpath,
                    pattern,
                )
                continue

            # Copy the current file to a temporary location
            srcpath = tempdir / dstpath.relative_to(dstdir)
            srcpath.parent.mkdir(exist_ok=True, parents=True)
            shutil.copy2(dstpath, srcpath)

            # Copy the file back while apply all modifications
            apply_header_subs(header, subs, srcpath, dstpath)


def modify(items: Iterable[dict] | None, dstdir: pathlib.Path):
    if items is None:
        logger.info("no files to modify")
        return

    for item in items:
        modify_item(item, dstdir)


def create(files: Iterable[str] | None, dstdir: pathlib.Path):
    if files is None:
        logger.info("no files to create")
        return

    for filename in files:
        path = dstdir / filename
        logger.info("creating %s", path)
        path.parent.mkdir(exist_ok=True, parents=True)
        path.touch()
