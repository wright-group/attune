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
@click.option("-n", default=10, help="number of change records to list")
# TODO: add a --date option (perhaps just date) to anchor the history list to
# TODO: add a --direction option to search forward or backward from date
def history(instrument, n=10):
    title_string = f"{instrument}, from latest to earliest"
    print(title_string + "-" * (80 - len(instrument)))
    current = store.load(instrument)
    for i in range(n):
        try:
            print(
                "{0:4} {1}{2} at {3}".format(
                    -i,
                    current.transition.type,
                    "." * (20 - len(current.transition.type)),
                    str(current.load),
                )
            )
            current = store.undo(current)
        except ValueError:  # reached end of history
            print("<end of history>")
            break


if __name__ == "__main__":
    main()
