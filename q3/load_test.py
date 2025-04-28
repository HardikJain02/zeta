import argparse
import asyncio
import json
import random
import time
import uuid
from decimal import Decimal

import httpx
import statistics
from tqdm import tqdm

BASE_URL = "http://localhost:8000/api/v1"

# Create an account for testing
async def create_test_account():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/accounts",
            json={
                "account_number": f"TEST{uuid.uuid4().hex[:10].upper()}",
                "account_name": "Load Test Account",
                "currency": "USD",
                "initial_balance": 1000000  # Large balance for testing
            }
        )
        if response.status_code != 201:
            print(f"Failed to create account: {response.text}")
            return None
        return response.json()

# Run load test for debit transactions
async def run_debit_test(account_id, num_requests, concurrent_requests):
    url = f"{BASE_URL}/transactions/debit"
    
    # Track response times
    response_times = []
    successful_requests = 0
    failed_requests = 0
    
    async def make_request(i):
        nonlocal successful_requests, failed_requests
        
        # Create random transaction data
        data = {
            "account_id": account_id,
            "amount": round(random.uniform(1, 100), 2),
            "currency": "USD",
            "reference": f"LOADTEST-{uuid.uuid4()}",
            "description": f"Load test transaction {i}"
        }
        
        start_time = time.time()
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=data, timeout=30)
            
            end_time = time.time()
            response_time = (end_time - start_time) * 1000  # Convert to ms
            response_times.append(response_time)
            
            if response.status_code == 201:
                successful_requests += 1
            else:
                failed_requests += 1
                print(f"Request {i} failed with status {response.status_code}: {response.text}")
                
        except Exception as e:
            failed_requests += 1
            print(f"Request {i} exception: {str(e)}")
    
    # Create batches of concurrent requests
    batch_size = concurrent_requests
    for i in range(0, num_requests, batch_size):
        batch_end = min(i + batch_size, num_requests)
        batch = range(i, batch_end)
        
        # Show progress bar
        with tqdm(total=len(batch), desc=f"Batch {i//batch_size + 1}") as progress:
            tasks = []
            for j in batch:
                tasks.append(make_request(j))
            
            # Wait for batch to complete with progress updates
            for future in asyncio.as_completed(tasks):
                await future
                progress.update(1)
    
    # Calculate statistics
    if response_times:
        avg_response_time = statistics.mean(response_times)
        median_response_time = statistics.median(response_times)
        p95_response_time = sorted(response_times)[int(len(response_times) * 0.95)]
        min_response_time = min(response_times)
        max_response_time = max(response_times)
    else:
        avg_response_time = median_response_time = p95_response_time = min_response_time = max_response_time = 0
    
    return {
        "total_requests": num_requests,
        "successful_requests": successful_requests,
        "failed_requests": failed_requests,
        "avg_response_time_ms": avg_response_time,
        "median_response_time_ms": median_response_time,
        "p95_response_time_ms": p95_response_time,
        "min_response_time_ms": min_response_time,
        "max_response_time_ms": max_response_time
    }

async def main():
    parser = argparse.ArgumentParser(description="Banking API Load Test")
    parser.add_argument("--requests", type=int, default=1000, help="Number of requests to make")
    parser.add_argument("--concurrency", type=int, default=50, help="Number of concurrent requests")
    args = parser.parse_args()
    
    print(f"Creating test account...")
    account = await create_test_account()
    if not account:
        print("Failed to create test account. Exiting.")
        return
    
    account_id = account["id"]
    print(f"Test account created with ID: {account_id}")
    
    print(f"\nRunning debit load test with {args.requests} requests, {args.concurrency} concurrency")
    results = await run_debit_test(account_id, args.requests, args.concurrency)
    
    print("\nLoad Test Results:")
    print(f"Total Requests: {results['total_requests']}")
    print(f"Successful: {results['successful_requests']}")
    print(f"Failed: {results['failed_requests']}")
    print(f"Success Rate: {results['successful_requests'] / results['total_requests'] * 100:.2f}%")
    print(f"Average Response Time: {results['avg_response_time_ms']:.2f} ms")
    print(f"Median Response Time: {results['median_response_time_ms']:.2f} ms")
    print(f"95th Percentile: {results['p95_response_time_ms']:.2f} ms")
    print(f"Min Response Time: {results['min_response_time_ms']:.2f} ms")
    print(f"Max Response Time: {results['max_response_time_ms']:.2f} ms")

if __name__ == "__main__":
    asyncio.run(main()) 