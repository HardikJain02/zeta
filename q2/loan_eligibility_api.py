from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, validator, root_validator
from typing import Optional, List, Dict, Union
import uvicorn
import random
from enum import Enum
from datetime import datetime, date

app = FastAPI(title="Loan Eligibility API", 
              description="API that accepts customer data and returns a loan eligibility score with recommendations")

class EmploymentStatus(str, Enum):
    EMPLOYED = "employed"
    SELF_EMPLOYED = "self_employed"
    UNEMPLOYED = "unemployed"
    RETIRED = "retired"
    STUDENT = "student"

class LoanPurpose(str, Enum):
    HOME = "home_purchase"
    EDUCATION = "education"
    VEHICLE = "vehicle"
    PERSONAL = "personal"
    BUSINESS = "business"
    DEBT_CONSOLIDATION = "debt_consolidation"
    OTHER = "other"

class LoanType(str, Enum):
    FIXED = "fixed"
    VARIABLE = "variable"
    INTEREST_ONLY = "interest_only"
    BALLOON = "balloon"

class DisputeStatus(str, Enum):
    RESOLVED = "resolved"
    PENDING = "pending"
    REJECTED = "rejected"

class DisputeRecord(BaseModel):
    dispute_id: str
    description: str
    submission_date: str  # ISO format date string
    status: DisputeStatus

class CustomerData(BaseModel):
    customer_id: str
    name: str
    email: str
    date_of_birth: Optional[str] = None
    income: float
    credit_score: int
    employment_status: EmploymentStatus
    employment_duration: int
    total_debts: float = 0
    debt_to_income_ratio: Optional[float] = None
    existing_loans: int = 0
    previous_defaults: int = 0
    dispute_history: Optional[List[DisputeRecord]] = []
    
    @validator('income')
    def income_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Income must be greater than zero')
        return v
    
    @validator('credit_score')
    def credit_score_range(cls, v):
        if v < 300 or v > 850:
            raise ValueError('Credit score must be between 300 and 850')
        return v
    
    @root_validator
    def calculate_dti_if_missing(cls, values):
        dti = values.get('debt_to_income_ratio')
        if dti is None:
            # If not provided but we have income and total debts, calculate it
            income = values.get('income')
            total_debts = values.get('total_debts', 0)
            if income and income > 0:
                values['debt_to_income_ratio'] = total_debts / income
            else:
                values['debt_to_income_ratio'] = 0.0
        return values
    
    @validator('debt_to_income_ratio')
    def check_dti_range(cls, v):
        if v is not None and (v < 0 or v > 1):
            raise ValueError('Debt to income ratio must be between 0 and 1')
        return v

class CollateralInfo(BaseModel):
    type: str  # e.g., "real_estate", "vehicle", "securities"
    value: float
    description: Optional[str] = None

class CoApplicantInfo(BaseModel):
    name: str
    income: float
    credit_score: int
    relationship: str  # e.g., "spouse", "business_partner"

class LoanApplicationRequest(BaseModel):
    loan_amount: float
    loan_type: LoanType
    loan_purpose: LoanPurpose
    loan_term: int  # in months
    collateral: Optional[CollateralInfo] = None
    co_applicant: Optional[CoApplicantInfo] = None
    customer_id: str  # Foreign key to Customer table
    
    @validator('loan_amount')
    def loan_amount_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Loan amount must be greater than zero')
        return v
    
    @validator('loan_term')
    def loan_term_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Loan term must be greater than zero')
        return v

class LoanEligibilityResponse(BaseModel):
    eligibility_score: float
    recommendation: str
    approval_status: str
    max_loan_amount: Optional[float] = None
    suggested_interest_rate: Optional[float] = None
    dispute_impact: Optional[Dict[str, float]] = None
    application_id: Optional[str] = None  # Would be assigned by the database in production

class LoanEligibilityRequest(BaseModel):
    customer: CustomerData
    loan_application: LoanApplicationRequest

@app.post("/loan-eligibility", response_model=LoanEligibilityResponse)
async def calculate_loan_eligibility(request: LoanEligibilityRequest):
    """
    Calculate loan eligibility score based on customer data and loan application
    """
    # Verify the customer_id in the loan application matches the customer
    if request.customer.customer_id != request.loan_application.customer_id:
        raise HTTPException(status_code=400, detail="Customer ID mismatch between customer and loan application")
    
    # Ensure debt_to_income_ratio is set
    if request.customer.debt_to_income_ratio is None:
        if request.customer.income > 0:
            request.customer.debt_to_income_ratio = request.customer.total_debts / request.customer.income
        else:
            request.customer.debt_to_income_ratio = 0.0
    
    # Calculate eligibility score
    score, dispute_impact = calculate_eligibility_score(request.customer, request.loan_application)
    
    # Generate recommendation and approval status
    result = generate_recommendation(score, request.customer, request.loan_application)
    
    # Add dispute impact information
    result.dispute_impact = dispute_impact
    
    # Generate a mock application ID (in a real system, this would be from the database)
    result.application_id = f"LOAN-{random.randint(10000, 99999)}"
    
    return result

