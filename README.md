# 💳 FinElite

An AI-powered credit card limit prediction and risk analytics app built with Python and Streamlit. This project brings machine learning straight to retail banking, taking customer finances, credit scores, and repayment histories to recommend smart, personalized credit limits while keeping default risks low.
Under the hood, it relies on a classic data science stack**Pandas** and **NumPy** for data cleaning and building custom features, **Scikit-learn** for predictive modeling, and a mix of **Plotly**, **Matplotlib**, and **Seaborn** to turn complex portfolio metrics and real-time predictions into clean, interactive visuals.

---

## 🌟 Key Dashboard Features

This dashboard suite is structured into three dedicated analytical views, allowing users to explore customer financial health, behavior, and credit risk from different perspectives:

### 1. Customer Spending & Behaviour Analysis
Deep-dive into customer-level transaction patterns and demographic habits.
* **Dynamic Spending Slicing:** Compare spending patterns across age cohorts, gender, employment type, and KYC status using bar, box, or violin plots.
* **Income vs. Spending Matrix:** Interactive scatter plot mapping spending against income, sized by credit limit and color-coded by credit score.
* **Top Spender Leaderboard:** Isolate top high-spending customers and analyze transaction frequency across different employment groups.
* **Automated Behavioral Flags:** Generate instant alerts for high-spending age brackets and accounts exceeding 70% credit utilization.

### 2. Financial Performance & Balance Sheet View
Evaluate customer asset health, debt burdens, and wealth indicators.
* **Executive Financial KPIs:** High-level summary of portfolio-wide income, total savings, investment volumes, and debt-to-income (DTI) metrics.
* **Multi-Factor Financial Slicer:** Dynamically switch between EMI obligations, DTI ratios, savings balances, and investments to observe group spending behavior.
* **Debt & Utilization Matrix:** Correlation scatter plot mapping credit limits against utilization rates and credit scores.
* **Occupational Financial Profiling:** Benchmark top 10 occupations against savings, investment capacity, and monthly EMIs.

### 3. Credit Risk & Decision Intelligence
Monitor default indicators and assess customer risk exposure in real time.
* **Portfolio Risk Metrics:** Track default rates, defaulter counts, average late payments, and high-risk cohort exposures.
* **Default Drivers Breakdown:** Visualize default distributions by demographic age groups and specific occupation segments.
* **Feature Correlation Engine:** Rank numerical factors that correlate most strongly with customer loan defaults.
* **Underwriter Risk Simulator:** Real-time interactive scoring tool to instantly classify new applicants as Standard or High Risk based on credit score, utilization, and missed payments.

---

## 🛠️ Tech Stack

### **Core Stack**
![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)

### **Visualization Stack**
![Plotly](https://img.shields.io/badge/Plotly-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)
![Matplotlib](https://img.shields.io/badge/Matplotlib-11557C?style=for-the-badge&logo=python&logoColor=white)
![Seaborn](https://img.shields.io/badge/Seaborn-3776AB?style=for-the-badge&logo=python&logoColor=white)

---

### **Detailed Breakdown**

* **Core Language:** `Python` — Powers backend data processing logic, analytical aggregations, and predictive features.
* **Dashboard Framework:** `Streamlit` — Drives the multi-page interactive web application, filter controls, and risk simulation tools.
* **Data Manipulation:** `Pandas` & `NumPy` — Handles data cleansing, cohort binning, summary stats, and group matrix operations.
* **Data Visualization:** `Plotly`, `Matplotlib`, `Seaborn` — Produces dynamic charts, distribution box plots, and risk correlation visuals.

---

## 📁 Project Structure

```text
.
├── Datasets/                               # Contains raw data files
│   └── Credir_Card_Bank.xlsx               
├── notebooks/                              # Jupyter notebooks for exploration & reporting
│   └── credit_card_eda.ipynb               
├── pages/                                  # Multi-page dashboard modules
│   ├── 1_📈_Customer_&_Spending.py        
│   ├── 2_💰_Financial_Analysis.py          
│   └── 3_🛡️_Risk_Analytics.py              
├── Dashboard.py                            # Main Streamlit application entry point
├── requirements.txt                        # Project dependencies
└── README.md                               # Project documentation
```

## 🚀 **Getting Started**

Follow these instructions to set up and run the project on your local machine.

### Prerequisites
* Python 3.8 or higher
* Git

---

### Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/your-username/credit-card-bank-analytics.git](https://github.com/your-username/credit-card-bank-analytics.git)
   cd credit-card-bank-analytics
   ```

2. **Create and activate a virtual environment (recommended):**

   * **Windows:**
     ```bash
     python -m venv venv
     venv\Scripts\activate
     ```

   * **macOS / Linux:**
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. **Install the required dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Streamlit application:**
   ```bash
   streamlit run Dashboard.py
   ```

5. **Access the Dashboard:**  
   Open your web browser and navigate to `http://localhost:8501`.
