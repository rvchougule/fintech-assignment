# app/routers/commission_routes.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import SchemeCommission, User,Scheme
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

