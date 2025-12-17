# app/utils/commission_permissions.py
from app.models.models import RoleEnum

ALLOWED_COMMISSION_ROLES = {
    RoleEnum.SUPER_ADMIN,
    RoleEnum.ADMIN,
    RoleEnum.WHITE_LABEL,
}

def can_set_commission(role: RoleEnum) -> bool:
    return role in ALLOWED_COMMISSION_ROLES
