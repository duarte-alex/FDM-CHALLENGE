import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import linregress


def plot_linear_fit(data: dict) -> None:
    for label, (x, y, color) in data.items():
        # Linear regression
        slope, intercept, r_value, _, _ = linregress(x, y)
        line_eq = f"{label} Fit: y = {slope:.2f}x + {intercept:.2f} (R = {r_value:.3f})"

        # Line for plotting
        x_fit = np.linspace(min(x), max(x), 100)
        y_fit = slope * x_fit + intercept

        # Plot
        plt.figure(figsize=(6, 4))
        plt.plot(x, y, "o", color=color, label="Data Points")
        plt.plot(x_fit, y_fit, "-", color=color, alpha=0.6, label="Linear Fit")
        plt.title(f"{label} - Linear Fit\n{line_eq}")
        plt.xlabel("Number of Heats")
        plt.ylabel("Tons Produced")
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.show()
