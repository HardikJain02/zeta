import requests
import json

# Base URL for the API
BASE_URL = "http://localhost:5001"

def test_process_dispute():
    # Test case 1: Fraud dispute with high-risk customer
    payload1 = {
        "customer_id": "C001",
        "dispute_description": "This was an unauthorized transaction on my card",
        "transaction_amount": 1500,
        "submission_date": "2025-05-01"
    }
    
    # Test case 2: Billing error with low-risk customer
    payload2 = {
        "customer_id": "C002",
        "dispute_description": "There was a billing error on my account",
        "transaction_amount": 500,
        "submission_date": "2025-05-01"
    }
    
    # Test case 3: Other dispute type with new customer
    payload3 = {
        "customer_id": "C003",
        "dispute_description": "I have a question about this charge",
        "transaction_amount": 200
    }
    
    # Send requests and print responses
    print("\nTest Case 1: Fraud dispute with high-risk customer")
    response1 = requests.post(f"{BASE_URL}/process-dispute", json=payload1)
    print(f"Status Code: {response1.status_code}")
    print(json.dumps(response1.json(), indent=2))
    
    print("\nTest Case 2: Billing error with low-risk customer")
    response2 = requests.post(f"{BASE_URL}/process-dispute", json=payload2)
    print(f"Status Code: {response2.status_code}")
    print(json.dumps(response2.json(), indent=2))
    
    print("\nTest Case 3: Other dispute type with new customer")
    response3 = requests.post(f"{BASE_URL}/process-dispute", json=payload3)
    print(f"Status Code: {response3.status_code}")
    print(json.dumps(response3.json(), indent=2))

if __name__ == "__main__":
    test_process_dispute() 