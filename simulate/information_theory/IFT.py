import numpy as np
from scipy.special import digamma, betaln
from scipy.optimize import minimize
from jax import grad, jacfwd, jacrev, jit
from jax.numpy import maximum
from jax.scipy.special import gammaln
from .info import Info
from config import init_conf

class IFT:
    """
    Information Field Theory for matching and evaluating distributions.
    """

    def __init__(self) -> None:
        """Initializes IFT with configuration settings."""
        self.conf = init_conf()

    def match(self, trust: float, Itruth: Info, Ilie: Info, Istart: Info) -> Info:
        """Matches moments based on trust level.

        Args:
            trust (float): Trust level between 0 and 1, where 0 corresponds to 
                           complete reliance on Ilie and 1 on Itruth.
            Itruth (Info): The Info instance representing the truthful distribution.
            Ilie (Info): The Info instance representing the deceptive distribution.
            Istart (Info): The starting Info instance to help in moment matching.

        Returns:
            Info: A new Info instance representing the matched distribution.
        """
        if trust == 0: 
            return Ilie
        elif trust == 1: 
            return Itruth
        
        Istart = self.match_moments(trust, Itruth, Ilie)
        # if competence: trust*competent + trust*(1-competent) + (1-trust)
        # parameter: trust, competent, Itruth_competent, Itruth_ncompetent, Ilie (same structure)
        # -> Itruth_ncompetent nicht nötig, ist einfach Itruth_competent (oder Itruth)
        # DOCH: Wenn Competence aktualisiert wird
        # Bei I_nh wird Ca übergeben (kein Update über Kompetenz)
        u = trust * (digamma(Itruth.mu + Itruth.la + 2) - digamma(Itruth.mu + 1)) + \
            (1 - trust) * (digamma(Ilie.mu + Ilie.la + 2) - digamma(Ilie.mu + 1))
        v = trust * (digamma(Itruth.mu + Itruth.la + 2) - digamma(Itruth.la + 1)) + \
            (1 - trust) * (digamma(Ilie.mu + Ilie.la + 2) - digamma(Ilie.la + 1))
        mu, la = self.minimize_KL(u, v, Istart.mu, Istart.la)
        return Info(mu, la)
    
    def match_moments(self, trust: float, Itruth: Info, Ilie: Info) -> Info:
        """Matches moments between two Info instances based on trust level.

        Args:
            trust (float): Trust level between 0 and 1.
            Itruth (Info): Info instance for the truthful distribution.
            Ilie (Info): Info instance for the deceptive distribution.

        Returns:
            Info: A new Info instance with matched moments.
        """
        mean = trust * (mh := (Itruth.mu + 1) / (Itruth.mu + Itruth.la + 2)) + \
               (1 - trust) * (mn := (Ilie.mu + 1) / (Ilie.mu + Ilie.la + 2))
        var = trust * (mh * (1 - mh) / (Itruth.mu + Itruth.la + 3) + mh**2) + \
              (1 - trust) * (mn * (1 - mn) / (Ilie.mu + Ilie.la + 3) + mn**2) - mean**2
        mu = mean ** 2 * (1 - mean) / var - mean - 1
        la = mean * (1 - mean) ** 2 / var + mean - 2
        return Info(mu, la)

    def make_average_opinion(self, norm_weights: np.ndarray, infos: list[Info]) -> Info:
        """Calculates the average opinion based on weighted Infos.

        Args:
            norm_weights (np.ndarray): Normalized weights for each Info instance.
            infos (list[Info]): List of Info instances to average.

        Returns:
            Info: An Info instance representing the average opinion.
        """
        u = sum(np.multiply([digamma(info.mu + info.la + 2) - digamma(info.mu + 1) for info in infos], norm_weights))
        v = sum(np.multiply([digamma(info.mu + info.la + 2) - digamma(info.la + 1) for info in infos], norm_weights))
        return Info(*self.minimize_KL(u, v))
    
    def KL(self, IP: Info, IQ: Info) -> float:
        """Calculates Kullback-Leibler divergence between two Info instances.

        Args:
            IP (Info): Info instance representing the first distribution.
            IQ (Info): Info instance representing the second distribution.

        Returns:
            float: The Kullback-Leibler divergence between IP and IQ.
        """
        muP, muQ = IP.mu, IQ.mu
        laP, laQ = IP.la, IQ.la
        digamma_muP_laP = digamma(muP + laP + 2)
        temp = (
            (muP - muQ) * (digamma(muP + 1) - digamma_muP_laP) +
            (laP - laQ) * (digamma(laP + 1) - digamma_muP_laP) +
            betaln(muQ + 1, laQ + 1) - betaln(muP + 1, laP + 1)
        )
        return temp

    def get_info_difference(self, P: Info, Q: Info) -> Info:
        """Returns the difference between two Info instances.

        Args:
            P (Info): First Info instance.
            Q (Info): Second Info instance.

        Returns:
            Info: The difference between P and Q, or an Info instance with zero values if not positive.
        """
        if (result := P - Q).check_positive():
            return result
        return Info(0, 0)
    
    def minimize_KL(self, u: float, v: float, mu_start: float = 0, la_start: float = 0) -> tuple[float, float]:
        """Minimizes the KL divergence based on specified moments.

        Args:
            u (float): First moment.
            v (float): Second moment.
            mu_start (float, optional): Initial guess for mu. Defaults to 0.
            la_start (float, optional): Initial guess for la. Defaults to 0.

        Returns:
            tuple[float, float]: A tuple containing the optimized mu and la values.
        """
        def rev_loss(J: np.ndarray) -> float: 
            return jLoss(u, v, self.conf("MIN_KL"), J)

        def jac_loss(J: np.ndarray) -> np.ndarray:
            return jgradLoss(u, v, self.conf("MIN_KL"), J)

        def hes_loss(J: np.ndarray) -> np.ndarray:
            return jhessLoss(u, v, self.conf("MIN_KL"), J)

        initial_guess = [mu_start, la_start]
        if self.conf("MINIMIZE_FUNCTION") == "ACCURATE":
            fun0, fun1, res1 = 1, 0, initial_guess
            while fun1 < fun0:
                res0 = minimize(rev_loss, res1, method="trust-exact", jac=jac_loss, hess=hes_loss, tol=self.conf("GTOL"))
                fun0, res0 = res0.fun, res0.x 
                res1 = minimize(rev_loss, res0, method="trust-ncg", jac=jac_loss, hess=hes_loss, tol=self.conf("GTOL"))
                fun1, res1 = res1.fun, res1.x
            return res1[0], res1[1]
        
        elif self.conf("MINIMIZE_FUNCTION") == "SHORT":
            res0 = minimize(rev_loss, initial_guess, method="trust-exact", jac=jac_loss, hess=hes_loss, tol=self.conf("GTOL")).x
            return res0[0], res0[1]
        
