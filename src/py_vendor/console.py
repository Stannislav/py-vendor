import click

import py_vendor


@click.group()
def run():
    pass


@run.command()
def version():
    click.secho("Version", fg="blue", nl=False)
    click.echo(": ", nl=False)
    click.secho(py_vendor.__version__, fg="green")
