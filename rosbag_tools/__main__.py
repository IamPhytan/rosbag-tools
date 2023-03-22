import click

from . import __version__

CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(__version__)
def cli_main():
    pass


if __name__ == "__main__":
    cli_main()
