import time
from collections import deque
import threading


class SlidingWindowRateLimiter:
    """
    A sliding window rate limiter that limits requests to a specified rate.
    This implementation is thread-safe and memory efficient.
    """
    
    def __init__(self, max_requests=5, window_seconds=1):
        """
        Initialize the rate limiter.
        
        Args:
            max_requests: Maximum number of requests allowed in the window period
            window_seconds: Time window in seconds
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        # Store user request timestamps using a dictionary of deques
        self.user_requests = {}
        self.lock = threading.Lock()
    
    def is_allowed(self, user_id):
        """
        Check if a request from a user is allowed based on their recent activity.
        
        Args:
            user_id: Unique identifier for the user making the request
            
        Returns:
            bool: True if request is allowed, False if rate limit exceeded
        """
        with self.lock:
            # Initialize deque for new users
            if user_id not in self.user_requests:
                self.user_requests[user_id] = deque()
            
            # Get current time
            current_time = time.time()
            
            # Remove timestamps older than the window
            self._clean_old_requests(user_id, current_time)
            
            # Check if user has exceeded the rate limit
            if len(self.user_requests[user_id]) >= self.max_requests:
                return False
            
            # Add current request timestamp
            self.user_requests[user_id].append(current_time)
            return True
    
    def _clean_old_requests(self, user_id, current_time):
        """Remove timestamps older than the sliding window."""
        window_start = current_time - self.window_seconds
        
        # Remove old timestamps from the front of the deque
        while (self.user_requests[user_id] and 
               self.user_requests[user_id][0] < window_start):
            self.user_requests[user_id].popleft()
        
        # Don't delete the user entry even if empty - it'll be reused
        # This fixes the KeyError problem in the threaded test


class TokenBucketRateLimiter:
    """
    A token bucket rate limiter implementation.
    Allows for bursts of traffic within overall rate limits.
    """
    
    def __init__(self, bucket_capacity=5, refill_rate=5):
        """
        Initialize the token bucket rate limiter.
        
        Args:
            bucket_capacity: Maximum number of tokens in the bucket
            refill_rate: Number of tokens added per second
        """
        self.bucket_capacity = bucket_capacity
        self.refill_rate = refill_rate
        # Map of user_id to (tokens, last_refill_time)
        self.user_buckets = {}
        self.lock = threading.Lock()
    
    def is_allowed(self, user_id):
        """
        Check if a request from a user is allowed based on their token bucket.
        
        Args:
            user_id: Unique identifier for the user making the request
            
        Returns:
            bool: True if request is allowed, False if rate limit exceeded
        """
        with self.lock:
            current_time = time.time()
            
            # Initialize new users with a full bucket
            if user_id not in self.user_buckets:
                self.user_buckets[user_id] = (self.bucket_capacity, current_time)
                
            tokens, last_refill = self.user_buckets[user_id]
            
            # Calculate token refill
            time_passed = current_time - last_refill
            new_tokens = min(
                self.bucket_capacity,
                tokens + time_passed * self.refill_rate
            )
            
            # If no tokens available, reject the request
            if new_tokens < 1:
                return False
                
            # Consume a token and update the bucket
            self.user_buckets[user_id] = (new_tokens - 1, current_time)
            return True


# Example usage
if __name__ == "__main__":
    # Create a rate limiter with 5 requests per second limit
    rate_limiter = SlidingWindowRateLimiter(max_requests=5, window_seconds=1)
    
    # Simulate transactions for user "alice"
    user_id = "alice"
    
    # Try making 7 requests in quick succession
    for i in range(7):
        result = rate_limiter.is_allowed(user_id)
        print(f"Request {i+1} for {user_id}: {'Allowed' if result else 'Blocked'}")
    
    # Wait for a second to allow rate limit to reset
    print("Waiting for rate limit window to pass...")
    time.sleep(1.1)
    
    # Try another request after the window has passed
    result = rate_limiter.is_allowed(user_id)
    print(f"Request after waiting: {'Allowed' if result else 'Blocked'}") 