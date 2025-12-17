from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models import Scheme, RoleEnum, User,Transaction,CommissionLedger
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


@router.get("/my-summary")
def my_transaction_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 1. Fetch user transactions
    transactions = db.query(Transaction).filter(
        Transaction.user_id == current_user.id
    ).all()

    response = []

    for txn in transactions:
        # 2. Fetch commission distribution
        ledgers = db.query(CommissionLedger).filter(
            CommissionLedger.transaction_id == txn.id
        ).all()

        distribution = []
        my_commission = None

        for ledger in ledgers:
            entry = {
                "user_id": ledger.user_id,
                "role": ledger.role.name if hasattr(ledger.role, "name") else ledger.role,
                "percent": ledger.commission_percent,
                "amount": ledger.commission_amount
            }

            distribution.append(entry)

            if ledger.user_id == current_user.id:
                my_commission = {
                    "percent": ledger.commission_percent,
                    "amount": ledger.commission_amount
                }

        response.append({
            "transaction_id": txn.id,
            "amount": txn.amount,
            "service_id": txn.service_id,
            "created_at": txn.created_at,
            "my_commission": my_commission,
            "commission_distribution": distribution
        })

    return {
        "user": {
            "id": current_user.id,
            "role": current_user.role.name
        },
        "transactions": response
    }


@router.delete("/delete/{txn_id}", status_code=204)
def delete_transaction(
    txn_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    txn = db.query(Transaction).filter(Transaction.id == txn_id).first()
    if not txn:
        raise HTTPException(status_code=404, detail="Transaction not found")

    # Only allow the owner or admin to delete
    if current_user.role.name not in {RoleEnum.SUPER_ADMIN, RoleEnum.ADMIN} and txn.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed to delete this transaction")

    # Delete associated commission ledgers
    db.query(CommissionLedger).filter(CommissionLedger.transaction_id == txn.id).delete()

    # Delete transaction
    db.delete(txn)
    db.commit()

    return {"message": f"Transaction {txn_id} and its commission ledger deleted successfully"}
