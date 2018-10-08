import numpy as np
from scipy.stats import gamma
from . import distribution, laplace

class Gamma(distribution.Distribution):
    def __init__(self, alpha, beta):
        assert alpha > 0 and beta > 0, "alpha and beta must be positive"

        self.alpha = alpha
        self.beta = beta

        # Scipy backend
        self.sp = gamma(a=alpha, scale=beta)

        # Initialize super
        super().__init__()

    def __repr__(self):
        return f"Gamma(alpha={self.alpha}, beta={self.beta})"

    def __add__(self, other):
        if isinstance(other, Gamma):
            if self.beta != other.beta:
                raise ValueError("Scale paramters of Gamma families must match")
            else:
                return Gamma(self.alpha + other.alpha, self.beta)
        else:
            raise TypeError("Only addition/subtraction of Gamma families supported")

    def __sub__(self, other):
        try:
            other = other.to_exponential()
            self.to_exponential()
        except:
            raise TypeError("Only subtraction of two Exponential random variables currently supported")

        if other.scale == self.to_exponential().scale:
            return laplace.Laplace(0, other.scale)
        else:
            raise TypeError("Difference of Exponentials must share scale parameter")

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return Gamma(self.alpha, other*self.beta)
        else:
            raise TypeError("Only multiplication by scalar supported")

    def __truediv__(self, other):
        if isinstance(other, (int, float)) and other != 0:
            return self.__mul__(1 / other)
        else:
            raise ZeroDivisionError("Cannot divide by zero!")

    def mgf(self, t):
        return np.where(t < 1/self.beta,
                   (1 - self.beta * t) ** (-self.alpha),
                   np.nan
               )

    def to_exponential(self):
        assert self.alpha == 1, "Alpha must be 1 to downcast to Exponential"
        return Exponential(self.beta)

    def to_chisq(self):
        assert self.beta == 2, "Beta must be 2 to downcast to ChiSq"
        return ChiSq(2*self.alpha)

class Exponential(Gamma):
    def __init__(self, scale):
        # Get Gamma distribution initialization
        super().__init__(1, scale)

        # Parameters
        self.scale = scale
        self.rate = 1 / scale

    def __repr__(self):
        return f"Exponential(scale={self.scale})"

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return Exponential(other*self.scale)
        else:
            raise TypeError("Only multiplication by scalar supported")

    #  TODO: def __sub__(self): -> Laplace

    def to_gamma(self):
        return Gamma(alpha=1, beta=self.scale)

    # NOTE: .to_chisq() unnecessary since special case when scale == 2
    # inherits from Gamma.

class ChiSq(Gamma):
    def __init__(self, df):
        assert isinstance(df, int), "Only integer degrees of freedome allowed."
        # Get Gamma distribution initialization
        super().__init__(alpha=df/2, beta=2)

        # Parameters
        self.df = df

    def __repr__(self):
        return f"ChiSq(df={self.df})"

    def __add__(self, other):
        if isinstance(other, ChiSq):
            return ChiSq(self.df + other.df)
        else:
            return self.to_gamma() + other

    def to_gamma(self):
        return Gamma(alpha=self.df/2, beta=2)

    # NOTE: .to_exponential() unnecessary since case when df == 2
    # inherits from Gamma.
