import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import linregress


def get_linear_fit(x: list, y: list) -> dict:
    """
    Calculate linear regression parameters for given x and y data.

    Args:
        x (list): List of x-values (independent variable).
        y (list): List of y-values (dependent variable).

    Returns:
        dict: Dictionary containing linear fit parameters:
            - 'slope': Slope of the regression line
            - 'intercept': Y-intercept of the regression line
            - 'r_value': Correlation coefficient
    """
    slope, intercept, r_value, _, _ = linregress(x, y)

    return {"slope": slope, "intercept": intercept, "r_value": r_value}


def plot_linear_fit(data: dict) -> None:
    """
    Plot linear regression fits for multiple datasets.

    Args:
        data (dict): Dictionary where keys are labels and values are tuples of
                    (x_values, y_values, color) for plotting.

    Returns:
        None: Displays plots using matplotlib.
    """
    for label, (x, y, color) in data.items():

        slope, intercept, r_value, _, _ = linregress(x, y)
        line_eq = f"{label} Fit: y = {slope:.2f}x + {intercept:.2f} (R = {r_value:.3f})"

        x_fit = np.linspace(min(x), max(x), 100)
        y_fit = slope * x_fit + intercept

        plt.figure(figsize=(6, 4))
        plt.plot(x, y, "o", color=color, label="Data Points")
        plt.plot(x_fit, y_fit, "-", color=color, alpha=0.6, label="Linear Fit")
        plt.title(f"{label} - Linear Fit\n{line_eq}")
        plt.xlabel("Short Tons")
        plt.ylabel("Number of Heats")
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.show()
