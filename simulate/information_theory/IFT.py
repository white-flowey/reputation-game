import numpy as np
from scipy.special import digamma, betaln
from scipy.optimize import minimize
from jax import grad, jacfwd, jacrev, jit
from jax.numpy import maximum
from jax.scipy.special import gammaln
from .info import Info
from config import init_conf


@jit
def jLoss(u, v, MIN_KL, J):
    """Loss function for matching moments ln(x) and ln(1-x) between the
    non-parametrized distribution and a beta distribution."""
    mu, la = maximum(J[0], MIN_KL), maximum(J[1], MIN_KL)
    return mu * u + la * v + gammaln(mu + 1) + gammaln(la + 1) - gammaln(mu + la + 2) + (J[0] - mu) ** 2 + (J[1] - la) ** 2

@jit
def jgradLoss(u, v, MIN_KL, J):
    """Gradient of the loss function."""
    return grad(jLoss, argnums=3)(u, v, MIN_KL, J)

@jit
def jhessLoss(u, v, MIN_KL, J):
    """Hessian of the loss function."""
    return jacfwd(jacrev(jLoss, argnums=3), argnums=3)(u, v, MIN_KL, J)

class IFT():
    def __init__(self):
        self.conf = init_conf()

    def match(self, trust, Itruth, Ilie, Istart):
        Istart = self.match_moments(trust, Itruth, Ilie)

        if trust == 0: 
            return Ilie
        elif trust == 1: 
            return Itruth
        
        u = trust * (digamma(Itruth.mu + Itruth.la + 2) - digamma(Itruth.mu + 1)) + (1 - trust) * (digamma(Ilie.mu + Ilie.la + 2) - digamma(Ilie.mu + 1))
        v = trust * (digamma(Itruth.mu + Itruth.la + 2) - digamma(Itruth.la + 1)) + (1 - trust) * (digamma(Ilie.mu + Ilie.la + 2) - digamma(Ilie.la + 1))
        mu, la = self.minimize_KL(u, v, Istart.mu, Istart.la)
        return Info(mu, la)
    
    def match_moments(self, trust, Itruth, Ilie):
        mean = trust * (mh := (Itruth.mu + 1) / (Itruth.mu + Itruth.la + 2)) + (1 - trust) * (mn := (Ilie.mu + 1) / (Ilie.mu + Ilie.la + 2))
        var = trust * (mh * (1 - mh) / (Itruth.mu + Itruth.la + 3) + mh**2) + (1 - trust) * (mn * (1 - mn) / (Ilie.mu + Ilie.la + 3) + mn**2) - mean**2
        mu = mean ** 2 * (1 - mean) / var - mean - 1
        la = mean * (1 - mean) ** 2 / var + mean - 2
        return Info(mu, la)

    def make_average_opinion(self, norm_weights, infos):
        u = sum(np.multiply([digamma(info.mu + info.la + 2) - digamma(info.mu + 1) for info in infos], norm_weights))
        v = sum(np.multiply([digamma(info.mu + info.la + 2) - digamma(info.la + 1) for info in infos], norm_weights))
        return Info(*self.minimize_KL(u, v))

    def KL(self, IP, IQ):
        muP, muQ = IP.mu, IQ.mu
        laP, laQ = IP.la, IQ.la
        digamma_muP_laP = digamma(muP + laP + 2)
        return (
            (muP - muQ) * (digamma(muP + 1) - digamma_muP_laP)
            + (laP - laQ) * (digamma(laP + 1) - digamma_muP_laP)
            + betaln(muQ + 1, laQ + 1) - betaln(muP + 1, laP + 1)
        )

    def get_info_difference(self, P, Q):
        if (result := P - Q).check_positive:
            return result
        return Info(0, 0)
    
    def minimize_KL(self, u, v, mu_start=0, la_start=0):
        def rev_loss(J):
            return jLoss(u, v, self.conf("MIN_KL"), J)

        def jac_loss(J):
            return jgradLoss(u, v, self.conf("MIN_KL"), J)

        def hes_loss(J):
            return jhessLoss(u, v, self.conf("MIN_KL"), J)

        initial_guess = [mu_start, la_start]
        if self.conf("MINIMIZE_FUNCTION") == "ACCURATE":
            fun0, fun1 = 1, 0
            while fun1 < fun0:
                res0 = minimize(rev_loss, initial_guess, method="trust-exact", jac=jac_loss, hess=hes_loss, tol=self.conf("GTOL"))
                fun0, res0 = res0.fun, res0.x 
                res1 = minimize(rev_loss, res0, method="trust-ncg", jac=jac_loss, hess=hes_loss, tol=self.conf("GTOL"))
                fun1, res1 = res1.fun, res1.x
                return res1[0], res1[1]
        
        elif self.conf("MINIMIZE_FUNCTION") == "SHORT":
                res0 = minimize(rev_loss, initial_guess, method="trust-exact", jac=jac_loss, hess=hes_loss, tol=self.conf("GTOL")).x
                return res0[0], res0[1]
Ift = IFT()