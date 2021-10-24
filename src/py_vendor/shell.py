import click


def echo(msg):
    click.secho(msg, fg="blue")


def echo_warning(msg):
    click.secho(msg, fg="yellow")


def echo_error(msg):
    click.secho(msg, fg="red")


def echo_pair(key, value):
    click.secho(key, fg="blue", nl=False)
    click.echo(": ", nl=False)
    click.secho(value, fg="green")
