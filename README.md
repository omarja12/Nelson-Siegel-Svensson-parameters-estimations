# Curve Lab

## Nelson-Siegel-Svensson parameter estimation

Curve Lab is a compact computational-finance project that estimates smooth yield curves from a small set of observed market rates. It uses the Nelson-Siegel-Svensson (NSS) model to describe the level, slope, and curvature of the term structure across five dated snapshots from 2020.

The project started as an individual computational-finance assignment and is preserved as an intentionally old, reproducible research artifact. The original data file and notebook remain in the repository; the portfolio page and standalone script make the work easier to explore today.

## Explore the project

Open [index.html](index.html) in a browser, or serve the repository locally:

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
| [script.js](script.js) | Browser curve explorer and date selector |
| [Nelson_Siegel_Svensson_parameters_estimations.py](Nelson_Siegel_Svensson_parameters_estimations.py) | Standalone Python translation of the notebook workflow |
| [Nelson_Siegel_Svensson_parameters_estimations.ipynb](Nelson_Siegel_Svensson_parameters_estimations.ipynb) | Original analysis notebook |
| [ha_cf_2021.py](ha_cf_2021.py) | Original dated market data |

## Historical note

The source artifacts are kept intact for provenance. The observations are from September and October 2020, while the repository history begins in August 2022. The portfolio page is a presentation layer around that work, not a replacement for the original notebook or data.

## License

See [LICENSE](LICENSE).
