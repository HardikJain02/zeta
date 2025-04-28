from flask import Flask, request, jsonify
import uuid
import time
from rate_limiter import SlidingWindowRateLimiter, TokenBucketRateLimiter

app = Flask(__name__)

# Configure rate limiters
# Standard rate limiter - 5 requests per second
standard_rate_limiter = SlidingWindowRateLimiter(max_requests=5, window_seconds=1)

# Premium rate limiter - 10 requests per second with burst capability
premium_rate_limiter = TokenBucketRateLimiter(bucket_capacity=10, refill_rate=10)

# Mock user database - in a real system, this would be a database
users = {
    "user123": {"name": "Alice Smith", "premium": False, "balance": 10000.00},
    "user456": {"name": "Bob Jones", "premium": True, "balance": 25000.00}
}

# Mock transaction store
transactions = {}


@app.route('/api/v1/transactions', methods=['POST'])
def create_transaction():
    """
    Process a new banking transaction with rate limiting.
    """
    # Get user ID from request
    user_id = request.headers.get('X-User-ID')
    
    # Validate user
    if not user_id or user_id not in users:
        return jsonify({"error": "Invalid or missing user ID"}), 401
    
    # Apply appropriate rate limiter based on user status
    if users[user_id]["premium"]:
        rate_limiter = premium_rate_limiter
    else:
        rate_limiter = standard_rate_limiter
    
    # Check if request is allowed by rate limiter
    if not rate_limiter.is_allowed(user_id):
        # Log the blocked request (in real system, would log to monitoring system)
        print(f"[{time.time()}] RATE LIMIT EXCEEDED: User {user_id}")
        
        # Return 429 Too Many Requests with Retry-After header
        response = jsonify({
            "error": "Rate limit exceeded",
            "message": "You have exceeded the transaction rate limit. Please try again later."
        })
        response.status_code = 429
        response.headers['Retry-After'] = '1'  # Suggest retry after 1 second
        return response
    
    # Parse transaction data from request
    try:
        data = request.json
        amount = float(data.get('amount', 0))
        destination = data.get('destination', '')
        description = data.get('description', '')
        
        # Validate transaction data
        if amount <= 0:
            return jsonify({"error": "Invalid amount"}), 400
        if not destination:
            return jsonify({"error": "Destination account required"}), 400
        
        # In real system: Check if user has sufficient funds
        if users[user_id]["balance"] < amount:
            return jsonify({"error": "Insufficient funds"}), 400
        
        # Generate transaction ID
        transaction_id = str(uuid.uuid4())
        
        # Process the transaction
        # In real system: Update database, call payment processor, etc.
        transactions[transaction_id] = {
            "id": transaction_id,
            "user_id": user_id,
            "amount": amount,
            "destination": destination,
            "description": description,
            "status": "completed",
            "timestamp": time.time()
        }
        
        # Update user balance (in real system, this would be an atomic database operation)
        users[user_id]["balance"] -= amount
        
        # Return success response
        return jsonify({
            "transaction_id": transaction_id,
            "status": "completed",
            "amount": amount,
            "new_balance": users[user_id]["balance"]
        })
        
    except Exception as e:
        # Log the error
        print(f"Error processing transaction: {str(e)}")
        return jsonify({"error": "Failed to process transaction"}), 500


@app.route('/api/v1/transactions/<transaction_id>', methods=['GET'])
def get_transaction(transaction_id):
    """
    Retrieve a specific transaction (also rate limited).
    """
    # Get user ID from request
    user_id = request.headers.get('X-User-ID')
    
    # Validate user
    if not user_id or user_id not in users:
        return jsonify({"error": "Invalid or missing user ID"}), 401
    
    # Apply rate limiting to GET requests as well
    if users[user_id]["premium"]:
        rate_limiter = premium_rate_limiter
    else:
        rate_limiter = standard_rate_limiter
    
    if not rate_limiter.is_allowed(user_id):
        response = jsonify({"error": "Rate limit exceeded"})
        response.status_code = 429
        response.headers['Retry-After'] = '1'
        return response
    
    # Check if transaction exists
    if transaction_id not in transactions:
        return jsonify({"error": "Transaction not found"}), 404
    
    # Check if user has permission to view this transaction
    if transactions[transaction_id]["user_id"] != user_id:
        return jsonify({"error": "Unauthorized"}), 403
    
    # Return transaction details
    return jsonify(transactions[transaction_id])


if __name__ == '__main__':
    # In a production environment, use WSGI server like Gunicorn
    app.run(debug=True, port=5000) 