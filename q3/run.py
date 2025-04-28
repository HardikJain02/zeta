import uvicorn
from app.core.config import settings

if __name__ == "__main__":
    # Run the API with uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        workers=settings.WORKERS_COUNT,
    ) 