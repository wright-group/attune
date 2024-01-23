import click

from .attune.__version__ import __version__
from .attune import _store


@click.group()
@click.version_option(__version__)
def main():
    pass


@main.command(name="inspect")
@click.argument("instrument", nargs=1)
@click.option("--arrangement", "-a", default=None)
def inspect(instrument, arrangement=None, tune=None):
    instr = _store.load(instrument)
    instr.print_tree()


@main.command(name="catalog")
def catalog():
    for ins in _store.catalog():
        print(ins)


@main.command(name="history")
@click.argument("instrument", nargs=1)
@click.option("-n", default=10)
def history(instrument, n=10):
    title_string = f"{instrument}, from latest to earliest"
    print(title_string + "-" * (80 - len(instrument)))
    current = _store.load(instrument)
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
            current = _store.undo(current)
        except ValueError:  # reached end of history
            print("<end of history>")
            break


if __name__ == "__main__":
    main()
