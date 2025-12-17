# app/utils/role_hierarchy.py
from app.models import RoleEnum

ROLE_LEVEL = {
    RoleEnum.SUPER_ADMIN: 1,
    RoleEnum.ADMIN: 2,
    RoleEnum.WHITE_LABEL: 3,
    RoleEnum.MASTER_DISTRIBUTOR: 4,
    RoleEnum.DISTRIBUTOR: 5,
    RoleEnum.RETAILER: 6,
    RoleEnum.CUSTOMER: 7,
}


ROLE_FIELD_MAP = {
    RoleEnum.ADMIN: "admin",
    RoleEnum.WHITE_LABEL: "white_label",
    RoleEnum.MASTER_DISTRIBUTOR: "master_distributor",
    RoleEnum.DISTRIBUTOR: "distributor",
    RoleEnum.RETAILER: "retailer",
    RoleEnum.CUSTOMER: "customer",
}