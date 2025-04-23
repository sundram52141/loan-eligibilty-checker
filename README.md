# Loan Eligibility Checker

An AI-powered loan eligibility checker that helps users determine their loan eligibility based on various financial and personal factors.

## Features

- Real-time loan eligibility assessment
- Comprehensive evaluation of multiple factors:
  - Credit score
  - Income
  - Employment history
  - Debt-to-income ratio
  - Down payment
  - Loan amount and term
- Detailed analysis and reasoning for the decision
- User-friendly interface

## Setup

1. Clone this repository
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

To run the application, execute:
```bash
streamlit run app.py
```

The application will open in your default web browser.

## How to Use

1. Enter your personal and financial information in the form
2. Click "Check Eligibility"
3. Review the results and analysis

## Eligibility Criteria

The application evaluates loan eligibility based on the following criteria:
- Minimum credit score: 620
- Maximum debt-to-income ratio: 43%
- Minimum down payment: 20% of loan amount
- Minimum employment history: 2 years
- Maximum monthly payment to income ratio: 28%

## Note

This is a demonstration application and should not be used as the sole basis for making financial decisions. Always consult with financial professionals for actual loan applications. 