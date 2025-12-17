# app/routers/commission_routes.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import SchemeCommission, User,Scheme, RoleEnum, Transaction, CommissionLedger
from app.schema.commission import CommissionSetup, CommissionResponse
from app.routers.auth_routes import get_current_user
from app.utils.commission_validation import validate_commission_payload
from app.utils.role_hierarchy import ROLE_FIELD_MAP

router = APIRouter(prefix="/commissions", tags=["Commission Management"])


@router.post("/", response_model=CommissionResponse)
def set_commission(
    payload: CommissionSetup,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 1️⃣ Fetch scheme explicitly
    scheme = db.query(Scheme).filter(
        Scheme.id == payload.scheme_id,
        Scheme.created_by == current_user.id
    ).first()

    if not scheme:
        raise HTTPException(
            status_code=403,
            detail="You are not allowed to configure this scheme"
        )

    # 2️⃣ Fetch parent commission (if any)
    parent_commission = None
    if scheme.parent_scheme:
        parent_commission = db.query(SchemeCommission).filter(
            SchemeCommission.scheme_id == scheme.parent_scheme.id,
            SchemeCommission.service_id == payload.service_id
        ).first()

    # 3️⃣ Validate payload
    validate_commission_payload(
        current_user=current_user,
        payload=payload,
        parent_commission=parent_commission
    )

    # 4️⃣ UPSERT commission
    commission = db.query(SchemeCommission).filter(
        SchemeCommission.scheme_id == scheme.id,
        SchemeCommission.service_id == payload.service_id
    ).first()

    if not commission:
        commission = SchemeCommission(
            scheme_id=scheme.id,
            service_id=payload.service_id,
            commission_type=payload.commission_type,
            set_by_user_id=current_user.id
        )
        db.add(commission)

    # 5️⃣ Apply values
    for role, field in ROLE_FIELD_MAP.items():
        value = getattr(payload, field)
        if value is not None:
            setattr(commission, field, value)

    commission.commission_type = payload.commission_type
    commission.set_by_user_id = current_user.id

    db.commit()
    db.refresh(commission)

    return commission


@router.delete("/commissions/delete/{commission_id}", status_code=204)
def delete_commission(
    commission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    commission = db.query(SchemeCommission).filter(SchemeCommission.id == commission_id).first()
    if not commission:
        raise HTTPException(status_code=404, detail="Commission not found")

    # Only allow creator or admin
    if current_user.role not in {RoleEnum.SUPER_ADMIN, RoleEnum.ADMIN} and commission.set_by_user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed to delete this commission")

    # 1. Find transactions under this commission's scheme & service
    transactions = db.query(Transaction).filter(
        Transaction.scheme_id == commission.scheme_id,
        Transaction.service_id == commission.service_id
    ).all()

    for txn in transactions:
        # Delete related ledgers
        db.query(CommissionLedger).filter(CommissionLedger.transaction_id == txn.id).delete()
        # Delete transaction
        db.delete(txn)

    # Delete the commission itself
    db.delete(commission)
    db.commit()

    return {"message": f"Commission {commission_id} and related transactions & ledgers deleted successfully"}


@router.get("/scheme/{scheme_id}")
def get_commissions_by_scheme(
    scheme_id: int,
    service_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    scheme = db.query(Scheme).filter(Scheme.id == scheme_id).first()
    if not scheme:
        raise HTTPException(status_code=404, detail="Scheme not found")

    # 🔒 Optional access control
    if current_user.role.name not in {RoleEnum.ADMIN, RoleEnum.SUPER_ADMIN} \
       and scheme.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    commission_chain = []
    current_scheme = scheme

    while current_scheme:
        commission = db.query(SchemeCommission).filter(
            SchemeCommission.scheme_id == current_scheme.id,
            SchemeCommission.service_id == service_id
        ).first()

        commission_chain.append({
            "scheme_id": current_scheme.id,
            "scheme_name": current_scheme.name,
            "is_root": current_scheme.parent_scheme_id is None,
            "commissions": (
                {
                    role.name: getattr(commission, field)
                    for role, field in ROLE_FIELD_MAP.items()
                }
                if commission else None
            )
        })

        current_scheme = current_scheme.parent_scheme


    return {
        "scheme_id": scheme_id,
        "service_id": service_id,
        "commission_chain": commission_chain
    }
