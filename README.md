# Curve Lab

## Nelson-Siegel-Svensson parameter estimation

Curve Lab is a compact computational-finance project that estimates smooth yield curves from a small set of observed market rates. It uses the Nelson-Siegel-Svensson (NSS) model to describe the level, slope, and curvature of the term structure across five dated snapshots from 2020.

The repository preserves the original data file and notebook as a reproducible research artifact, while the portfolio page and standalone script present the workflow as a focused fixed-income analytics case study.

## Explore the project

Open [index.html](index.html) in a browser, or read the theory in the dedicated [numerical methods page](notes.html). You can serve the repository locally:

```powershell
python -m http.server 4173
```

Then visit `http://localhost:4173` to explore the interactive curve visualizer.

The live portfolio page is published at [omarja12.github.io/Nelson-Siegel-Svensson-parameters-estimations](https://omarja12.github.io/Nelson-Siegel-Svensson-parameters-estimations/). GitHub Pages deploys automatically from `main` through [the Pages workflow](.github/workflows/pages.yml).

## What it demonstrates

- Builds a pandas DataFrame from 15 observed tenors, from 3M through 30Y.
- Converts quoted tenors into year fractions.
- Estimates six NSS parameters for each market date with `scipy.optimize.minimize`.
- Plots observed market rates alongside fitted NSS curves.
- Interpolates rates for 9M, 3.5Y, 12.5Y, and 25Y.
- Tracks selected tenor rates through time.
- Implements Act/360 and Act/365 day-count conventions.
- Discounts a future payment using annual compounding.

## Theory

### Why model a yield curve?

A yield curve maps the maturity of a fixed-income instrument to its yield. Market data rarely provides a quote for every possible maturity, so a model is useful for producing a continuous curve from a finite set of observations. A good curve should remain interpretable, behave smoothly between observations, and provide sensible values at maturities that were not directly quoted.

This project uses maturities ranging from three months to thirty years. The observed data is represented as a set of pairs $(t_i, y_i)$, where $t_i$ is the maturity in years and $y_i$ is the corresponding market yield.

### Nelson-Siegel-Svensson model

The Nelson-Siegel-Svensson model represents the yield at maturity $t$ as a weighted combination of level, slope, and curvature factors:

$$
y(t) = \beta_0 + \beta_1 L_1(t; \tau_1) + \beta_2 L_2(t; \tau_1) + \beta_3 L_3(t; \tau_2)
$$

The loading functions used by the implementation are:

$$
L_1(t; \tau_1) = \frac{1 - e^{-t/\tau_1}}{t/\tau_1}
$$

$$
L_2(t; \tau_1) = \frac{1 - e^{-t/\tau_1}}{t/\tau_1} - e^{-t/\tau_1}
$$

$$
L_3(t; \tau_2) = \frac{1 - e^{-t/\tau_2}}{t/\tau_2} - e^{-t/\tau_2}
$$

The six parameters have distinct roles:

| Parameter | Interpretation | Effect on the curve |
| --- | --- | --- |
| $\beta_0$ | Long-run level | Controls the long-maturity yield as the other loadings decay. |
| $\beta_1$ | Short-term slope | Drives the difference between short and long maturities. |
| $\beta_2$ | First curvature factor | Adds a hump or dip at shorter and medium maturities. |
| $\beta_3$ | Second curvature factor | Adds a second hump or dip at a different maturity range. |
| $\tau_1$ | First decay constant | Controls where the first slope/curvature effects fade. |
| $\tau_2$ | Second decay constant | Controls where the second curvature effect fades. |

As $t$ becomes large, the exponential terms approach zero, so the curve approaches the level parameter $\beta_0$. This gives the model a useful economic interpretation while allowing enough flexibility to fit more than one hump.

### Calibration by least squares

For each date, the notebook starts with an initial parameter vector

$$
p_0 = (1, 1, 1, 1, 1, 1)
$$

and minimizes the sum of squared differences between the model and the observed yields:

$$
\mathrm{SSE}(p) = \sum_{i=1}^{n} \left[y(t_i; p) - y_i\right]^2
$$

The fitted vector $p$ contains $(\beta_0, \beta_1, \beta_2, \beta_3, \tau_1, \tau_2)$. The implementation uses `scipy.optimize.minimize` independently for each of the five market dates. Once calibrated, the same function $y(t; p)$ can evaluate the curve at any positive maturity, including the synthetic tenors used in the project.

#### What least squares is doing

For a candidate parameter vector $p$, the model produces a fitted yield $\widehat{y}_i = y(t_i; p)$ at every observed maturity. The difference between the market observation and the fitted value is the residual:

$$
e_i = y_i - \widehat{y}_i
$$

The optimizer chooses the parameters that make the total squared residual as small as possible:

$$
\widehat{p} = \arg\min_p \mathrm{SSE}(p)
$$

Squaring makes positive and negative errors contribute equally and penalizes large misses more heavily. The resulting curve is therefore the NSS curve with the smallest total squared deviation from the 15 observed rates, according to this objective. This is a calibration criterion, not a claim that the observations are noise-free or that the model is economically true.

The NSS calibration is nonlinear because $\tau_1$ and $\tau_2$ appear inside exponential functions. `scipy.optimize.minimize` searches the parameter space from the initial guess, evaluates the SSE repeatedly, and returns the parameter vector found at the minimum. Different starting values or parameter constraints can lead to different local solutions, which is why a production implementation would normally add bounds, diagnostics, convergence checks, and sensitivity tests.

This is a direct unweighted least-squares calibration rather than a production pricing curve. It gives every quoted tenor the same influence, even though market instruments may differ in liquidity, price precision, and risk. It also fits yields directly instead of fitting discount factors or zero-coupon prices. Natural extensions for a market-grade implementation include weighted least squares, parameter bounds such as $\tau_1,\tau_2 > 0$, robust error diagnostics, and instrument-level cash-flow pricing.

### Interpolation and curve evolution

The model is used to estimate rates at 9M, 3.5Y, 12.5Y, and 25Y. These maturities are not all present in the source quotes. Instead of drawing a straight line between two neighboring observations, the project evaluates the calibrated NSS function at each requested maturity. This preserves the model's level, slope, and curvature assumptions:

$$
\widehat{y}(t_s) = y(t_s; \widehat{p})
$$

Here $t_s$ is the selected maturity and $\widehat{p}$ is the parameter vector estimated for that date. For example, the 9M estimate is obtained by converting 9M to $0.75$ years and evaluating $y(0.75; \widehat{p})$. Repeating this calculation for every date creates a time series for each selected maturity. Comparing those series shows how the term structure moved during the archived observation window.

This is interpolation when $t_s$ lies inside the quoted range and model-based extrapolation when it lies beyond the available quotes. The 25Y estimate is an interpolation between the 20Y and 30Y observations; a request beyond 30Y would be an extrapolation and should be treated with more caution.

### Day-count fractions

An actual-day convention expresses the time between two dates as a fraction of a chosen denominator. For start date $d_s$ and end date $d_e$:

$$
\mathrm{DCF}_{\text{Act/360}} = \frac{\mathrm{days}(d_s, d_e)}{360}
$$

$$
\mathrm{DCF}_{\text{Act/365}} = \frac{\mathrm{days}(d_s, d_e)}{365}
$$

The denominator changes the year fraction and therefore changes interest accrual or discounting. For the example dates 15-06-2020 and 15-12-2021, the elapsed 548 days gives approximately $1.5222$ under Act/360 and $1.5014$ under Act/365. The Python implementation parses dates in `DD-MM-YYYY` format and supports both conventions explicitly.

### Present value

For a future cash flow $FV$, an annual effective rate $r$, and a maturity of $T$ years, the annually compounded present value is:

$$
PV = \frac{FV}{(1+r)^T}
$$

For the project example, $FV = 2430.04$, $r = 0.05$, and $T = 5$, so:

$$
PV = \frac{2430.04}{(1.05)^5} \approx 1904.00
$$

The result is lower than the future payment because money received later is worth less than money held today when the discount rate is positive. In a full fixed-income valuation, the rate would normally be consistent with the instrument's compounding convention, day-count basis, and payment schedule. A complete bond price would discount each coupon and principal cash flow separately rather than treating the investment as one payment.

### Practical limitations

This repository is an educational and portfolio artifact, not investment advice or a live market-data service. The input rates are hard-coded historical observations, the calibration is unweighted, and the fitted parameters are not persisted as a separate output file. The notebook and standalone script are intentionally transparent so the full calculation can be inspected and rerun.

## Run the Python version

Create a virtual environment if desired, then install the analytical dependencies:

```powershell
python -m pip install numpy pandas matplotlib scipy
```

Run the standalone version:

```powershell
python Nelson_Siegel_Svensson_parameters_estimations.py
```

The script prints the source market data, fitted parameters, interpolated rates, day-count examples, and present-value example. It also opens the curve plots when run in an environment with a graphical backend.

## Files

| File | Purpose |
| --- | --- |
| [index.html](index.html) | Portfolio-facing interactive project page |
| [styles.css](styles.css) | Responsive visual design for the project page |
| [landing.css](landing.css) | NSS model section styling for the landing page |
| [notes-link.css](notes-link.css) | Prominent project-notes link styling |
| [script.js](script.js) | Browser curve explorer and date selector |
| [favicon.svg](favicon.svg) | Curve Lab browser tab icon |
| [notes.html](notes.html) | Web version of the numerical methods and theory |
| [notes.css](notes.css) | Responsive styling for the numerical methods page |
| [Nelson_Siegel_Svensson_parameters_estimations.py](Nelson_Siegel_Svensson_parameters_estimations.py) | Standalone Python translation of the notebook workflow |
| [Nelson_Siegel_Svensson_parameters_estimations.ipynb](Nelson_Siegel_Svensson_parameters_estimations.ipynb) | Original analysis notebook |
| [ha_cf_2021.py](ha_cf_2021.py) | Original dated market data |

## Historical note

The source artifacts are kept intact for provenance. The observations span June through October 2020, while the repository history begins in August 2022. The portfolio page is a presentation layer around that work, not a replacement for the original notebook or data.

## License

See [LICENSE](LICENSE).
