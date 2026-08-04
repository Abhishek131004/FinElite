## Credit Card Bank Data Analysis

A comprehensive Exploratory Data Analysis (EDA) of credit card bank customer data using Python, Pandas, Seaborn, and Matplotlib. This project investigates key financial indicators, customer risk profiles, demographic trends, and the drivers behind credit limit allocations.

## 📑 Table of Contents
1. [Project Overview](#-project-overview)
2. [Dataset Structure](#-dataset-structure)
3. [Key Features & Feature Engineering](#-key-features--feature-engineering)
4. [Analysis Architecture](#-analysis-architecture)
5. [Key Findings & Portfolio Insights](#-key-findings--portfolio-insights)
6. [Requirements & Setup](#-requirements--setup)

## 📌 Project Overview

Understanding credit limit allocation and customer risk profiles is vital for risk mitigation and financial product structuring in retail banking. This analysis performs structured data exploration on bank customer records to identify:

Key predictors of Credit Limit (e.g., Annual Income, Credit Score, Debt-to-Income Ratio).

Customer demographic segmentation based on age, occupation, and income tiers.

Behavioral risk markers linked to default rates, missed payments, and fraud flags.

## 📊 Dataset Structure

The raw dataset comprises financial metrics, demographic profiles, verification indicators, and historical credit behavior:

| Category | Attributes |
| :--- | :--- |
| **Identifiers & Demographics** | `Customer_ID`, `Age`, `Gender`, `Occupation`, `Employment_Type`, `Residential_Status` |
| **Financial Metrics** | `Annual_Income`, `Savings_Balance`, `Investment_Value`, `EMI_Per_Month`, `Debt_To_Income_Ratio`, `Avg_Monthly_Spending` |
| **Credit Profile** | `Credit_Score`, `Credit_Limit`, `Credit_Utilization`, `Existing_Credit_Cards`, `Years_With_Bank` |
| **Risk & Compliance** | `Missed_Payments`, `Number_of_Defaults`, `Fraud_Flag`, `PAN_Verified`, `KYC_Status` |

## 🛠️ Key Features & Feature Engineering

To perform group-level benchmarking, custom binning logic was applied across numerical features:

### 1. Income Segmentation (`Income_Group`)
* **Low Income:** < ₹3,00,000 (< ₹3 Lakhs)
* **Lower Middle:** ₹3,00,000 – ₹5,99,999 (₹3L – ₹6L)
* **Middle Income:** ₹6,00,000 – ₹9,99,999 (₹6L – ₹10L)
* **Upper Middle:** ₹10,00,000 – ₹14,99,999 (₹10L – ₹15L)
* **High Income:** $\ge$ ₹15,00,000 ($\ge$ ₹15 Lakhs)

### 2. Credit Score Tiering (`Credit_Score_Category`)
* **Excellent:** $\ge$ 800
* **Very Good:** 750 – 799
* **Good:** 700 – 749
* **Fair:** 650 – 699
* **Poor:** 550 – 649
* **Very Poor:** < 550
  
## 🔄 Analysis Architecture

## Phase 1: Data Ingestion & Structural Integrity Audit

The pipeline begins by loading the Credir_Card_Bank.xlsx file into a Pandas DataFrame. Before performing statistical evaluations, the system conducts foundational health checks:

Schema Verification: Audits column names and confirms expected data types (integers, floats, and strings).

Missing Value Identification: Scans all attributes using explicit null checks (isnull().sum()) to quantify missingness across financial records.

Deduplication: Evaluates row-level uniqueness (duplicated().sum()) to ensure no duplicated customer profiles bias downstream aggregations.

## Phase 2: Univariate Statistical Audit

Once data cleanliness is verified, the pipeline generates parametric and non-parametric summary metrics across all variables:

Central Tendency: Calculates mean, median, and mode across numerical features to evaluate central distributions and detect global skewness.

Dispersion & Spread: Measures variance (var()) and standard deviation (std()) alongside summary percentiles (describe()) to assess the spread of financial attributes like Annual_Income, Savings_Balance, and Credit_Limit.

Categorical Profiling: Evaluates object types to count unique values, top occurrences, and frequency counts across non-numeric variables.

## Phase 3: Feature Domain Engineering & Binning Logic

To enable meaningful cohort analysis, raw continuous variables are transformed into categorical domain tiers using explicit helper functions:

Income Tiering (Income_Group): Bins Annual_Income into five economic brackets ranging from Low Income (< 300k) up to High Income (>= 1.5M).

Credit Rating Categorization (Credit_Score_Category): Maps numerical FICO/credit scores to industry-standard rating tiers ranging from Very Poor (< 550) to Excellent (>= 800).

Demographic Cohort Generation (Age_Group): Bins age values into five structured life-stage brackets (18-24, 25-34, 35-44, 45-54, 55+).

## Phase 4: Bivariate Analysis & Relationship Mining

This phase explores interactions between variables to understand what influences credit allocation and default risk:

Correlation Matrices: Computes pairwise Pearson correlation coefficients between Credit_Limit and numerical parameters (Annual_Income, Credit_Score, EMI_Per_Month, Debt_To_Income_Ratio, Credit_Utilization, and bank tenure).

Demographic Cross-Tabulations: Groups financial metrics by Occupation, Employment_Type, Residential_Status, and Gender to evaluate income and credit variance across sub-populations.

Risk Behavior Evaluation: Cross-examines behavioral markers—such as Missed_Payments and Number_of_Defaults—against credit scores, debt ratios, and credit line allocations.

## Phase 5: Synthesis, Compliance, & Portfolio Insights

The final stage isolates top performers, checks compliance flags, and synthesizes key insights:

High-Value Customer Analysis: Extracts top customer segments (nlargest()) ranked by highest credit limits, savings balances, and investment portfolios.

Compliance & Fraud Profiling: Evaluates how verification statuses (PAN_Verified, KYC_Status) and system flags (Fraud_Flag) correlate with default rates and credit line adjustments.

Global Ranking: Ranks all numeric attributes by their correlation strength against Credit_Limit to pinpoint primary decision drivers for bank underwriting models.

## 💡 Key Findings & Observations

## 1. Credit Limit Allocation DriversPrimary Underwriting DeterminantsAnnual Income as the Core Pillar: 
-The correlation between Annual_Income and Credit_Limit reveals that income tier is the strongest determinant for line assignment. 

-Credit Score Tier Segmentation:Customers in Excellent (>= 800) and Very Good (750-799) tiers receive significantly higher average credit limits compared to Fair or Poor tiers.

-The aggregation matrix confirms that higher credit score bands show lower average Number_of_Defaults and Missed_Payments.
-Bank Relationship & Tenure: The correlation between Years_With_Bank and Credit_Limit alongside groupby("Years_With_Bank") demonstrates that bank loyalty and historical tenure yield gradual credit limit enhancements.


## 2. Customer Liquidity & Asset ExposureSavings & Investment Correlation: 
-Evaluating correlation metrics for Savings_Balance and Investment_Value against Credit_Limit shows that customers with larger liquid safety nets represent lower credit risk, justifying higher line assignments.

-Top 10 High-Net-Worth Profile: Isolating the top 10 customers by Credit_Limit and Savings_Balance shows a concentrated overlap in specific Occupation classes, demonstrating where the bank's total credit exposure is concentrated.

## 3. Debt Burden & Risk ProfilingDebt-to-Income (DTI) & Monthly ObligationsEMI vs. Credit Limit: 
-Analyzing EMI_Per_Month alongside Debt_To_Income_Ratio highlights customer leverage levels. High DTI ratios correlate inversely with credit score health.

-Credit Utilization Patterns: Evaluating Credit_Utilization provides insight into how heavily customers depend on their existing credit lines:High Utilization + High DTI: Signals over-leveraged borrowers who are vulnerable to missing payments.

-Low Utilization + High Credit Score: Represents prime candidates for credit line increases or cross-selling investment products.

-Default & Missed Payment Sorting: Sorting records by Number_of_Defaults and Missed_Payments isolates the highest-risk portfolio segment. These accounts show low credit scores combined with elevated debt ratios

## 4. Demographic & Occupational Profiling:
## 1. Occupational Profiling (Occupation)
Occupational grouping serves as a primary proxy for income stability, earning capacity, and cash-flow regularity.

Key Aggregations Analyzed: count, mean, min, max across Annual_Income, Credit_Score, Credit_Limit, Savings_Balance, Investment_Value, EMI_Per_Month, and Debt_To_Income_Ratio.

High-Earning Professionals (Corporate / Tech / Senior Roles):

Income & Credit Lines: Display the highest mean Annual_Income and Credit_Limit. These roles show high baseline liquidity (Savings_Balance) and investment capacity (Investment_Value).

Credit Score Stability: Maintain tight min-max spreads in Credit_Score, indicating consistent financial health and low volatility in repayment capability.

Variable-Income Roles (Freelancers / Small Business / Sales):

Spread & Volatility: Show significantly wider min-max variances in Annual_Income and Credit_Score.

Risk Cushioning: Higher volatility in monthly income leads banks to maintain more conservative average Credit_Limit caps relative to their peak income to mitigate sudden cash-flow shocks.

## 2. Life-Stage & Age Cohort Profiling (Age_Group)
Categorizing customers into life-stage brackets (18–24, 25–34, 35–44, 45–54, 55+) highlights clear financial lifecycle trends:

18–24 Cohort (Early Career / Entry Level):

Metrics: Lowest average Annual_Income, Credit_Limit, and Savings_Balance.

Risk Outlook: Lower average Credit_Score due to short credit histories (Years_With_Bank) rather than default behavior.

25–34 Cohort (Early Consolidation):

Metrics: Rising Avg_Monthly_Spending alongside growing Credit_Limit assignments.

Behavior: Increasing usage of credit lines for consumer lifestyle spending and early major loans (EMIs).

35–44 & 45–54 Cohorts (Peak Asset Accumulation & Wealth Phase):

Metrics: Peak performance across Annual_Income, Credit_Limit, Savings_Balance, and Investment_Value.

Risk Outlook: Highest average Credit_Score bands, driven by extended banking tenure and disciplined debt-to-income management.

55+ Cohort (Pre-Retirement / Maturity):

Metrics: High savings-to-spending ratios, moderate Avg_Monthly_Spending, and lower overall borrowing/debt obligations (EMI_Per_Month).

## 3. Employment Type Profiling (Employment_Type)
Evaluating customer records across Salaried vs. Self-Employed / Contractual profiles reveals distinct risk-reward trade-offs:

Salaried Individuals:

Predictable monthly income streams result in predictable cash flows.

Receive higher baseline Credit_Limit approvals at lower income thresholds due to lower perceived default risk.

Display stable Debt_To_Income_Ratio control.

Self-Employed Individuals:

Show higher average asset generation potential (Investment_Value), but face stricter debt-servicing scrutiny.

Banks adjust leverage boundaries (Credit_Limit) based on higher required liquid cushions (Savings_Balance).

## 4. Residential Status (Residential_Status)
Housing status provides strong context regarding fixed overhead costs, asset backing, and long-term residency stability:

Owns / Mortgage Holders:

Asset Backing: Higher mean Savings_Balance, Investment_Value, and higher baseline Credit_Score metrics.

Underwriting Preference: Mortgage holders and property owners present collateral/stability factors that justify higher extended credit lines.

Renters:

Display higher sensitivity to rising monthly fixed obligations (EMI_Per_Month to income ratio).

Require tighter monitoring of Credit_Utilization to prevent over-leveraging.

## 5. Gender-Based Financial Benchmarking (Gender)
Comparing Annual_Income, Credit_Score, and Credit_Limit across gender breakdowns provides an objective baseline audit:

Credit Score Parity: Credit_Score distribution remains uniform across genders, confirming that credit rating models are driven strictly by financial performance and repayment history.

Line Allocation: Average Credit_Limit scales proportionally with Annual_Income across all gender categories, keeping allocation parity strictly bound to risk metrics.
## 5. Compliance, Fraud, & Verification AuditFraud Flag Segmentation: 
-The aggregation on Fraud_Flag shows that flagged accounts exhibit significantly higher average Missed_Payments and Number_of_Defaults, alongside reduced credit limits.

-KYC & PAN Verification Impact: Accounts with completed KYC_Status and verified PAN_Verified maintain higher average credit scores and higher credit line allocations compared to unverified or pending accounts, confirming that identity verification reduces default risk.

-Primary Credit Limit Driver: Annual_Income exhibits a strong positive correlation with Credit_Limit, followed by Credit_Score and overall tenure with the bank (Years_With_Bank).

-Risk Indicator Divergence: High Debt_To_Income_Ratio and higher instances of Missed_Payments strongly align with lower credit score bands and elevated Number_of_Defaults.

-Compliance Correlation: Accounts with verified PAN and completed KYC_Status show higher average credit score benchmarks and higher credit limits. is this correct readme 

