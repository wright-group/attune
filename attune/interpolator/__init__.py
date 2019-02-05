from ._base import Interpolator
from ._linear import Linear
from ._poly import Poly
from ._spline import Spline

builtins = {"Linear": Linear, "Poly": Poly, "Spline": Spline}
