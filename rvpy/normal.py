import numpy as np
from scipy.stats import norm, lognorm
from . import distribution
from . import gamma, cauchy

class Normal(distribution.Distribution):
    def __init__(self, mu=0, sigma=1):
        assert isinstance(mu, (int, float)), "mu must be numeric!"
        assert isinstance(sigma, (int, float)), "sigma must be numeric!"
        assert sigma > 0, "sigma must be positive"

        self.mu = mu
        self.sigma = sigma

        # Scipy backend
        self.sp = norm(mu, sigma)

        # Intialize super
        super().__init__()

    def __repr__(self):
        return f"Normal(mu={self.mu}, sigma={self.sigma})"

    def __add__(self, other):
        if isinstance(other, Normal):
            new_mu = other.mu + self.mu
            new_sigma = (self.var + other.var)**0.5
            return Normal(new_mu, new_sigma)
        elif isinstance(other, (int, float)):
            return Normal(self.mu + other, self.sigma)
        else:
            raise TypeError(f"Addiing {type(other)} to Normal not supported")

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return Normal(other*self.mu, float(np.abs(other)*self.sigma))
        else:
            raise TypeError("Only multiplicated by int or float supported.")

    def __truediv__(self, other):
        if isinstance(other, (int, float)) and other != 0:
            return self.__mul__(1 / other)
        elif isinstance(other, Normal):
            self.to_standard()
            other.to_standard()
            return cauchy.StandardCauchy()
        else:
            raise ZeroDivisionError("Cannot divide a Normal by zero!")

    def __neg__(self):
        return Normal(-self.mu, self.sigma)
    
    def __pow__(self, n):
        return self.to_standard()**n

    def exp(self):
        return LogNormal(self.mu, self.sigma)

    def mgf(self, t):
        return np.exp(t*self.mu + 0.5*(t**2)*(self.var))

    def to_standard(self):
        if np.round(self.mu, 7) == 0 and np.round(self.sigma, 7) == 1:
            return StandardNormal()
        else:
            raise ValueError("Must be Normal(0, 1) to standardize!")


class StandardNormal(Normal):
    def __init__(self):
        # Get non-standard Normal distribution initialization
        super().__init__(0, 1)

    def __repr__(self):
        return f"StandardNormal(mu=0, sigma=1)"

    def __pow__(self, k):
        assert k == 2, "Only squaring standard normal is supportd"
        return gamma.ChiSq(1)

    def to_nonstandard(self):
        return Normal(mu=0, sigma=1)

class LogNormal(distribution.Distribution):
    def __init__(self, mu=0, sigma=1):
        assert sigma > 0, "sigma must be positive"

        # Parameters
        self.mu = mu
        self.sigma = sigma

        # Scipy backend
        self.sp = lognorm(s=sigma, scale=np.exp(mu))

        super().__init__()

    def __repr__(self):
        return f"LogNormal(mu={self.mu}, sigma={self.sigma})"

    def log(self):
        return Normal(self.mu, self.sigma)

    def __mul__(self, other):
        if isinstance(other, LogNormal):
            return LogNormal(self.mu + other.mu, self.sigma + other.sigma)
        elif isinstance(other, (int, float)):
            if other == 0:
                raise TypeError("Can't multiply by 0!")
            else:
                return LogNormal(self.mu + np.log(other), self.sigma)
        else:
            raise TypeError(f"Multiplying LogNormal by {type(other)} not supported.")

    def __truediv__(self, c):
            return self.__mul__(1/c)

    def __rtruediv__(self, c):
        if isinstance(c, (int, float)):
            return c*LogNormal(-self.mu, self.sigma)
        else:
            raise TypeError(f"__rtruediv__ of LogNormal by {type(c)} not supported.")

    def __pow__(self, k):
        if isinstance(k, (int, float)) and k != 0:
            if k != 0:
                return LogNormal(k*self.mu, abs(k)*self.sigma)
            else:
                raise ValueError("Exponent to LogNormal must be nonzero.")
        else:
            raise TypeError(f"Exponentiation of LogNormal by {type(k)} not supported.")
