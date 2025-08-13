#!/usr/bin/env python
"""
Start script for production deployment
"""
import os
import sys

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set environment variable for production
os.environ["ENV"] = "production"

# Import and run the production app
if __name__ == "__main__":
    import uvicorn
    from app.main_production import app
    
    port = int(os.environ.get("PORT", 8000))
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
