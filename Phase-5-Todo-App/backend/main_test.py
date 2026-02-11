from fastapi import FastAPI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import models to register them with SQLModel
from models import Task

# Create FastAPI app instance
app = FastAPI(title="Todo Backend API", version="1.0.0")

@app.get("/")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Todo Backend API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)