## Credit Card Bank Data Analysis

A comprehensive Exploratory Data Analysis (EDA) of credit card bank customer data using Python, Pandas, Seaborn, and Matplotlib. This project investigates key financial indicators, customer risk profiles, demographic trends, and the drivers behind credit limit allocations.

## 📑 Table of Contents
1. [Project Overview](#-project-overview)
2. [Dataset Structure](#-dataset-structure)
3. [Key Features & Feature Engineering](#-key-features--feature-engineering)
4. [Analysis Architecture](#-analysis-architecture)
5. [Key Findings & Observations](#-key-findings--Observations)
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
## Phase 1: Ingestion & Structural Integrity Audit
The pipeline begins by ingesting customer records from Credir_Card_Bank.xlsx into a Pandas DataFrame (df) to establish data readiness before performing statistical computations.

Schema & Dtype Verification:

Checks structure using df.dtypes and df.columns to ensure numeric features (Annual_Income, Credit_Score, Credit_Limit, Savings_Balance, Investment_Value, EMI_Per_Month) are correctly registered as int64 or float64, and text fields (Occupation, Employment_Type, Residential_Status, KYC_Status) are parsed as object.

Missing Value Quantification:

Executes df.isnull().sum() across all columns to evaluate missingness and prevent null values from skewing aggregations or correlation metrics.

Deduplication Audit:

Evaluates row-level uniqueness using df.duplicated().sum() to verify that individual customer profiles (Customer_ID) are not duplicated, preventing artificial inflation of sample sizes.

## Phase 2: Univariate Statistical Audit

Once cleanliness is confirmed, the pipeline generates baseline parametric and non-parametric summary metrics to understand univariate distributions:

Central Tendency Analysis:

Computes parametric mean (df.mean(numeric_only=True)), non-parametric median (df.median(numeric_only=True)), and mode (df.mode().iloc[0]) across numerical features to evaluate central tendencies and identify distribution skewness (e.g., comparing mean vs. median for Annual_Income and Credit_Limit).

Dispersion & Distribution Spread:

Calculates variance (df.var(numeric_only=True)) and standard deviation (df.std(numeric_only=True)).

Generates five-number summaries via df.describe().T to inspect minimums, maximums, and interquartile ranges (25th, 50th, 75th percentiles) for liquid assets (Savings_Balance, Investment_Value) and debt parameters (EMI_Per_Month, Debt_To_Income_Ratio).

Categorical Feature Profiling:

Executes df.describe(include=object).T to audit string variables, extracting unique category counts (unique), dominant modal categories (top), and category frequencies (freq).

## Phase 3: Feature Domain Engineering & Binning Logic

To facilitate meaningful cohort analysis, raw continuous metrics are transformed into structured categorical tiers using Indian Rupee (₹) benchmarks:

Income Tiering (Income_Group):

Bins Annual_Income into 5 income brackets using the explicit function income_group:

Low Income: < ₹3,00,000 (< ₹3 Lakhs)

Lower Middle: ₹3,00,000 – ₹5,99,999 (₹3L – ₹6L)

Middle Income: ₹6,00,000 – ₹9,99,999 (₹6L – ₹10L)

Upper Middle: ₹10,00,000 – ₹14,99,999 (₹10L – ₹15L)

High Income: ≥ ₹15,00,000 (≥ ₹15 Lakhs)

Credit Score Tiering (Credit_Score_Category):

Maps numerical credit scores (Credit_Score) into standard credit rating tiers via score_category:

Excellent: ≥ 800

Very Good: 750 – 799

Good: 700 – 749

Fair: 650 – 699

Poor: 550 – 649

Very Poor: < 550

Demographic Cohort Generation (Age_Group):

Categorizes customer age (Age) into life-stage brackets via age_group:

18-24, 25-34, 35-44, 45-54, and 55+

## Phase 4: Bivariate Analysis & Relationship Mining

This phase explores multi-variable interactions to identify the primary drivers of credit line allocation and default risk:

Pairwise Pearson Correlation Analysis:

Computes pairwise correlation coefficients using .corr() to measure line relationship strengths against Credit_Limit:

Annual_Income vs. Credit_Limit

Credit_Score vs. Credit_Limit

Savings_Balance vs. Credit_Limit

Investment_Value vs. Credit_Limit

EMI_Per_Month vs. Credit_Limit

Debt_To_Income_Ratio vs. Credit_Limit

Credit_Utilization vs. Credit_Limit

Years_With_Bank vs. Credit_Limit

Visualizes correlation matrices using Seaborn heatmaps (sb.heatmap(..., annot=True, cmap='coolwarm')).

Demographic & Occupational Aggregations:

Occupational Benchmarking: Groups records by Occupation to measure statistical summaries (count, mean, min, max) for Annual_Income, Credit_Score, Credit_Limit, Savings_Balance, Investment_Value, EMI_Per_Month, and Debt_To_Income_Ratio.

Demographic Cross-Tabulations: Computes mean financial metrics across Age_Group, Employment_Type, Residential_Status, and Gender.

Risk Behavior Evaluation:

Evaluates interactions between credit scores, debt obligations, missed payments (Missed_Payments), and defaults (Number_of_Defaults) across binned credit tiers (Credit_Score_Category).

## Phase 5: Synthesis, Compliance, & Portfolio Insights

The final phase isolates high-value customer segments, assesses compliance markers, and ranks overall underwriting drivers:

High-Value Customer Isolation (nlargest):

Filters top 10 accounts ranked by Credit_Limit (df.nlargest(10, "Credit_Limit")) and Savings_Balance (df.nlargest(10, "Savings_Balance")) to identify concentration risk among high-net-worth customers.

High-Risk Portfolio Sorting:

Filters vulnerable accounts and sorts them by default severity (df.sort_values(by=["Number_of_Defaults", "Missed_Payments"], ascending=False)) to cross-check debt ratios against default occurrences.

Compliance & Verification Audits:

Evaluates mean Credit_Score and Credit_Limit across verification flags:

PAN_Verified (Verified vs. Unverified)

KYC_Status (Completed vs. Pending)

Fraud_Flag (Flagged vs. Clean)

Global Underwriting Driver Ranking:

Generates a global correlation ranking using df.corr(numeric_only=True)["Credit_Limit"].sort_values(ascending=False) to establish the definitive order of features influencing bank credit allocation decisions.

## 💡 Key Findings & Observations

## 💳 Credit Limit Allocation Drivers & Underwriting Determinants

Retail bank underwriting models rely on a combination of financial capacity, historical credit behavior, and customer retention metrics to establish initial credit lines and credit limit enhancements. The EDA reveals three foundational pillars driving the bank's credit allocation algorithm:

---

### 1. Income Segmentation vs. Credit Limit Baseline

`Annual_Income` exhibits the strongest positive correlation with `Credit_Limit`, confirming that gross earning capacity serves as the primary ceiling for total credit exposure. 

| Income Tier (`Income_Group`) | Annual Income Range (INR) | Mean Credit Limit | Underwriting Behavioral & Risk Insight |
| :--- | :--- | :--- | :--- |
| **Low Income** | `< ₹3,00,000` (< ₹3 Lakhs) | Entry-Level Baseline | Strict conservative caps to prevent early over-leveraging and debt overload. |
| **Lower Middle** | `₹3,00,000 – ₹5,99,999` (₹3L – ₹6L) | Moderate Allocation | Scaled credit lines matching regular monthly household expenditures. |
| **Middle Income** | `₹6,00,000 – ₹9,99,999` (₹6L – ₹10L) | Above-Average Allocation | Substantial credit buffer allowed for consumer lifestyle and travel spending. |
| **Upper Middle** | `₹10,00,000 – ₹14,99,999` (₹10L – ₹15L) | High Exposure | Expanded limits tailored for multi-card users and major EMI conversions. |
| **High Income** | `≥ ₹15,00,000` (≥ ₹15 Lakhs) | Peak Exposure | Premium line assignments designed for high-net-worth liquidity needs. |

---

### 2. Credit Score Tier Risk Stratification

While income determines the upper boundary of credit capacity, `Credit_Score` acts as the *risk multiplier* that determines where within that boundary a customer's limit actually sits.

| Credit Score Tier (`Credit_Score_Category`) | Score Range | Relative Limit Allocation | Default & Risk Profile (`Number_of_Defaults` & `Missed_Payments`) |
| :--- | :--- | :--- | :--- |
| **Excellent** | `≥ 800` | Maximum Tier Limit | Near-zero default instances; prime low-risk accounts. |
| **Very Good** | `750 – 799` | Premium Line Assignment | Extremely low missed payment rates; highly reliable. |
| **Good** | `700 – 749` | Standard Baseline Limit | Moderate risk profile; standard monitoring applied. |
| **Fair** | `650 – 699` | Restricted Baseline Limit | Elevated monitoring; lower limit approval ratios. |
| **Poor** | `550 – 649` | Risk-Mitigated Caps | Concentrated default instances; high debt-to-income ratios. |
| **Very Poor** | `< 550` | Minimum / Flagged Caps | Highest default concentration and frequent missed payments. |

---

### 3. Bank Relationship & Tenure (`Years_With_Bank`)

Long-term customer tenure acts as an internal credit seasoning mechanism, justifying automatic credit line enhancements over time.

| Relationship Stage | Tenure (`Years_With_Bank`) | Underwriting Impact | Primary Drivers |
| :--- | :--- | :--- | :--- |
| **New Onboarding** | `< 2 Years` | Conservative Baseline | Limited internal transaction history; relies strictly on CIBIL/FICO scores. |
| **Established Account** | `2 – 5 Years` | Gradual Line Expansion | Account activity seasoned; regular salary credits and timely EMI performance proven. |
| **Mature / Loyal** | `5+ Years` | Preferred Credit Line | Long internal transactional record reduces operational uncertainty, unlocking automatic CLI. |

---

### 📊 Summary Matrix: Primary Underwriting Determinants

| Feature Parameter | Correlation Strength | Primary Underwriting Role | Impact on Credit Allocation (₹) |
| :--- | :--- | :--- | :--- |
| **`Annual_Income`** | Strongest Positive | **Capacity Pillar** | Establishes core baseline credit ceiling across income brackets (< ₹3L to ≥ ₹15L). |
| **`Credit_Score`** | Strong Positive | **Risk Modifier** | High scores (≥ 750) unlock top tier limits; low scores (< 650) trigger risk caps. |
| **`Years_With_Bank`** | Moderate Positive | **Retention & Seasoning** | Long tenure yields automatic limit enhancements due to proven transactional reliability. |

## 2. Customer Liquidity & Asset ExposureSavings & Investment Correlation: 
-Evaluating correlation metrics for Savings_Balance and Investment_Value against Credit_Limit shows that customers with larger liquid safety nets represent lower credit risk, justifying higher line assignments.

-Top 10 High-Net-Worth Profile: Isolating the top 10 customers by Credit_Limit and Savings_Balance shows a concentrated overlap in specific Occupation classes, demonstrating where the bank's total credit exposure is concentrated.

## 3. Debt Burden & Risk ProfilingDebt-to-Income (DTI) & Monthly ObligationsEMI vs. Credit Limit: 
-Analyzing EMI_Per_Month alongside Debt_To_Income_Ratio highlights customer leverage levels. High DTI ratios correlate inversely with credit score health.

-Credit Utilization Patterns: Evaluating Credit_Utilization provides insight into how heavily customers depend on their existing credit lines:High Utilization + High DTI: Signals over-leveraged borrowers who are vulnerable to missing payments.

-Low Utilization + High Credit Score: Represents prime candidates for credit line increases or cross-selling investment products.

-Default & Missed Payment Sorting: Sorting records by Number_of_Defaults and Missed_Payments isolates the highest-risk portfolio segment. These accounts show low credit scores combined with elevated debt ratios

## 4. Demographic & Occupational Profiling:
## i. Occupational Profiling (Occupation)
Occupational grouping serves as a primary proxy for income stability, earning capacity, and cash-flow regularity.

Key Aggregations Analyzed: count, mean, min, max across Annual_Income, Credit_Score, Credit_Limit, Savings_Balance, Investment_Value, EMI_Per_Month, and Debt_To_Income_Ratio.

High-Earning Professionals (Corporate / Tech / Senior Roles):

Income & Credit Lines: Display the highest mean Annual_Income and Credit_Limit. These roles show high baseline liquidity (Savings_Balance) and investment capacity (Investment_Value).

Credit Score Stability: Maintain tight min-max spreads in Credit_Score, indicating consistent financial health and low volatility in repayment capability.

Variable-Income Roles (Freelancers / Small Business / Sales):

Spread & Volatility: Show significantly wider min-max variances in Annual_Income and Credit_Score.

Risk Cushioning: Higher volatility in monthly income leads banks to maintain more conservative average Credit_Limit caps relative to their peak income to mitigate sudden cash-flow shocks.

## ii. Life-Stage & Age Cohort Profiling (Age_Group)
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

## iii. Employment Type Profiling (Employment_Type)
Evaluating customer records across Salaried vs. Self-Employed / Contractual profiles reveals distinct risk-reward trade-offs:

Salaried Individuals:

Predictable monthly income streams result in predictable cash flows.

Receive higher baseline Credit_Limit approvals at lower income thresholds due to lower perceived default risk.

Display stable Debt_To_Income_Ratio control.

Self-Employed Individuals:

Show higher average asset generation potential (Investment_Value), but face stricter debt-servicing scrutiny.

Banks adjust leverage boundaries (Credit_Limit) based on higher required liquid cushions (Savings_Balance).

## iv. Residential Status (Residential_Status)
Housing status provides strong context regarding fixed overhead costs, asset backing, and long-term residency stability:

Owns / Mortgage Holders:

Asset Backing: Higher mean Savings_Balance, Investment_Value, and higher baseline Credit_Score metrics.

Underwriting Preference: Mortgage holders and property owners present collateral/stability factors that justify higher extended credit lines.

Renters:

Display higher sensitivity to rising monthly fixed obligations (EMI_Per_Month to income ratio).

Require tighter monitoring of Credit_Utilization to prevent over-leveraging.

## v. Gender-Based Financial Benchmarking (Gender)
Comparing Annual_Income, Credit_Score, and Credit_Limit across gender breakdowns provides an objective baseline audit:

Credit Score Parity: Credit_Score distribution remains uniform across genders, confirming that credit rating models are driven strictly by financial performance and repayment history.

Line Allocation: Average Credit_Limit scales proportionally with Annual_Income across all gender categories, keeping allocation parity strictly bound to risk metrics.
## 5. Compliance, Fraud, & Verification AuditFraud Flag Segmentation: 
-The aggregation on Fraud_Flag shows that flagged accounts exhibit significantly higher average Missed_Payments and Number_of_Defaults, alongside reduced credit limits.

-KYC & PAN Verification Impact: Accounts with completed KYC_Status and verified PAN_Verified maintain higher average credit scores and higher credit line allocations compared to unverified or pending accounts, confirming that identity verification reduces default risk.

-Primary Credit Limit Driver: Annual_Income exhibits a strong positive correlation with Credit_Limit, followed by Credit_Score and overall tenure with the bank (Years_With_Bank).

-Risk Indicator Divergence: High Debt_To_Income_Ratio and higher instances of Missed_Payments strongly align with lower credit score bands and elevated Number_of_Defaults.

-Compliance Correlation: Accounts with verified PAN and completed KYC_Status show higher average credit score benchmarks and higher credit limits. is this correct readme 

