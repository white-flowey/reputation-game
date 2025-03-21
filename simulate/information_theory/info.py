MAX_COUNT = 1e6

class Info:
    """
    Represents information with parameters for a Beta distribution.
    Instances of this class are the main mathematical object for Information Theoretical calculations in simulation.

    Attributes:
        mu (float): First shape parameter of the Beta distribution.
        la (float): Second shape parameter of the Beta distribution.
        mean (float): Mean of the Beta distribution calculated from mu and la.
    """

    def __init__(self, mu: float = 0, la: float = 0) -> None:
        """
        Initializes Info with mu and la parameters.

        Args:
            mu (float): First shape parameter (default is 0).
            la (float): Second shape parameter (default is 0).
        """
        MIN_KL = -0.9999
        self.mu, self.la = max(mu, MIN_KL), max(la, MIN_KL)
        total = mu+la
        if (total := mu + la) > MAX_COUNT: #limit to a million counts
            mu = MAX_COUNT * mu / total # rescaled
            la = MAX_COUNT * la / total # rescaled
        self.mu, self.la = mu, la
    
    @property
    def mean(self):
        """Returns mean of the Beta distribution"""
        return (self.mu + 1) / (self.mu + self.la + 2)

    def __str__(self) -> str:
        """Returns string representation of the Info instance."""
        mu, la = f"{self.mu}".lstrip(), f"{self.la}".lstrip()
        return f"({mu}, {la})"

    def __add__(self, other: 'Info') -> 'Info':
        """Adds another Info instance."""
        return Info(self.mu + other.mu, self.la + other.la)
    
    def __sub__(self, other: 'Info') -> 'Info':
        """Subtracts another Info instance."""
        return Info(self.mu - other.mu, self.la - other.la)

    def __mul__(self, a: float) -> 'Info':
        """Multiplies by a scalar."""
        return Info(a * self.mu, a * self.la)

    def __rmul__(self, a: float) -> 'Info':
        """Supports right multiplication."""
        return self * a
    
    def round(self, digits: int) -> 'Info':
        """Rounds mu and la to specified digits."""
        self.mu = round(self.mu, digits)
        self.la = round(self.la, digits)
        return self
    
    def round_mean(self) -> float:
        """Returns the rounded mean value."""
        return float(round(self.mean, 3))

    def draw(self) -> float:
        """Draws a sample from the Beta distribution."""
        from scipy.stats import beta as Beta
        return Beta.random_state.beta(self.mu + 1, self.la + 1)
    
    def check_positive(self) -> bool:
        """Checks if mu and la are non-negative."""
        return (self.mu >= 0) & (self.la >= 0)
