# app/services/commission_engine.py
from sqlalchemy.orm import Session
from app.models import SchemeCommission, User,Scheme, Transaction,CommissionLedger
from app.models.models import CommissionTypeEnum,RoleEnum
from app.utils.role_hierarchy import ROLE_FIELD_MAP,ROLE_LEVEL

# app/services/commission_engine.py
from sqlalchemy.orm import Session
from app.models import SchemeCommission, Scheme
from app.utils.role_hierarchy import ROLE_FIELD_MAP, ROLE_LEVEL


def resolve_absolute_commission(db: Session, scheme: Scheme, service_id: int) -> dict:
    resolved = {}

    def get_root(s):
        while s.parent_scheme:
            s = s.parent_scheme
        return s

    root_scheme = get_root(scheme)

    for role, field in ROLE_FIELD_MAP.items():
        current_scheme = scheme

        # Walk hierarchy
        while current_scheme:
            record = db.query(SchemeCommission).filter(
                SchemeCommission.scheme_id == current_scheme.id,
                SchemeCommission.service_id == service_id
            ).first()

            if record:
                value = getattr(record, field)
                if value is not None:
                    resolved[role] = value
                    break

            current_scheme = current_scheme.parent_scheme

        # Root fallback
        if role not in resolved:
            root_record = db.query(SchemeCommission).filter(
                SchemeCommission.scheme_id == root_scheme.id,
                SchemeCommission.service_id == service_id
            ).first()

            if root_record:
                value = getattr(root_record, field)
                if value is not None:
                    resolved[role] = value

    return resolved





def calculate_commission_earnings(absolute: dict) -> dict:
    """
    Convert absolute commission into margin commission
    Missing roles are treated as 0
    """
    sorted_roles = sorted(
        ROLE_LEVEL.items(),
        key=lambda x: x[1]
    )

    earnings = {}

    for i, (role, _) in enumerate(sorted_roles):
        current_value = absolute.get(role, 0)

        next_value = 0
        for j in range(i + 1, len(sorted_roles)):
            next_role = sorted_roles[j][0]
            if next_role in absolute:
                next_value = absolute[next_role]
                break

        margin = current_value - next_value
        if margin > 0:
            earnings[role] = margin

    return earnings



def calculate_commission(amount, percent, commission_type):
    if commission_type == CommissionTypeEnum.PERCENTAGE:
        return round((amount * percent) / 100, 2)
    return round(percent, 2)



def settle_commission(db: Session, transaction: Transaction):
    user = db.query(User).get(transaction.user_id)

    # Step 1: Resolve absolute commission
    absolute = resolve_absolute_commission(
        db=db,
        scheme=user.scheme,
        service_id=transaction.service_id
    )
    
    print("Absolute Commissions:", absolute)

    # Step 2: Convert to margin
    earnings = calculate_commission_earnings(absolute)
    print("Earnings Distribution:", earnings)

    # Step 3: Pay only real users in hierarchy
    current = user
    while current:
        role_enum = RoleEnum[current.role.name]

        percent = earnings.get(role_enum)
        if percent and percent > 0:
            amount = calculate_commission(
                transaction.amount,
                percent,
                CommissionTypeEnum.PERCENTAGE
            )

            ledger = CommissionLedger(
                transaction_id=transaction.id,
                user_id=current.id,
                role=role_enum,
                scheme_id=current.scheme_id,
                service_id=transaction.service_id,
                commission_type=CommissionTypeEnum.PERCENTAGE,
                commission_percent=percent,
                commission_amount=amount
            )

            db.add(ledger)

        current = current.parent

    db.commit()