def calculate_eligibility_score(customer: CustomerData, loan_application: LoanApplicationRequest) -> tuple:
    """
    Calculate eligibility score based on AI logic
    
    This is a model that weighs different factors:
    - Credit score: 30%
    - Income to loan amount ratio: 20%
    - Employment stability: 15%
    - Debt to income ratio: 15%
    - Previous loan history: 10%
    - Dispute history: 10%
    """
    # Credit score factor (30% of total)
    credit_factor = (customer.credit_score - 300) / 550 * 30  # Normalized to 0-30 range
    
    # Income to loan ratio factor (20% of total)
    income_loan_ratio = min(customer.income / (loan_application.loan_amount or 1), 10) / 10
    income_factor = income_loan_ratio * 20
    
    # Employment stability factor (15% of total)
    employment_factor = 0
    if customer.employment_status in [EmploymentStatus.EMPLOYED, EmploymentStatus.SELF_EMPLOYED]:
        # Higher score for longer employment
        employment_factor = min(customer.employment_duration / 60, 1) * 15  # Cap at 5 years (60 months)
    elif customer.employment_status == EmploymentStatus.RETIRED:
        employment_factor = 10  # Retirees get a moderate score
    
    # Debt to income ratio factor (15% of total)
    dti_factor = (1 - customer.debt_to_income_ratio) * 15
    
    # Previous loan history factor (10% of total)
    history_factor = 10 - (min(customer.previous_defaults, 5) * 2)  # Each default reduces score, max 5 defaults
    
    # Dispute history factor (10% of total)
    dispute_factor, dispute_impact = calculate_dispute_factor(customer.dispute_history)
    
    # Calculate total score (0-100)
    total_score = credit_factor + income_factor + employment_factor + dti_factor + history_factor + dispute_factor
    
    # Apply loan purpose adjustment
    if loan_application.loan_purpose in [LoanPurpose.HOME, LoanPurpose.EDUCATION]:
        total_score *= 1.05  # 5% boost for home and education loans
    elif loan_application.loan_purpose == LoanPurpose.BUSINESS:
        total_score *= 0.95  # 5% reduction for higher-risk business loans
    
    # Apply loan term adjustment
    if loan_application.loan_term > 120:  # Long term loans > 10 years
        total_score *= 0.97  # 3% reduction
    
    # Apply co-applicant adjustment if present
    if loan_application.co_applicant:
        co_applicant_factor = calculate_co_applicant_factor(loan_application.co_applicant, customer)
        total_score *= co_applicant_factor
    
    # Apply collateral adjustment if present
    if loan_application.collateral:
        collateral_factor = calculate_collateral_factor(loan_application.collateral, loan_application.loan_amount)
        total_score *= collateral_factor
    
    # Cap score at 100
    return min(round(total_score, 1), 100), dispute_impact

def calculate_co_applicant_factor(co_applicant: CoApplicantInfo, customer: CustomerData) -> float:
    """Calculate the impact of a co-applicant on loan eligibility"""
    
    # Base factor is 1.0 (no change)
    factor = 1.0
    
    # If co-applicant has good credit, improve factor
    if co_applicant.credit_score > 700:
        factor += 0.05
    elif co_applicant.credit_score < 600:
        factor -= 0.05
    
    # If co-applicant income significantly adds to customer income
    combined_income = customer.income + co_applicant.income
    if combined_income > customer.income * 1.5:
        factor += 0.05
    
    # Cap the adjustment range
    return max(min(factor, 1.15), 0.9)

def calculate_collateral_factor(collateral: CollateralInfo, loan_amount: float) -> float:
    """Calculate the impact of collateral on loan eligibility"""
    
    # Base factor is 1.0 (no change)
    factor = 1.0
    
    # If collateral covers a significant portion of the loan
    coverage_ratio = collateral.value / loan_amount
    
    if coverage_ratio >= 1.0:  # Full coverage
        factor += 0.1
    elif coverage_ratio >= 0.7:  # Significant coverage
        factor += 0.05
    
    # Cap the adjustment
    return min(factor, 1.1)

def calculate_dispute_factor(dispute_history: List[DisputeRecord]) -> tuple:
    """Calculate the impact of dispute history on eligibility score"""
    
    if not dispute_history:
        return 10.0, {"dispute_score": 10.0, "total_disputes": 0, "recent_disputes": 0, "rejected_disputes": 0}
    
    # Start with maximum score
    max_score = 10.0
    current_score = max_score
    
    # Count types of disputes
    total_disputes = len(dispute_history)
    recent_disputes = 0
    rejected_disputes = 0
    
    # Check for recent disputes (within last 12 months)
    current_date = datetime.now()
    
    for dispute in dispute_history:
        try:
            # Try to parse the submission date
            dispute_date = datetime.fromisoformat(dispute.submission_date.replace('Z', '+00:00'))
            
            # Check if dispute is recent (within last 12 months)
            days_difference = (current_date - dispute_date).days
            if days_difference <= 365:
                recent_disputes += 1
            
            # Check dispute status
            if dispute.status == DisputeStatus.REJECTED:
                rejected_disputes += 1
                
        except (ValueError, TypeError):
            # If date parsing fails, continue to next dispute
            continue
    
    # Calculate penalty based on number and recency of disputes
    # Each dispute reduces score, with higher impact for recent and rejected disputes
    
    # Penalty for total number of disputes
    if total_disputes > 0:
        total_disputes_penalty = min(total_disputes * 0.5, 3.0)  # Up to 3 points for many disputes
        current_score -= total_disputes_penalty
    
    # Additional penalty for recent disputes
    if recent_disputes > 0:
        recent_disputes_penalty = min(recent_disputes * 1.0, 4.0)  # Up to 4 points for recent disputes
        current_score -= recent_disputes_penalty
    
    # Additional penalty for rejected disputes
    if rejected_disputes > 0:
        rejected_disputes_penalty = min(rejected_disputes * 1.5, 5.0)  # Up to 5 points for rejected disputes
        current_score -= rejected_disputes_penalty
    
    # Ensure score doesn't go below 0
    current_score = max(current_score, 0)
    
    # Return the dispute factor and details about the impact
    impact = {
        "dispute_score": round(current_score, 1),
        "total_disputes": total_disputes,
        "recent_disputes": recent_disputes,
        "rejected_disputes": rejected_disputes
    }
    
    return current_score, impact

def generate_recommendation(score: float, customer: CustomerData, loan_application: LoanApplicationRequest) -> LoanEligibilityResponse:
    """Generate human-readable recommendation based on eligibility score"""
    
    # Calculate maximum loan amount based on income and credit score
    income_based_limit = customer.income * 5  # Up to 5x annual income
    credit_based_multiplier = 0.5 + (customer.credit_score - 300) / 550  # 0.5 to 1.5 based on credit
    
    # If there's a co-applicant, consider their income too
    if loan_application.co_applicant:
        combined_income = customer.income + loan_application.co_applicant.income
        income_based_limit = combined_income * 4  # Slightly more conservative with combined income
    
    max_loan = min(income_based_limit * credit_based_multiplier, loan_application.loan_amount * 1.2)
    
    # Calculate suggested interest rate based on score and credit
    base_rate = 5.0  # Base interest rate
    risk_adjustment = (100 - score) / 20  # 0-5% adjustment based on risk
    credit_adjustment = (850 - customer.credit_score) / 100  # 0-5.5% adjustment based on credit
    
    # Adjust for loan type
    if loan_application.loan_type == LoanType.VARIABLE:
        base_rate -= 0.25  # Variable rates typically start lower
    elif loan_application.loan_type == LoanType.INTEREST_ONLY:
        base_rate += 0.5  # Interest-only loans are higher risk
    elif loan_application.loan_type == LoanType.BALLOON:
        base_rate += 0.75  # Balloon loans are highest risk
    
    interest_rate = round(base_rate + risk_adjustment + credit_adjustment, 2)
    
    # Add dispute history impact to recommendation
    dispute_message = ""
    if customer.dispute_history and len(customer.dispute_history) > 0:
        recent_disputes = sum(1 for d in customer.dispute_history if datetime.now().timestamp() - datetime.fromisoformat(d.submission_date.replace('Z', '+00:00')).timestamp() < 86400 * 365)
        if recent_disputes > 0:
            dispute_message = f" Your recent dispute history ({recent_disputes} in the past year) is affecting your eligibility."
    
    if score >= 80:
        approval_status = "Approved"
        recommendation = f"Congratulations! You are highly eligible for this loan. We recommend proceeding with your application for ${loan_application.loan_amount:,.2f}."
    elif score >= 60:
        approval_status = "Conditionally Approved"
        if loan_application.loan_amount > max_loan:
            recommendation = f"You qualify for a loan, but we recommend reducing the amount to ${max_loan:,.2f} for better terms. Your credit profile suggests an interest rate of {interest_rate}%.{dispute_message}"
        else:
            recommendation = f"You qualify for this loan with an estimated interest rate of {interest_rate}%. Consider improving your credit score or reducing debt to get better terms.{dispute_message}"
    else:
        approval_status = "Denied"
        if score >= 40:
            recommendation = f"We cannot approve your application at this time. Consider improving your credit score (current: {customer.credit_score}), reducing existing debt, or applying for a smaller loan amount.{dispute_message}"
        else:
            recommendation = f"Your application does not meet our current lending criteria. Major factors include credit score ({customer.credit_score}), debt-to-income ratio ({customer.debt_to_income_ratio:.2%}), and loan amount (${loan_application.loan_amount:,.2f}).{dispute_message}"
    
    return LoanEligibilityResponse(
        eligibility_score=score,
        recommendation=recommendation,
        approval_status=approval_status,
        max_loan_amount=max_loan if score >= 60 else None,
        suggested_interest_rate=interest_rate if score >= 60 else None
    )

@app.get("/")
async def root():
    return {"message": "Welcome to the Loan Eligibility API. Use /docs to see the API documentation."}

if __name__ == "__main__":
    uvicorn.run("loan_eligibility_api:app", host="0.0.0.0", port=8000, reload=True) 