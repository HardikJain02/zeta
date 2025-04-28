from flask import Flask, request, jsonify
from datetime import datetime, timedelta

app = Flask(__name__)

# Simulated customer history (replace with database in production)
customer_history = {
    "C001": {"dispute_count": 5, "high_risk": True, "last_dispute_date": "2025-04-20", "credit_score": 650},
    "C002": {"dispute_count": 1, "high_risk": False, "last_dispute_date": "2025-03-01", "credit_score": 750}
}

@app.route('/process-dispute', methods=['POST'])
def process_dispute():
    data = request.get_json()
    customer_id = data.get('customer_id')
    dispute_description = data.get('dispute_description', '').lower()
    transaction_amount = data.get('transaction_amount', 0)
    submission_date = data.get('submission_date', datetime.now().strftime("%Y-%m-%d"))

    # Simulate AI categorization (replace with BERT model in production)
    category = "Fraud" if "fraud" in dispute_description or "unauthorized" in dispute_description else \
               "Billing Error" if "error" in dispute_description else "Other"

    # Assign priority based on customer history
    history = customer_history.get(customer_id, {"dispute_count": 0, "high_risk": False, "last_dispute_date": None, "credit_score": 700})
    dispute_count = history["dispute_count"]
    priority = "High" if dispute_count >= 4 else "Medium" if dispute_count >= 2 else "Low"

    # Adjust priority based on recency, amount, and category
    if history["last_dispute_date"]:
        last_dispute = datetime.strptime(history["last_dispute_date"], "%Y-%m-%d")
        if submission_date <= (last_dispute + timedelta(days=30)).strftime("%Y-%m-%d"):
            priority = "High" if priority == "Medium" else priority
    if transaction_amount > 1000:
        priority = "High" if priority == "Medium" else priority
    if category == "Fraud":
        priority = "High"

    # Flag high-risk disputes
    high_risk = history["high_risk"] or category == "Fraud" or transaction_amount > 1000 or history["credit_score"] < 600

    # Generate recommendation
    recommendation = f"Review {category} dispute. Priority: {priority}. "
    if high_risk:
        recommendation += "Flag for high-risk investigation."
    elif category == "Fraud":
        recommendation += "Verify transaction details with customer."
    elif category == "Billing Error":
        recommendation += "Request additional documentation."
    else:
        recommendation += "Standard review."

    return jsonify({
        'customer_id': customer_id,
        'category': category,
        'priority': priority,
        'high_risk': high_risk,
        'recommendation': recommendation
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001) 