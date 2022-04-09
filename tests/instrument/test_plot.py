import attune
import numpy as np

def test_plot_arrangement():
    x = np.linspace(0, 2, 21)
    a = attune.Tune(independent=x, dependent=x**0.5)
    b = attune.Tune(independent=x, dependent=x**0.3)
    arrangement = attune.Arrangement(name="test", tunes={"a": a, "b": b})
    arrangement.plot()


def test_plot_instrument():
    x = np.linspace(0, 2, 21)
    a = attune.Tune(independent=x, dependent=x**0.5)
    b = attune.Tune(independent=x, dependent=x**0.3)
    arrangement = attune.Arrangement(name="test", tunes={"a": a, "b": b})
    instrument = attune.Instrument({"arr1":arrangement}, name="test")
    instrument.plot()


if __name__ == "__main__":
    import matplotlib.pyplot as plt
    test_plot_arrangement()
    test_plot_instrument()
    plt.show()