# Rate Limiting for Banking Transactions

This project implements rate limiting solutions for Zeta's payment platform to prevent fraudulent users from spamming transactions while ensuring genuine users don't face unnecessary delays.

## Rate Limiting Approaches

### 1. Sliding Window Algorithm

Implemented in `SlidingWindowRateLimiter` class, this approach:
- Tracks exact timestamps of requests within a sliding time window
- Provides more precise control over request rates
- Prevents edge-case issues at window boundaries
- Implemented with a per-user deque of timestamps

### 2. Token Bucket Algorithm

Implemented in `TokenBucketRateLimiter` class, this approach:
- Maintains a "bucket" of tokens for each user that refill at a constant rate
- Allows for controlled bursts of traffic (more natural for user behavior)
- Each request consumes one token
- When a user's bucket is empty, further requests are rejected

## Implementation Details

Both implementations:
- Are thread-safe using locks to prevent race conditions in multi-threaded environments
- Track rate limits on a per-user basis
- Allow configuration of rate limiting parameters
- Have O(1) time complexity for the rate check operation

## Trade-offs Between Approaches

### Sliding Window Approach

**Pros:**
- More precise control over rate limits
- Accurately represents the actual request pattern over time
- Handles edge cases better than fixed-window counters
- Better for strict enforcement of limits

**Cons:**
- Higher memory usage as it stores individual request timestamps
- Memory usage grows with the number of requests within the window
- Potentially more CPU intensive due to timestamp management and cleanup

### Token Bucket Approach

**Pros:**
- Allows for natural bursts of traffic (better user experience)
- More memory efficient (stores only token count and last refill time)
- Good for services where occasional bursts are acceptable
- Simple to understand and implement

**Cons:**
- Less precise in enforcing strict limits
- Can be exploited with strategically timed request patterns
- Less suitable for scenarios requiring exact request counting

## Usage Example

```python
# Create a rate limiter that allows 5 requests per second per user
rate_limiter = SlidingWindowRateLimiter(max_requests=5, window_seconds=1)

# Check if a request is allowed
user_id = "alice"
if rate_limiter.is_allowed(user_id):
    # Process the request
    process_transaction(user_id, transaction_data)
else:
    # Reject the request
    return rate_limit_exceeded_response()
```

## Testing

Run the tests to see how the rate limiters perform with different user behaviors:

```
python3 test_rate_limiter.py
```

The test simulates:
- Regular users making transactions at a moderate pace
- Power users making transactions quickly but within limits
- Suspicious users trying to flood the system with transactions

## Conclusion

For Zeta's banking platform, the sliding window approach is recommended for most transaction types due to its precision and ability to enforce strict limits. However, the token bucket approach might be better for premium users or specific scenarios where allowing controlled bursts would improve user experience.

Both implementations effectively prevent transaction spamming while allowing legitimate users to transact smoothly. 