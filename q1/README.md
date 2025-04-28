# Dispute Processing API

A Flask-based API for processing customer disputes with automated categorization, prioritization, and recommendation generation.

## Features

- Categorizes disputes as Fraud, Billing Error, or Other based on description text
- Assigns priority (High, Medium, Low) based on customer history and dispute details
- Flags high-risk disputes based on multiple factors
- Generates contextual recommendations for dispute handling

## Requirements

- Python 3.6+
- Flask
- Requests (for test script)

## Installation

1. Clone this repository. Go to q1 folder
2. Install dependencies:

```bash
pip install flask requests
```

## Running the Application

1. Start the Flask server:

```bash
python app.py
```

The server will start on http://localhost:5001

2. Run the test script in a separate terminal:

```bash
python test_dispute_api.py
```

## API Endpoints

### Process Dispute

**Endpoint**: POST /process-dispute

**Request Body**:
```json
{
  "customer_id": "C001",
  "dispute_description": "This was an unauthorized transaction",
  "transaction_amount": 1500,
  "submission_date": "2025-05-01"
}
```

**Response**:
```json
{
  "customer_id": "C001",
  "category": "Fraud",
  "priority": "High",
  "high_risk": true,
  "recommendation": "Review Fraud dispute. Priority: High. Flag for high-risk investigation."
}
```

## Production Considerations

- Replace simulated customer history with a proper database
- Implement a production-grade ML model (e.g., BERT) for dispute categorization
- Add authentication and API security
- Add proper error handling and logging 