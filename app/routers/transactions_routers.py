from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models import Scheme, RoleEnum, User,Transaction
from app.routers.auth_routes import get_current_user
from app.schema.transactions import *
from app.services.commission_engine import settle_commission

router = APIRouter(prefix="/transaction", tags=["transaction Management"])

@router.post("/")
def create_transaction(
    payload: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # ❌ Admin / SuperAdmin never initiate transactions
    if current_user.role in {RoleEnum.SUPER_ADMIN, RoleEnum.ADMIN}:
        raise HTTPException(
            status_code=403,
            detail="This role cannot initiate transactions"
        )

    if not current_user.scheme_id:
        raise HTTPException(
            status_code=400,
            detail="User is not assigned to any scheme"
        )

    txn = Transaction(
        user_id=current_user.id,
        scheme_id=current_user.scheme_id,
        service_id=payload.service_id,
        amount=payload.amount
    )

    db.add(txn)
    db.flush()  # get transaction.id

    # 🔥 Commission settlement (role-agnostic)
    settle_commission(
        db=db,
        transaction=txn
    )

    db.commit()

    return {
        "transaction_id": txn.id,
        "initiated_by_role": current_user.role,
        "message": "Transaction completed successfully"
    }
