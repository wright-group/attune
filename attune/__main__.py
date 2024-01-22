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
    if arrangement is None:
        pass
    print("inspecting")
    pass


@main.command(name="catalog")
def catalog():
    for ins in _store.catalog():
        print(_store.load(ins).__repr__())


@main.command(name="history")
@click.argument("instrument", nargs=1)
@click.option("-n", default=5)
def history(instr, n=5):
    for i in range(n):
        print(n)


if __name__ == "__main__":
    main()
