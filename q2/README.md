# Loan Eligibility API

This API accepts customer data and returns a loan eligibility score with recommendations using basic AI logic.

## Features

- Calculates a loan eligibility score (0-100) based on customer financial data
- Provides a human-readable recommendation
- Determines approval status (Approved, Conditionally Approved, or Denied)
- Suggests maximum loan amount and interest rate for eligible applicants
- Evaluates dispute history impact on loan eligibility
- Supports co-applicants and collateral information

## Setup

1. Create and activate a virtual environment:
   ```
   python3 -m venv zeta
   source zeta/bin/activate
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the API server:
   ```
   python loan_eligibility_api.py
   ```

   The API will be available at http://localhost:8000

4. Run the test script (in a separate terminal):
   ```
   source zeta/bin/activate  # If not already activated
   python test_api.py
   ```

## Running the Complete Demo

For a complete demonstration of the loan eligibility scoring system:

1. Start the API server in the background:
   ```bash
   # Make sure any previous instances are stopped
   pkill -f "python loan_eligibility_api.py" || true
   
   # Start the server in the background
   python loan_eligibility_api.py &
   ```

2. Run the test script with sample loan applications:
   ```bash
   python test_api.py
   ```

3. To stop the server when finished:
   ```bash
   pkill -f "python loan_eligibility_api.py"
   ```

## API Documentation

Once running, visit http://localhost:8000/docs for interactive API documentation.

### Loan Eligibility Request Structure

```json
{
  "customer": {
    "customer_id": "CUST12345",
    "name": "John Smith",
    "email": "john.smith@example.com",
    "date_of_birth": "1985-06-15",
    "income": 95000,
    "credit_score": 780,
    "employment_status": "employed",
    "employment_duration": 60,
    "total_debts": 23750,
    "existing_loans": 1,
    "previous_defaults": 0,
    "dispute_history": []
  },
  "loan_application": {
    "loan_amount": 250000,
    "loan_type": "fixed",
    "loan_purpose": "home_purchase",
    "loan_term": 360,
    "customer_id": "CUST12345",
    "collateral": {
      "type": "real_estate",
      "value": 320000,
      "description": "Primary residence"
    }
  }
}
```

### Example Response

```json
{
  "eligibility_score": 82.0,
  "recommendation": "Congratulations! You are highly eligible for this loan. We recommend proceeding with your application for $250,000.00.",
  "approval_status": "Approved",
  "max_loan_amount": 300000,
  "suggested_interest_rate": 6.6,
  "dispute_impact": {
    "dispute_score": 10.0,
    "total_disputes": 0,
    "recent_disputes": 0,
    "rejected_disputes": 0
  },
  "application_id": "LOAN-74682"
}
```

## Eligibility Scoring Model

The API uses a weighted model considering:
- Credit score (30%)
- Income to loan amount ratio (20%)
- Employment stability (15%)
- Debt to income ratio (15%)
- Previous loan history (10%)
- Dispute history (10%)

Additional adjustments for:
- Loan purpose (favorable for home purchase and education)
- Loan term (slight reduction for very long-term loans)
- Co-applicant's income and credit score
- Collateral value relative to loan amount 