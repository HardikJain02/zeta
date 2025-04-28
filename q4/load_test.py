import requests
import threading
import time
import random
import json
from concurrent.futures import ThreadPoolExecutor


class BankingAPILoadTest:
    """
    Load testing tool for our Banking API with rate limiting.
    """
    
    def __init__(self, base_url="http://localhost:5000"):
        """Initialize the load test with API endpoint."""
        self.base_url = base_url
        self.transactions_endpoint = f"{base_url}/api/v1/transactions"
        
        # Test users - in a real system these would be test accounts
        self.standard_user = "user123"  # Standard user with 5 req/sec limit
        self.premium_user = "user456"   # Premium user with 10 req/sec limit
        
        # Statistics tracking
        self.success_count = 0
        self.error_count = 0
        self.rate_limited_count = 0
        self.lock = threading.Lock()
    
    def create_transaction(self, user_id, amount=None):
        """Send a transaction request to the API."""
        if amount is None:
            # Generate random transaction amount between $1 and $100
            amount = round(random.uniform(1.0, 100.0), 2)
        
        # Prepare transaction data
        transaction_data = {
            "amount": amount,
            "destination": f"account-{random.randint(1000, 9999)}",
            "description": f"Test transaction {time.time()}"
        }
        
        # Send the request with user ID in header
        headers = {
            "Content-Type": "application/json",
            "X-User-ID": user_id
        }
        
        try:
            response = requests.post(
                self.transactions_endpoint,
                data=json.dumps(transaction_data),
                headers=headers
            )
            
            # Track the result based on status code
            with self.lock:
                if response.status_code == 200:
                    self.success_count += 1
                    return True
                elif response.status_code == 429:  # Rate limit exceeded
                    self.rate_limited_count += 1
                    return False
                else:
                    self.error_count += 1
                    print(f"Error: {response.status_code} - {response.text}")
                    return False
        
        except Exception as e:
            with self.lock:
                self.error_count += 1
            print(f"Exception: {str(e)}")
            return False
    
    def user_transaction_burst(self, user_id, count, delay_min=0, delay_max=0.1):
        """Simulate a burst of transactions from a single user."""
        for i in range(count):
            self.create_transaction(user_id)
            
            # Random delay between requests
            if i < count - 1:  # No need to delay after the last request
                time.sleep(random.uniform(delay_min, delay_max))
    
    def run_standard_user_test(self):
        """Test with a standard user (5 req/sec limit)."""
        print(f"\nRunning test for standard user ({self.standard_user})")
        
        # Reset counters
        self.success_count = 0
        self.rate_limited_count = 0
        self.error_count = 0
        
        # Simulate burst of 20 requests (should hit rate limit)
        start_time = time.time()
        self.user_transaction_burst(self.standard_user, 20, 0, 0.05)
        end_time = time.time()
        
        # Print results
        print(f"Standard user test completed in {end_time - start_time:.2f} seconds")
        print(f"Successful transactions: {self.success_count}")
        print(f"Rate limited transactions: {self.rate_limited_count}")
        print(f"Other errors: {self.error_count}")
    
    def run_premium_user_test(self):
        """Test with a premium user (10 req/sec limit)."""
        print(f"\nRunning test for premium user ({self.premium_user})")
        
        # Reset counters
        self.success_count = 0
        self.rate_limited_count = 0
        self.error_count = 0
        
        # Simulate burst of 20 requests (should hit rate limit but less severely)
        start_time = time.time()
        self.user_transaction_burst(self.premium_user, 20, 0, 0.05)
        end_time = time.time()
        
        # Print results
        print(f"Premium user test completed in {end_time - start_time:.2f} seconds")
        print(f"Successful transactions: {self.success_count}")
        print(f"Rate limited transactions: {self.rate_limited_count}")
        print(f"Other errors: {self.error_count}")
    
    def run_concurrent_users_test(self, user_count=10, requests_per_user=5):
        """Simulate multiple users making concurrent requests."""
        print(f"\nRunning concurrent users test ({user_count} users)")
        
        # Reset counters
        self.success_count = 0
        self.rate_limited_count = 0
        self.error_count = 0
        
        start_time = time.time()
        
        # Create a mix of standard and premium users
        users = []
        for i in range(user_count):
            if i % 5 == 0:  # 20% premium users
                users.append(self.premium_user)
            else:
                users.append(self.standard_user)
        
        # Execute concurrent requests using thread pool
        with ThreadPoolExecutor(max_workers=user_count) as executor:
            for user_id in users:
                executor.submit(self.user_transaction_burst, user_id, requests_per_user, 0.1, 0.2)
        
        end_time = time.time()
        
        # Print results
        print(f"Concurrent users test completed in {end_time - start_time:.2f} seconds")
        print(f"Successful transactions: {self.success_count}")
        print(f"Rate limited transactions: {self.rate_limited_count}")
        print(f"Other errors: {self.error_count}")


if __name__ == "__main__":
    # This script can be run when the Flask app is running
    print("Banking API Load Test")
    print("=====================")
    print("Make sure the banking_api_example.py is running before starting this test.")
    
    # Create load test instance
    load_test = BankingAPILoadTest()
    
    # Run tests
    load_test.run_standard_user_test()
    time.sleep(2)  # Wait for rate limit window to reset
    
    load_test.run_premium_user_test()
    time.sleep(2)  # Wait for rate limit window to reset
    
    load_test.run_concurrent_users_test() 