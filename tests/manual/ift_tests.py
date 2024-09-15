import numpy as np
from scipy.optimize import minimize
from scipy.integrate import quad
from simulate.information_theory import Info, Ift  # Import the Info class from your file

# Define the superposition of two Beta distributions using the Info class
def superpositioned_beta_pdf(x, info1, info2, w1, w2):
    """ Returns the probability density of the weighted sum of two Beta distributions. """
    return w1 * info1.probability_density(x) + w2 * info2.probability_density(x)

# KL Divergence between superpositioned Beta and single Beta
def kl_divergence_superposition_single(single_info, info1, info2, w1, w2):
    """ KL divergence between superposition of two Beta distributions and a single Beta distribution. """
    def integrand(x):
        p_x = superpositioned_beta_pdf(x, info1, info2, w1, w2)
        q_x = single_info.probability_density(x)
        return p_x * np.log(p_x / q_x) if p_x > 0 and q_x > 0 else 0

    kl, _ = quad(integrand, 0, 1)  # Integrate from 0 to 1 over x
    return kl

# Minimization function to find optimal parameters of the single Beta
def minimize_kl_divergence(info1, info2, w1, w2, initial_guess):
    """ Minimize the KL divergence to find optimal parameters for a single Beta distribution. """
    def objective(params):
        a, b = params  # The parameters of the single Beta distribution
        single_info = Info(a, b)
        return kl_divergence_superposition_single(single_info, info1, info2, w1, w2)

    result = minimize(objective, initial_guess, bounds=[(0.001, 10), (0.001, 10)], method='trust-constr')
    return result.x, result.fun

# Parameters for the superpositioned Beta function (two beta distributions)
info1 = Info(2.0, 5.0)  # First Beta distribution (a1, b1)
info2 = Info(3.0, 3.0)  # Second Beta distribution (a2, b2)
w1, w2 = 0.5, 0.5  # Weights for the superposition


# Initial guess for the parameters of the single Beta distribution
initial_guess = [2.5, 2.5]

# Minimize the KL divergence to find the optimal parameters for the single Beta
optimal_params, min_kl_value = minimize_kl_divergence(info1, info2, w1, w2, initial_guess)

# Output the optimal parameters and minimum KL divergence value
print(f"Optimal a: {optimal_params[0]}")
print(f"Optimal b: {optimal_params[1]}")
print(f"Minimum KL Divergence: {min_kl_value}")

# IFT object
result = Ift.match(0.3, info1, info2, Info(initial_guess[0], initial_guess[1]))
print(result)
print(f"Minimum KL Divergence: {kl_divergence_superposition_single(result, info1, info2, 0.3, 0.7)}")