@jit
def jLoss(u: float, v: float, MIN_KL: float, J: np.ndarray) -> float:
    """Loss function for matching moments between distributions.

    Args:
        u (float): First moment.
        v (float): Second moment.
        MIN_KL (float): Minimum Kullback-Leibler divergence value.
        J (np.ndarray): Current values for mu and la.

    Returns:
        float: Computed loss value.
    """
    mu, la = maximum(J[0], MIN_KL), maximum(J[1], MIN_KL)
    return (mu * u + la * v +
            gammaln(mu + 1) + gammaln(la + 1) - gammaln(mu + la + 2) +
            (J[0] - mu) ** 2 + (J[1] - la) ** 2)

@jit
def jgradLoss(u: float, v: float, MIN_KL: float, J: np.ndarray) -> np.ndarray:
    """Gradient of the loss function.

    Args:
        u (float): First moment.
        v (float): Second moment.
        MIN_KL (float): Minimum Kullback-Leibler divergence value.
        J (np.ndarray): Current values for mu and la.

    Returns:
        np.ndarray: Gradient of the loss with respect to mu and la.
    """
    return grad(jLoss, argnums=3)(u, v, MIN_KL, J)


@jit
def jhessLoss(u: float, v: float, MIN_KL: float, J: np.ndarray) -> np.ndarray:
    """Hessian of the loss function.

    Args:
        u (float): First moment.
        v (float): Second moment.
        MIN_KL (float): Minimum Kullback-Leibler divergence value.
        J (np.ndarray): Current values for mu and la.

    Returns:
        np.ndarray: Hessian matrix of the loss function.
    """
    return jacfwd(jacrev(jLoss, argnums=3), argnums=3)(u, v, MIN_KL, J)

# Create an instance of IFT
Ift = IFT()
