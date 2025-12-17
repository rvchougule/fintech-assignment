# app/utils/commission_validation.py
from fastapi import HTTPException
from app.utils.role_hierarchy import ROLE_LEVEL, ROLE_FIELD_MAP
from app.utils.commission_permissions import can_set_commission
from app.models.models import RoleEnum
from app.models import SchemeCommission, User
from app.schema.commission import CommissionSetup


def validate_commission_payload(
    current_user: User,
    payload: CommissionSetup,
    parent_commission: SchemeCommission | None
):
    if not can_set_commission(current_user.role.name):
        raise HTTPException(403, "Not allowed to set commissions")

    for role, field in ROLE_FIELD_MAP.items():
        value = getattr(payload, field)

        if value is None:
            continue

        # Can only set LOWER roles
        if ROLE_LEVEL[role] <= ROLE_LEVEL[current_user.role.name]:
            raise HTTPException(
                403,
                f"Cannot set commission for {role}"
            )

        # Parent cap enforcement
        if parent_commission:
            parent_value = getattr(parent_commission, field)
            if parent_value is not None and value > parent_value:
                raise HTTPException(
                    400,
                    f"{role} commission cannot exceed parent scheme limit"
                )

        if value < 0:
            raise HTTPException(400, "Commission cannot be negative")
