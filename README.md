# BPD risk calculator

Streamlit research calculator for the reported seven-input logistic regression model.
It applies the coefficients, imputation medians, scaling parameters and score tertiles
reported in Supplementary Table S5. The rounded function was checked against the
public-data reconstruction; it retains the historical model specification.

## Run

Python 3.11:

```sh
pip install -r requirements.txt
streamlit run app.py
```

For Streamlit Community Cloud, select the `main` branch and `app.py` entry point.

## Inputs and example

Inputs are birth weight, gestational-age category, maternal age, hypertensive disorder
of pregnancy (HDP), premature rupture of membranes (PROM), gestational diabetes
mellitus (GDM), and 5-minute Apgar score.

Gestational-age categories are 1: <28 weeks; 2: 28+0–31+6 weeks;
3: 32+0–33+6 weeks; and 4: 34+0–36+6 weeks.

The synthetic example (1,800 g, category 2, maternal age 28, HDP/PROM/GDM all 0,
Apgar 8) returns approximately 43.2%, in the intermediate development-score group.

## Scope

The model was developed from 1,958 public records and evaluated on 3,031 external
records with birth weight below 2,500 g. Score groups are development-score tertiles,
not clinical action thresholds. Combinations of unavailable inputs absent from the
development data trigger an extrapolation warning.

This is research software. Clinical utility and equivalence of source endpoints
have not been established. The application does not load patient datasets, save
input records, fit models, or recalibrate the reported model.

## Deployment files

- `app.py`: calculator interface and inference.
- `model_parameters.json`: aggregate reported parameters.
- `requirements.txt`: pinned Streamlit dependency.
- `README.md`: usage and provenance.
