# AI-Based Loan Approval Assistant

## React + FastAPI frontend

The full-stack application uses the existing Python/LightGBM/SHAP pipeline
through FastAPI:

```powershell
# Terminal 1: backend
python -m uvicorn backend.main:app --reload

# Terminal 2: frontend
cd frontend
npm install
npm run dev
```

The React app reads `VITE_API_URL`. During local development it defaults to
`http://localhost:8000`; production builds require `VITE_API_URL` to be set to
the public backend origin (for example, `https://loan-api.example.com`). The
assessment endpoint is `POST /api/assessment` and uses multipart form data.

For a backend host such as Render, use:

```text
Build command: pip install -r backend/requirements.txt
Start command: python -m uvicorn backend.main:app --host 0.0.0.0 --port $PORT
```

Set `CORS_ORIGINS` on the backend to the exact frontend origin(s), separated by
commas, for example `https://ai-loan-approval-assistant.in,https://your-app.vercel.app`.
The default configuration also permits Vercel preview origins through
`CORS_ORIGIN_REGEX`. Set that variable to a narrower regular expression when
preview access is not needed.

For the deployed frontend, set `VITE_API_URL` in its Vercel project settings,
then redeploy so Vite embeds the value into the static bundle. Do not include a
trailing slash. The backend must be deployed separately and its public URL is
the value to use; this repository does not contain a backend provider URL.

## 📌 Overview

The **AI-Based Loan Approval Assistant** is a Python-based machine learning project that helps make loan assessment more **consistent, explainable, and data-driven**.

The system uses historical **Lending Club loan data** to learn patterns between an applicant's financial profile and their loan repayment outcome. It predicts the **probability of loan default** and provides a recommendation such as **Approve, Manual Review, or Reject**.

Unlike a simple rule-based loan system, the project also explains **why** a particular applicant was considered risky or low-risk using **Explainable AI (SHAP/LIME)** techniques.

The project additionally performs a **fairness analysis** to identify potential differences in model performance across demographic groups.

---

## 🎯 Objectives

* Predict the probability of loan default.
* Reduce inconsistent manual loan assessment.
* Handle class imbalance in loan outcomes.
* Evaluate models using precision, recall, F1-score, and ROC-AUC.
* Explain individual loan predictions using SHAP/LIME.
* Analyze potential fairness issues across demographic groups.
* Provide an easy-to-use React web interface backed by FastAPI.

---

## 🔄 Project Workflow

```text
Lending Club Dataset
        ↓
Data Collection
        ↓
Data Cleaning & Preprocessing
        ↓
Feature Engineering
        ↓
Handle Class Imbalance
        ↓
Train Machine Learning Models
        ↓
Model Evaluation
        ↓
Select Best Model
        ↓
Default Risk Prediction
        ↓
SHAP/LIME Explanation
        ↓
Fairness Analysis
        ↓
React Dashboard
```

---

## 📊 Dataset

The project uses the **Lending Club loan dataset** available on Kaggle.

**Dataset:** Lending Club Loan Data
**Source:** Kaggle – wordsforthewise/lending-club

The dataset contains historical loan information such as:

* Annual income
* Loan amount
* Employment length
* Credit/FICO information
* Debt-to-income ratio
* Home ownership
* Loan purpose
* Credit history
* Loan status

### Target Variable

The `loan_status` column is processed to create the prediction target.

For the initial binary classification:

```text
Fully Paid    → 0
Charged Off   → 1
```

Where:

* `0` = Loan was fully paid
* `1` = Loan was charged off/defaulted

Other loan statuses such as `Current` need to be handled carefully because the final repayment outcome may not yet be known.

---

## 🧠 Machine Learning

Multiple machine learning algorithms can be evaluated:

### 1. Logistic Regression

Used as a baseline model because it is simple and relatively interpretable.

### 2. Random Forest

Used to capture nonlinear relationships between financial features.

### 3. LightGBM

Used as a powerful gradient-boosting model for structured/tabular data.

The models will be compared using:

* Precision
* Recall
* F1-score
* ROC-AUC
* Confusion Matrix

The final model will be selected based on performance and the project's focus on reducing costly **false approvals**.

---

## ⚖️ Class Imbalance

Loan default datasets commonly contain significantly more successfully repaid loans than defaulted loans.

For example:

```text
Fully Paid       85%
Charged Off      15%
```

This imbalance can cause a model to favor the majority class.

