from __future__ import annotations

import logging
import pathlib
import re
import shutil
import subprocess
import tempfile

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


def copy_item(item: str | dict, srcdir: pathlib.Path, dstdir: pathlib.Path):
    if isinstance(item, dict):
        pattern = item.get("pattern")
        target_str = item.get("dest", "")
        rel_dir = item.get("relative_to", "")
        header = item.get("header", "")
        subs = [(re.compile(pattern), repl) for pattern, repl in item.get("subs", [])]
    else:
        pattern = item
        target_str = ""
        rel_dir = ""
        header = ""
        subs = []
    logger.debug("header:\n%s", header)
    logger.debug("subs:\n%s", "".join(map(str, subs)))
    target = dstdir / target_str
    for path in srcdir.glob(pattern):
        pathdst = target / path.relative_to(srcdir).relative_to(rel_dir)
        logger.info(f"copying {path.relative_to(srcdir)} to {pathdst}")
        if path.is_dir():
            if header:
                logging.warning("header ignored for directory: %s", path)
            shutil.copytree(path, pathdst)
        else:
            pathdst.parent.mkdir(parents=True, exist_ok=True)
            if header or subs:
                with open(path) as fh_in, open(pathdst, "w") as fh_out:
                    if header:
                        fh_out.write(header)
                    if subs:
                        lines = fh_in.readlines()
                        for pattern, repl in subs:
                            logger.info(
                                'applying sub "%s" ->  "%s" to %s',
                                pattern.pattern,
                                repl,
                                pathdst,
                            )
                            lines = [pattern.sub(repl, line) for line in lines]
                        fh_out.writelines(lines)
                    else:
                        # maybe faster than writing line-by-line
                        fh_out.write(fh_in.read())
                shutil.copymode(path, pathdst)
            else:
                shutil.copy2(path, pathdst)


def do_vendor(
    url: str, dstdir: pathlib.Path, ref: str, files: list[str | dict] | None = None
):
    with tempfile.TemporaryDirectory() as srcdir:
        clone_repo(url, ref, srcdir)
        if files is None:
            logger.info("no files specified, copying everything to %s", dstdir)
            shutil.copytree(srcdir, dstdir)
        else:
            dstdir.mkdir()
            for item in files:
                copy_item(item, pathlib.Path(srcdir), dstdir)
