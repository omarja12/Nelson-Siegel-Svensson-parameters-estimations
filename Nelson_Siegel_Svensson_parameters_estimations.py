"""Standalone Python version of the original NSS estimation notebook.

The source data remains in ha_cf_2021.py and is intentionally preserved.
"""

from datetime import datetime, timedelta
import re

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.optimize import minimize

from ha_cf_2021 import data, dates, tenors


pd.set_option("display.precision", 4)
COLORS = ["black", "red", "green", "blue", "darkgrey"]


def year_fraction(tenor):
    """Convert a tenor such as 9M or 3.5Y into years."""
    value = float(re.findall(r"\d+\.?\d*", tenor)[0])
    if "M" in tenor:
        return value / 12.0
    if "Y" in tenor:
        return value
    raise ValueError(f"Unsupported tenor: {tenor}")


def nss(parameters, term):
    """Evaluate the six-parameter Nelson-Siegel-Svensson curve."""
    beta0, beta1, beta2, beta3, tau1, tau2 = parameters
    first_loading = (1 - np.exp(-term / tau1)) / (term / tau1)
    second_loading = first_loading - np.exp(-term / tau1)
    third_loading = (1 - np.exp(-term / tau2)) / (term / tau2)
    return beta0 + beta1 * first_loading + beta2 * second_loading + beta3 * (
        third_loading - np.exp(-term / tau2)
    )


def error(parameters, terms, yields):
    """Return the sum of squared errors used by the optimizer."""
    return ((nss(parameters, terms) - yields) ** 2).sum()


def day_count(start_date, end_date, convention):
    """Return an actual-day fraction using Act/360 or Act/365."""
    start = datetime.strptime(start_date, "%d-%m-%Y")
    end = datetime.strptime(end_date, "%d-%m-%Y")
    if convention == "Act/360":
        return (end - start).days / 360.0
    if convention == "Act/365":
        return (end - start).days / 365.0
    raise ValueError("Convention must be Act/360 or Act/365")


def present_value(amount, rate, maturity):
    """Discount a future payment with an annually compounded rate."""
    return amount / (1 + rate) ** maturity


def build_market_data():
    return pd.DataFrame(data=np.array(data).T, index=tenors, columns=dates)


def estimate_parameters(market_data):
    terms = market_data.index.map(year_fraction).values
    initial_guess = np.array([1, 1, 1, 1, 1, 1])
    parameters = pd.DataFrame(
        columns=market_data.columns,
        index=["beta0", "beta1", "beta2", "beta3", "tau1", "tau2"],
    )
    for column in market_data.columns:
        parameters[column] = minimize(
            error, initial_guess, args=(terms, market_data[column].values)
        )["x"]
    return parameters


def interpolate_tenors(parameters):
    requested_tenors = ["9M", "3.5Y", "12.5Y", "25Y"]
    terms = [year_fraction(tenor) for tenor in requested_tenors]
    return pd.DataFrame(
        {
            column: nss(parameters[column].values, terms)
            for column in parameters.columns
        },
        index=requested_tenors,
    )


def plot_curves(market_data, parameters):
    terms = market_data.index.map(year_fraction).values
    curve_terms = np.linspace(0.25, 30, 100)
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    for index, column in enumerate(market_data.columns):
        axes[0].plot(
            terms,
            market_data[column].values,
            marker="o",
            color=COLORS[index],
            label=column,
        )
        axes[0].plot(
            curve_terms,
            nss(parameters[column].values, curve_terms),
            color=COLORS[index],
            alpha=0.55,
        )
    axes[0].set_title("Observed and fitted yield curves")
    axes[0].set_xlabel("Residual maturity in years")
    axes[0].set_ylabel("Yield")
    axes[0].grid(alpha=0.3)
    axes[0].legend()

    interpolated = interpolate_tenors(parameters).T.iloc[::-1]
    interpolated.plot(ax=axes[1], marker="o", grid=True)
    axes[1].set_title("Selected tenor evolution")
    axes[1].set_xlabel("Date")
    axes[1].set_ylabel("Yield")
    fig.tight_layout()
    return fig


def main(show_plot=True):
    market_data = build_market_data()
    parameters = estimate_parameters(market_data)
    selected_rates = interpolate_tenors(parameters)

    print("Market data:")
    print(market_data)
    print("\nNSS parameters:")
    print(parameters)
    print("\nInterpolated rates:")
    print(selected_rates)

    fraction_360 = day_count("15-06-2020", "15-12-2021", "Act/360")
    fraction_365 = day_count("15-06-2020", "15-12-2021", "Act/365")
    print(f"\nAct/360: {fraction_360:.4f}")
    print(f"Act/365: {fraction_365:.4f}")
    print(f"PV: EUR {present_value(2430.04, 0.05, 5):.4f}")

    if show_plot:
        plot_curves(market_data, parameters)
        plt.show()
    return market_data, parameters, selected_rates


if __name__ == "__main__":
    main()
