from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import SessionLocal, engine,Base
from app.models import *
import uvicorn

# -------------------------------------------------
# Create DB Tables
# -------------------------------------------------
Base.metadata.create_all(bind=engine)

# -------------------------------------------------
# FastAPI App
# -------------------------------------------------
app = FastAPI(
    title="FinTech Scheme & Commission Engine",
    description="BRD-aligned Scheme and Commission Management System",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*"                        
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------------------------------------
# Database Dependency
# -------------------------------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# -------------------------------------------------
# Health Check (MANDATORY for demos)
# -------------------------------------------------
@app.get("/")
def health_check():
    return {
        "status": "OK",
        "message": "Scheme & Commission Engine is running"
    }

# -------------------------------------------------
# Placeholder Routes (will add next)
# -------------------------------------------------

@app.get("/ping")
def ping():
    return {"message": "pong"}


from app.routers import auth_routes, scheme_routes, member_routes, commission_routes, transactions_routers

app.include_router(auth_routes.router)
app.include_router(scheme_routes.router)
app.include_router(member_routes.router)
app.include_router(commission_routes.router)
app.include_router(transactions_routers.router)



if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )