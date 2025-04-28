from fastapi import APIRouter
from app.api.v1.endpoints import accounts, transactions

api_router = APIRouter()
api_router.include_router(accounts.router)
api_router.include_router(transactions.router) 