# AI-Based Loan Approval Assistant

## Project title

AI-Based Loan Approval Assistant

## Problem statement

The project uses historical Lending Club loan data to predict the probability that a borrower will default on a loan. The system must help a lender triage applications using default risk rather than a direct historical approval label, because Lending Club data records repayment outcomes and does not provide a clean binary approval target that matches a future lending decision.

## Solution

The project follows a standard ML workflow: local raw data is filtered, cleaned, and feature engineered; models are trained with class imbalance handling; the best model is stored for inference; default probability is converted into a recommendation using configurable threshold logic; SHAP explains the prediction; fairness is audited across groups; and a Streamlit dashboard presents the results.

## Architecture

```text
RAW DATA
  ↓
FILTERING
  ↓
CLEANING / FEATURE ENGINEERING
  ↓
TRAIN / VALIDATION / TEST SPLIT
  ↓
PREPROCESSING PIPELINE
  ↓
MODEL
  ↓
DEFAULT PROBABILITY
  ↓
DECISION ENGINE
  ↓
SHAP
  ↓
STREAMLIT
```

## Dataset information

This project uses the Lending Club dataset from Kaggle, consisting of historical loan records with financial, credit, and repayment metadata. The ML target is `default_flag`, where:

- `0` = Fully Paid
- `1` = Charged Off

The model predicts default risk, not whether a loan was historically approved.

## Why dataset is not stored in GitHub

The raw Lending Club CSV is intentionally excluded from GitHub because it is large and is not part of the code repository. This repository keeps only the folder structure and scripts needed to work with the local dataset.

## How to download the dataset

1. Visit the Kaggle Lending Club dataset page.
2. Download the CSV file locally.
3. Place it at:
   `data/raw/loan_data.csv`
4. Keep the file on your local machine and do not commit it to GitHub.

## Required file location

The project expects the local CSV at:

```text
data/raw/loan_data.csv
```

## Installation instructions

```bash
python -m pip install -r requirements.txt
```

## Data pipeline commands

```bash
python src/data/filter_sample.py
python src/data/clean.py
```

## Model training commands

```bash
python src/model/train.py
python src/model/evaluate.py
```

## Streamlit command

```bash
streamlit run app/app.py
```

## Folder structure

```text
AI-BASED-LOAN-APPROVAL-ASSISTANT/
├── app/
│   ├── app.py
│   ├── components/
│   └── pages/
├── data/
│   ├── raw/
│   ├── interim/
│   └── processed/
├── models/
├── notebooks/
├── reports/
│   ├── figures/
│   └── metrics/
├── src/
│   ├── data/
│   ├── explainability/
│   ├── fairness/
│   ├── model/
│   └── __init__.py
├── tests/
├── .gitignore
├── README.md
├── requirements.txt
└── .gitkeep
```

## Team responsibilities

- Data pipeline: filter and clean raw Lending Club data.
- Model training: train and compare candidate classifiers.
- Explainability: SHAP analysis for individual decisions.
- Fairness: test for disparities across groups.
- Dashboard: Streamlit assessment and reporting experience.

## ML methodology

The project uses a binary classification target (`default_flag`). Candidate models include logistic regression, random forest, and XGBoost. Training uses a stratified train/test split, and model comparison focuses on default recall, false approvals, and ROC-AUC rather than accuracy alone.

## SHAP methodology

SHAP values quantify how each feature pushes a prediction toward or away from default risk. The app and explainability utilities use actual model outputs to identify the features most responsible for a given applicant's risk score.

## Fairness methodology

Fairness is evaluated on the same held-out test dataset by comparing performance across groups using the same predictions. The code is generic and accepts `y_true`, `y_pred`, and `group_labels`. This is an audit for potential disparities, not a claim of fairness.

## Limitations

- The raw Kaggle CSV is not stored in the repository and must be downloaded locally.
- Historical default data may contain survivorship or sampling biases.
- Labeling and outcomes are based on historical repayment behavior rather than a direct approval decision.
- Thresholds are starting values and should be reviewed by domain stakeholders before production use.

## Future improvements

- Add a richer applicant profile form and validation rules.
- Tune risk thresholds using business objectives and cost trade-offs.
- Expand fairness analysis with additional protected attributes where valid and lawful.
- Move the model artifact and metrics to a deployment-ready pipeline.

---

## Data pipeline notes

The repository preserves the existing Day-1 and Day-2 scripts:

```bash
python src/data/filter_sample.py
python src/data/clean.py
```

These scripts must run against the local raw file at `data/raw/loan_data.csv` and generate output in `data/interim/` and `data/processed/` respectively.

## Important disclaimer

This project does not claim to directly predict historical Lending Club approval decisions. The model predicts default probability, and then a separate decision engine converts that probability into `APPROVE`, `MANUAL REVIEW`, or `REJECT`.

│ └── exploratory_analysis.ipynb
│
├── src/
│ ├── preprocessing.py
│ ├── train_model.py
│ ├── predict.py
│ ├── explain.py
│ └── fairness.py
│
├── models/
│ └── loan_model.pkl
│
├── app.py
├── requirements.txt
└── README.md

````

---

## 🚀 Installation

Clone the repository:

```bash
git clone <repository-url>
cd loan-approval-ai
````

Create a virtual environment:

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## ▶️ Running the Project

### Train the model

```bash
python src/train_model.py
```

### Run the Streamlit application

```bash
streamlit run app.py
```

The application will open in your browser.

---

## 📈 Expected Results

The project aims to develop a model with strong performance on:

- **Precision**
- **Recall**
- **F1-score**
- **ROC-AUC**

A target of approximately **0.80+** can be used as a project benchmark, while reporting the actual test-set performance.

Particular attention will be given to **false approvals**, since incorrectly approving a high-risk borrower can result in financial losses.

---

## 🔐 Important Consideration: Data Leakage

Only information that would reasonably be available **at the time of loan assessment** should be used as model input.

Features that become available after the loan is issued, such as later payment information or recovery amounts, should not be used for prediction.

This prevents the model from learning from information that would not actually be available when making a loan decision.

---

## 🔮 Future Enhancements

- Real-time credit-risk assessment.
- Cost-sensitive decision thresholds.
- More advanced fairness mitigation techniques.
- Integration with external credit-data APIs.
- Applicant-facing explanation reports.
- Model monitoring and drift detection.
- Automated model retraining.
- Cloud deployment.
- Authentication and role-based access for loan officers.

---

## 👥 Project Focus

This project combines:

**Machine Learning + Explainable AI + Responsible AI + Web Application**

The final goal is not to replace human loan officers, but to provide an **AI-assisted decision-support system** that helps them assess applicants consistently while understanding the reasoning and potential fairness implications behind each recommendation.
