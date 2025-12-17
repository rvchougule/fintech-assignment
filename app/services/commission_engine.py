# app/services/commission_engine.py
from sqlalchemy.orm import Session
from app.models import SchemeCommission, User,Scheme, Transaction,CommissionLedger
from app.models.models import CommissionTypeEnum,RoleEnum
from app.utils.role_hierarchy import ROLE_FIELD_MAP,ROLE_LEVEL

# app/services/commission_engine.py
from sqlalchemy.orm import Session
from app.models import SchemeCommission, Scheme
from app.utils.role_hierarchy import ROLE_FIELD_MAP, ROLE_LEVEL


def resolve_absolute_commission(
    db: Session,
    scheme: Scheme,
    service_id: int
) -> dict:
    """
    Walk up scheme tree and resolve absolute commission per role
    """
    chain = []

    while scheme:
        record = db.query(SchemeCommission).filter(
            SchemeCommission.scheme_id == scheme.id,
            SchemeCommission.service_id == service_id
        ).first()
        if record:
            chain.append(record)
        scheme = scheme.parent_scheme

    if not chain:
        raise Exception("No commission configured")

    final = {}

    for role, field in ROLE_FIELD_MAP.items():
        for record in chain:
            value = getattr(record, field)
            if value is not None:
                final[role] = value
                break

    return final


def calculate_commission_earnings(absolute: dict):
    """
    absolute = {
        ADMIN: 10,
        WHITE_LABEL: 8,
        DISTRIBUTOR: 4,
        RETAILER: 2
    }
    """
    ordered = sorted(
        absolute.items(),
        key=lambda x: ROLE_LEVEL[x[0]]
    )

    earnings = {}

    for i in range(len(ordered)):
        role, value = ordered[i]
        if i == len(ordered) - 1:
            earnings[role] = value
        else:
            earnings[role] = value - ordered[i + 1][1]

    return earnings


def calculate_commission(amount, percent, commission_type):
    if commission_type == CommissionTypeEnum.PERCENTAGE:
        return round((amount * percent) / 100, 2)
    return round(percent, 2)



def settle_commission(db: Session, transaction: Transaction):
    user = db.query(User).get(transaction.user_id)

    # Step 1: resolve absolute commission using scheme hierarchy
    absolute = resolve_absolute_commission(
        db=db,
        scheme=user.scheme,
        service_id=transaction.service_id
    )

    # Step 2: calculate per-role earnings
    earnings = calculate_commission_earnings(absolute)

    # Step 3: walk user hierarchy and create ledger entries
    current = user
    while current:
        role_enum = RoleEnum[current.role.name]

        percent = earnings.get(role_enum)
        if percent and percent > 0:
            commission_amount = calculate_commission(
                transaction.amount,
                percent,
                CommissionTypeEnum.PERCENTAGE
            )

            ledger = CommissionLedger(
                transaction_id=transaction.id,
                user_id=current.id,
                role=role_enum,   # ENUM, not string
                scheme_id=current.scheme_id,
                service_id=transaction.service_id,
                commission_type=CommissionTypeEnum.PERCENTAGE,
                commission_percent=percent,
                commission_amount=commission_amount
            )

            db.add(ledger)

        current = current.parent
