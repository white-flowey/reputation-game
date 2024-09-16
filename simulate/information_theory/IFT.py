import numpy as np
from scipy.special import digamma, betaln
from scipy.optimize import minimize
from jax import grad, jacfwd, jacrev, jit
from jax.numpy import maximum, log10
from jax.scipy.special import gammaln
from .LUT import LUT
from .info import Info
from config import init_conf

@jit
def find_index_log_to_lin(value, log_start, log_end, n_lin_indices):
    return (n_lin_indices - 1) / (log_end - log_start) * (log10(value) - log_start)


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
        pass

    def match(self, trust, Itruth, Ilie, Istart=None, method=None):
        method = method if method else self.conf("COMPRESSION_METHOD")

        if trust == 0: 
            return Ilie
        elif trust == 1: 
            return Itruth
        
        if Istart == None:
            Istart = Info(0, 0)

        if method == "KL_minimization":
            u = trust * (digamma(Itruth.mu + Itruth.la + 2) - digamma(Itruth.mu + 1)) + (1 - trust) * (digamma(Ilie.mu + Ilie.la + 2) - digamma(Ilie.mu + 1))
            v = trust * (digamma(Itruth.mu + Itruth.la + 2) - digamma(Itruth.la + 1)) + (1 - trust) * (digamma(Ilie.mu + Ilie.la + 2) - digamma(Ilie.la + 1))
            mu, la = self.minimize_KL(u, v, Istart.mu, Istart.la)
            return Info(mu, la)

        if method == "moment_matching":
            mean = trust * (mh := (Itruth.mu + 1) / (Itruth.mu + Itruth.la + 2)) + (1 - trust) * (mn := (Ilie.mu + 1) / (Ilie.mu + Ilie.la + 2))
            var = trust * (mh * (1 - mh) / (Itruth.mu + Itruth.la + 3) + mh**2) + (1 - trust) * (mn * (1 - mn) / (Ilie.mu + Ilie.la + 3) + mn**2) - mean**2
            mu = mean ** 2 * (1 - mean) / var - mean - 1
            la = mean * (1 - mean) ** 2 / var + mean - 2
            return Info(mu, la)

        if method == "LUT":
            u = trust * (digamma(Itruth.mu + Itruth.la + 2) - digamma(Itruth.mu + 1)) + (1 - trust) * (digamma(Ilie.mu + Ilie.la + 2) - digamma(Ilie.mu + 1))
            v = trust * (digamma(Itruth.mu + Itruth.la + 2) - digamma(Itruth.la + 1)) + (1 - trust) * (digamma(Ilie.mu + Ilie.la + 2) - digamma(Ilie.la + 1))
            u_index = find_index_log_to_lin(u, -3, 1.5, LUT.len)
            v_limit = u - np.log(np.exp(u) - 1)
            v_index = self.find_index_poly_to_lin(v, 1.000001 * v_limit, 32, LUT.len)
            mu, la = self.minimize_KL(u, v, 10**float(LUT.mu((u_index, v_index))) - 1, 10**float(LUT.la((u_index, v_index))) - 1) if 0 < u_index < LUT.len and 0 < v_index < LUT.len else self.minimize_KL(u, v, Istart.mu, Istart.la)
            return Info(mu, la)
        

    def make_average_opinion(self, infos, norm_weights):
        u = sum(np.multiply([digamma(info.mu + info.la + 2) - digamma(info.mu + 1) for info in infos], norm_weights))
        v = sum(np.multiply([digamma(info.mu + info.la + 2) - digamma(info.la + 1) for info in infos], norm_weights))


        if self.conf("COMPRESSION_METHOD") == "LUT":
            u_index = self.find_index_log_to_lin(u, -3, 1.5, LUT.len)
            v_limit = mu - np.log(np.exp(u) - 1)
            v_index = self.find_index_poly_to_lin(v, 1.000001 * v_limit, 32, LUT.len)
            if 0 <= u_index <= LUT.len and 0 <= v_index <= LUT.len:
                mu = 10 ** (float(LUT.mu((u_index, v_index)))) - 1
                la = 10 ** (float(LUT.la((u_index, v_index)))) - 1
                return Info(mu, la)

        return Info(self.minimize_KL(u, v))


    def find_index_poly_to_lin(self, value, poly_start, poly_end, N, exp=10):
        slope = (poly_start - poly_end) / (poly_start ** exp - poly_end ** exp)
        value_at_0 = poly_start - slope * poly_start ** exp
        return ((value - value_at_0) / slope) ** (1 / exp) * (N - 1) / (poly_end - value_at_0)
    
    # def minimize_KL(self, u, v, mu_start=0, la_start=0):
    #     def rev_loss(J): return jLoss(u, v, self.conf("MIN_KL"), J)
    #     def jac_loss(J): return jgradLoss(u, v, self.conf("MIN_KL"), J)
    #     def hess_loss(J): return jhessLoss(u, v, self.conf("MIN_KL"), J)
        
    #     initial_guess = [mu_start, la_start]
    #     if self.conf("OPTIMIZATION_METHOD") == "trust-constr":
    #         result = minimize(rev_loss, initial_guess, method="trust-constr", jac=jac_loss, hess=hess_loss, options={"gtol": self.conf("GTOL")})
    #     elif self.conf("OPTIMIZATION_METHOD") == "L-BFGS-B":
    #         result = minimize(rev_loss, initial_guess, method="L-BFGS-B")

    #     return result.x[0], result.x[1]  # mu, la
    
    def KL(self, IP, IQ):
        muP, muQ = IP.mu, IQ.mu
        laP, laQ = IP.la, IQ.la
        return (
            (muP - muQ) * (digamma(muP + 1) - digamma(muP + laP + 2))
            + (laP - laQ) * (digamma(laP + 1) - digamma(muP + laP + 2))
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

        if self.conf("MINIMIZE_FUNCTION") == "DEFAULT":
            res1 = [mu_start, la_start]
            fun0, fun1 = 1, 0

            while fun1 < fun0:
                res0 = minimize(rev_loss, res1, method="trust-exact", jac=jac_loss, hess=hes_loss, tol=self.conf("GTOL"))
                fun0, res1 = res0.fun, minimize(rev_loss, res0.x, method="trust-ncg", jac=jac_loss, hess=hes_loss, tol=self.conf("GTOL"))
                fun1, res1 = res1.fun, res1.x
            return res1[0], res1[1]
        
        elif self.conf("MINIMIZE_FUNCTION") == "UPDATED": 
            initial_guesss = [mu_start, la_start]
            result = minimize(rev_loss, initial_guesss, method="trust-exact", jac=jac_loss, hess=hes_loss, tol=self.conf("GTOL")).x

            return result[0], result[1]

    
Ift = IFT()