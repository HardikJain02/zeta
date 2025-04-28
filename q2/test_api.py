import requests
import json
from datetime import datetime, timedelta

def test_loan_eligibility():
    """Test the loan eligibility API with sample data"""
    
    url = "http://localhost:8000/loan-eligibility"
    
    # Generate ISO formatted dates for disputes
    today = datetime.now()
    three_months_ago = (today - timedelta(days=90)).isoformat()
    six_months_ago = (today - timedelta(days=180)).isoformat()
    one_year_ago = (today - timedelta(days=365)).isoformat()
    two_years_ago = (today - timedelta(days=730)).isoformat()
    
    # Test case 1: High credit score, good income, no disputes
    test_case_1 = {
        "customer": {
            "customer_id": "CUST12345",
            "name": "John Smith",
            "email": "john.smith@example.com",
            "date_of_birth": "1985-06-15",
            "income": 95000,
            "credit_score": 780,
            "employment_status": "employed",
            "employment_duration": 60,
            "total_debts": 23750,  # 25% debt-to-income ratio
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
    
    # Test case 2: Moderate credit, high loan amount, some disputes
    test_case_2 = {
        "customer": {
            "customer_id": "CUST67890",
            "name": "Sarah Jones",
            "email": "sarah.jones@example.com",
            "date_of_birth": "1992-03-20",
            "income": 65000,
            "credit_score": 680,
            "employment_status": "employed",
            "employment_duration": 24,
            "total_debts": 22750,  # ~35% debt-to-income ratio
            "existing_loans": 2,
            "previous_defaults": 0,
            "dispute_history": [
                {
                    "dispute_id": "DSP001",
                    "description": "Unauthorized charge on credit card",
                    "submission_date": six_months_ago,
                    "status": "resolved"
                },
                {
                    "dispute_id": "DSP002",
                    "description": "Double charge at restaurant",
                    "submission_date": two_years_ago,
                    "status": "resolved"
                }
            ]
        },
        "loan_application": {
            "loan_amount": 300000,
            "loan_type": "variable",
            "loan_purpose": "home_purchase",
            "loan_term": 360,
            "customer_id": "CUST67890",
            "co_applicant": {
                "name": "Michael Jones",
                "income": 55000,
                "credit_score": 700,
                "relationship": "spouse"
            }
        }
    }
    
    # Test case 3: Poor credit, high DTI, many recent disputes
    test_case_3 = {
        "customer": {
            "customer_id": "CUST54321",
            "name": "Robert Brown",
            "email": "robert.brown@example.com",
            "date_of_birth": "1980-11-08",
            "income": 45000,
            "credit_score": 580,
            "employment_status": "employed",
            "employment_duration": 12,
            "total_debts": 21600,  # 48% debt-to-income ratio
            "existing_loans": 3,
            "previous_defaults": 1,
            "dispute_history": [
                {
                    "dispute_id": "DSP003",
                    "description": "Unauthorized online purchase",
                    "submission_date": three_months_ago,
                    "status": "pending"
                },
                {
                    "dispute_id": "DSP004",
                    "description": "Statement error on credit card",
                    "submission_date": six_months_ago,
                    "status": "rejected"
                },
                {
                    "dispute_id": "DSP005",
                    "description": "Service not received",
                    "submission_date": one_year_ago,
                    "status": "rejected"
                }
            ]
        },
        "loan_application": {
            "loan_amount": 200000,
            "loan_type": "interest_only",
            "loan_purpose": "personal",
            "loan_term": 360,
            "customer_id": "CUST54321"
        }
    }
    
    test_cases = [test_case_1, test_case_2, test_case_3]
    
    print("Testing Loan Eligibility API...")
    print("-" * 80)
    
    for i, test_case in enumerate(test_cases, 1):
        try:
            response = requests.post(url, json=test_case)
            response.raise_for_status()
            result = response.json()
            
            customer = test_case["customer"]
            loan = test_case["loan_application"]
            
            print(f"Test Case {i}:")
            print(f"Customer: {customer['name']} (ID: {customer['customer_id']})")
            print(f"Income: ${customer['income']:,}")
            print(f"Credit Score: {customer['credit_score']}")
            print(f"Loan Amount: ${loan['loan_amount']:,}")
            print(f"Loan Type: {loan['loan_type']}")
            print(f"Loan Purpose: {loan['loan_purpose']}")
            print(f"Dispute History: {len(customer['dispute_history'])} disputes")
            
            # Show co-applicant if present
            if "co_applicant" in loan:
                co_applicant = loan["co_applicant"]
                print(f"Co-Applicant: {co_applicant['name']}")
                print(f"Co-Applicant Income: ${co_applicant['income']:,}")
                print(f"Co-Applicant Credit Score: {co_applicant['credit_score']}")
            
            # Show collateral if present
            if "collateral" in loan:
                collateral = loan["collateral"]
                print(f"Collateral: {collateral['type']} (Value: ${collateral['value']:,})")
            
            print()
            print(f"Results:")
            print(f"Application ID: {result['application_id']}")
            print(f"Eligibility Score: {result['eligibility_score']}")
            print(f"Status: {result['approval_status']}")
            print(f"Recommendation: {result['recommendation']}")
            
            if result.get('dispute_impact'):
                print(f"Dispute Impact:")
                for k, v in result['dispute_impact'].items():
                    print(f"  {k}: {v}")
            
            if result.get('max_loan_amount'):
                print(f"Max Loan Amount: ${result['max_loan_amount']:,.2f}")
            
            if result.get('suggested_interest_rate'):
                print(f"Suggested Interest Rate: {result['suggested_interest_rate']}%")
            
            print("-" * 80)
        
        except requests.exceptions.RequestException as e:
            print(f"Error with Test Case {i}: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response: {e.response.text}")
            print("Make sure the API server is running at http://localhost:8000")
            break

if __name__ == "__main__":
    test_loan_eligibility() 