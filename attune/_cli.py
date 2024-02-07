import click

from .__version__ import __version__
from . import _store as store


@click.group()
@click.version_option(__version__)
def main():
    pass


@main.command(name="inspect", help="show the structure of an instrument")
@click.argument("instrument", nargs=1)
def inspect(instrument, arrangement=None, tune=None):
    instr = store.load(instrument)
    instr.print_tree()


@main.command(name="catalog", help="lists the instrument names in the catalog")
def catalog():
    for ins in store.catalog():
        print(ins)


@main.command(name="history", help="show the change history of an instrument")
@click.argument("instrument", nargs=1)
@click.option("-n", default=10, help="number of records to list (default is 10)")
@click.option("--start", "-s", default="now", help="date to start history (default is now)")
@click.option(
    "--forward",
    "-f",
    is_flag=True,
    show_default=True,
    default=False,
    help="when specified, history will search forwards in time",
)
def history(instrument, n=10, start="now", forward=False):
    store.print_history(instrument, n, start, reverse=not forward)


if __name__ == "__main__":
    main()
