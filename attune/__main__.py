import click

from attune.__version__ import __version__
import attune._store as _store


@click.group()
@click.version_option(__version__)
def main():
    pass


@main.command(name="inspect")
@click.argument("instrument", nargs=1)
@click.option("--arrangement", "-a", default=None)
def inspect(instrument, arrangement=None, tune=None):
    instr = _store.load(instrument)
    print(instr.__repr__())


@main.command(name="catalog")
def catalog():
    for ins in _store.catalog():
        print(ins)


@main.command(name="history")
@click.argument("instrument", nargs=1)
@click.option("-n", default=5)
def history(instrument, n=5):
    title_string = f"{instrument}, from latest to earliest"
    print(title_string + "-"*(80-len(instrument)))
    current = _store.load(instrument)
    for i in range(n):
        try:            
            print("{0}{1} at {2}".format(
                current.transition.type,
                " " * (20-len(current.transition.type)),
                str(current.load)))
            current = _store.undo(current)
        except ValueError:  # reached end of history
            break


if __name__ == "__main__":
    main()