The project will investigate techniques such as:

* Class weighting
* SMOTE
* Oversampling/undersampling

The chosen technique will be evaluated based on its effect on minority-class recall and overall model performance.

---

## 🔍 Explainable AI

The project uses **SHAP and/or LIME** to explain individual predictions.

Instead of simply displaying:

```text
Loan Recommendation: REJECT
```

the system can provide:

```text
Default Probability: 72%

Factors increasing risk:
- High debt-to-income ratio
- Lower credit score
- Large loan amount

Factors reducing risk:
- Stable employment
- Strong repayment history
```

This makes the prediction easier for a loan officer or applicant to understand.

---

## ⚖️ Fairness Analysis

The system will evaluate whether model performance differs across relevant demographic groups.

Metrics may include:

* Precision
* Recall
* False-positive rate
* False-negative rate
* True-positive rate
* Approval/recommendation rates

The purpose is to identify potential disparities and understand whether the model requires further investigation or mitigation.

---

## 🖥️ React Dashboard

The final application will provide a simple interface where a user can enter applicant information.

### Example Input

```text
Annual Income       : ₹60,000
Loan Amount         : ₹5,00,000
Employment Length   : 5 years
Credit Score        : 720
Debt-to-Income      : 15%
Home Ownership      : RENT
Loan Purpose        : Personal
```

### Example Output

```text
-----------------------------------
       LOAN RISK ASSESSMENT
-----------------------------------

Default Probability : 18%
Risk Level          : LOW

Recommendation      : APPROVE

-----------------------------------
WHY?
-----------------------------------

Positive Factors:
✓ Good credit score
✓ Stable employment
✓ Manageable debt

Risk Factors:
! Relatively high loan amount
```

---

## 🛠️ Technologies

| Component            | Technology          |
| -------------------- | ------------------- |
| Programming Language | Python              |
| Data Processing      | Pandas, NumPy       |
| Visualization        | Matplotlib, Seaborn |
| Machine Learning     | Scikit-learn        |
| Gradient Boosting    | LightGBM             |
| Imbalance Handling   | imbalanced-learn    |
| Explainable AI       | SHAP / LIME         |
| Frontend             | React / Vite        |
| Backend API          | FastAPI / Uvicorn   |
| Model Storage        | Joblib              |

---

## 📁 Project Structure

```text
loan-approval-ai/
│
├── data/
│   └── accepted_2007_to_2018Q4.csv
│
├── notebooks/
│   └── exploratory_analysis.ipynb
│
├── src/
│   ├── preprocessing.py
│   ├── train_model.py
│   ├── predict.py
│   ├── explain.py
│   └── fairness.py
│
├── models/
│   └── loan_model.pkl
│
├── app.py
├── requirements.txt
└── README.md
```

---

## 🚀 Installation

Clone the repository:

```bash
git clone <repository-url>
cd loan-approval-ai
```

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

### Run the application

```bash
# Terminal 1
python -m uvicorn backend.main:app --reload

# Terminal 2
cd frontend
npm install
npm run dev
```

The frontend uses `VITE_API_URL` when set and defaults to `http://localhost:8000`.

---

## 📈 Expected Results

The project aims to develop a model with strong performance on:

* **Precision**
* **Recall**
* **F1-score**
* **ROC-AUC**

A target of approximately **0.80+** can be used as a project benchmark, while reporting the actual test-set performance.

Particular attention will be given to **false approvals**, since incorrectly approving a high-risk borrower can result in financial losses.

---

## 🔐 Important Consideration: Data Leakage

Only information that would reasonably be available **at the time of loan assessment** should be used as model input.

Features that become available after the loan is issued, such as later payment information or recovery amounts, should not be used for prediction.

This prevents the model from learning from information that would not actually be available when making a loan decision.

---

## 🔮 Future Enhancements

* Real-time credit-risk assessment.
* Cost-sensitive decision thresholds.
* More advanced fairness mitigation techniques.
* Integration with external credit-data APIs.
* Applicant-facing explanation reports.
* Model monitoring and drift detection.
* Automated model retraining.
* Cloud deployment.
* Authentication and role-based access for loan officers.

---

## 👥 Project Focus

This project combines:

**Machine Learning + Explainable AI + Responsible AI + Web Application**

The final goal is not to replace human loan officers, but to provide an **AI-assisted decision-support system** that helps them assess applicants consistently while understanding the reasoning and potential fairness implications behind each recommendation.
