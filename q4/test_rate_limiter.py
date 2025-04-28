import time
import threading
import random
from rate_limiter import SlidingWindowRateLimiter, TokenBucketRateLimiter


def simulate_transaction(user_id, rate_limiter, transaction_id):
    """Simulate a banking transaction with rate limiting."""
    if rate_limiter.is_allowed(user_id):
        # Transaction is allowed
        # In a real system, this would process the actual transaction
        print(f"[{time.time():.3f}] Transaction {transaction_id} for user {user_id}: PROCESSED")
        return True
    else:
        # Transaction is blocked due to rate limiting
        print(f"[{time.time():.3f}] Transaction {transaction_id} for user {user_id}: BLOCKED (rate limit)")
        return False


def simulate_user_behavior(user_id, rate_limiter, transaction_count, interval_min=0, interval_max=0.5):
    """Simulate a user making multiple transactions with varying intervals."""
    success_count = 0
    fail_count = 0
    
    for i in range(transaction_count):
        result = simulate_transaction(user_id, rate_limiter, i+1)
        if result:
            success_count += 1
        else:
            fail_count += 1
            
        # Random delay between transactions to simulate real-world usage
        if i < transaction_count - 1:  # No need to sleep after the last transaction
            sleep_time = random.uniform(interval_min, interval_max)
            time.sleep(sleep_time)
    
    print(f"\nUser {user_id} statistics:")
    print(f"  Successful transactions: {success_count}")
    print(f"  Blocked transactions: {fail_count}")
    print(f"  Success rate: {success_count/transaction_count*100:.1f}%")


def test_sliding_window():
    """Test the sliding window rate limiter with multiple users."""
    print("\n=== Testing Sliding Window Rate Limiter ===")
    rate_limiter = SlidingWindowRateLimiter(max_requests=5, window_seconds=1)
    
    # Regular user - makes transactions at a moderate pace
    regular_user = threading.Thread(
        target=simulate_user_behavior,
        args=("regular_user", rate_limiter, 10, 0.2, 0.3)
    )
    
    # Power user - makes transactions quickly but within limits
    power_user = threading.Thread(
        target=simulate_user_behavior,
        args=("power_user", rate_limiter, 10, 0.15, 0.25)
    )
    
    # Suspicious user - tries to make many transactions quickly
    suspicious_user = threading.Thread(
        target=simulate_user_behavior,
        args=("suspicious_user", rate_limiter, 15, 0, 0.1)
    )
    
    # Start all threads
    regular_user.start()
    power_user.start()
    suspicious_user.start()
    
    # Wait for all threads to complete
    regular_user.join()
    power_user.join()
    suspicious_user.join()


def test_token_bucket():
    """Test the token bucket rate limiter with multiple users."""
    print("\n=== Testing Token Bucket Rate Limiter ===")
    rate_limiter = TokenBucketRateLimiter(bucket_capacity=5, refill_rate=5)
    
    # Regular user - makes transactions at a moderate pace
    regular_user = threading.Thread(
        target=simulate_user_behavior,
        args=("regular_user", rate_limiter, 10, 0.2, 0.3)
    )
    
    # Power user - makes transactions quickly but within limits
    power_user = threading.Thread(
        target=simulate_user_behavior,
        args=("power_user", rate_limiter, 10, 0.15, 0.25)
    )
    
    # Suspicious user - tries to make many transactions quickly
    suspicious_user = threading.Thread(
        target=simulate_user_behavior,
        args=("suspicious_user", rate_limiter, 15, 0, 0.1)
    )
    
    # Start all threads
    regular_user.start()
    power_user.start()
    suspicious_user.start()
    
    # Wait for all threads to complete
    regular_user.join()
    power_user.join()
    suspicious_user.join()


if __name__ == "__main__":
    # Set random seed for reproducibility
    random.seed(42)
    
    # Test both rate limiting approaches
    test_sliding_window()
    
    # Wait between tests
    time.sleep(2)
    
    test_token_bucket() 