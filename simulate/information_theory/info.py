import numpy as np
from scipy import integrate
from scipy.stats import beta as Beta

# from config import conf

class Info:
    def __init__(self, mu = 0, la = 0):
        # total = mu + la
        # if total > conf("MAX_COUNT"):
        #     scale = conf("MAX_COUNT") / total
        #     mu, la = mu * scale, la * scale
        MIN_KL = -0.9999
        self.mu, self.la = max(mu, MIN_KL), max(la,MIN_KL)
        self.mean = (self.mu + 1) / (self.mu + self.la + 2) 
        # self.mean = Beta.mean(self.mu + 1, self.la + 1)
        # self.rms = np.sqrt(Beta.var(self.mu + 1, self.la + 1))

    def __str__(self):
        # return (f"x = {self.mean:10.4f} ± {self.rms:10.4f} "f"({self.mu:5.2f}, {self.la:5.2f})")
        # mu, la = f"{self.mu:5.2f}".lstrip(), f"{self.la:5.2f}".lstrip()
        mu, la = f"{self.mu}".lstrip(), f"{self.la}".lstrip()
        return (f"({mu}, {la})")

    def __add__(self, other):
        return Info(self.mu + other.mu, self.la + other.la)
    
    def __sub__(self, other):
        return Info(self.mu - other.mu, self.la - other.la)

    def __mul__(self, a):
        return Info(a * self.mu, a * self.la)

    def __rmul__(self, a):
        return self * a
    
    def round(self, digits):
        return Info(round(self.mu, digits), round(self.la, digits))
    
    def round_mean(self):
        return float(round(self.mean, 3))

    def draw(self):
        return Beta.random_state.beta(self.mu + 1, self.la + 1)

    # def average(self, f):
    #     return integrate.quad(lambda x: self.pdf(x, self.mu, self.la) * f(x), 0, 1)[0]

    # def norm(self):
    #     return self.average(lambda x: 1)

    # def arr(self):
    #     return np.array([self.mu, self.la])

    # def to_list(self):
    #     return {"mu": float(self.mu), "la": float(self.la)}
    
    # def probability_density(self, x):
    #     return Beta.pdf(x, self.mu + 1, self.la + 1)

    # def hamiltonian(self, x, mu, la):
    #     return -Beta.logpdf(x, mu + 1, la + 1)
    
    def check_positive(self):
        return self.mu >= 0 and self.la >= 0
    

    
Inf = Info()