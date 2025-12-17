from sqlalchemy.orm import Session
from app.core.database import SessionLocal, Base, engine
from app.models import RoleEnum, Role, Service, User
from app.utils.auth import hash_password

# -------------------------
# Create all tables
# -------------------------
Base.metadata.create_all(bind=engine)

# -------------------------
# Seed Roles, Services, Super Admin
# -------------------------
def seed_core_data():
    db: Session = SessionLocal()
    try:
        # -------------------------
        # 1️⃣ Roles
        # -------------------------
        roles = [
            {"name": RoleEnum.SUPER_ADMIN, "level": 1},
            {"name": RoleEnum.ADMIN, "level": 2},
            {"name": RoleEnum.WHITE_LABEL, "level": 3},
            {"name": RoleEnum.MASTER_DISTRIBUTOR, "level": 4},
            {"name": RoleEnum.DISTRIBUTOR, "level": 5},
            {"name": RoleEnum.RETAILER, "level": 6},
            {"name": RoleEnum.CUSTOMER, "level": 7},
        ]
        for r in roles:
            role_obj = db.query(Role).filter(Role.name == r["name"]).first()
            if not role_obj:
                db.add(Role(name=r["name"], level=r["level"]))
        db.commit()

        # -------------------------
        # 2️⃣ Services
        # -------------------------
        services = [
            {"category": "Recharge", "code": "MOBILE", "name": "Mobile Recharge"},
            {"category": "Recharge", "code": "DTH", "name": "DTH Recharge"},
            {"category": "Banking", "code": "AEPS", "name": "AEPS Service"},
            {"category": "Banking", "code": "DMT", "name": "DMT Service"},
        ]
        for s in services:
            service_obj = db.query(Service).filter(Service.code == s["code"]).first()
            if not service_obj:
                db.add(Service(category=s["category"], code=s["code"], name=s["name"]))
        db.commit()

        # -------------------------
        # 3️⃣ Super Admin User
        # -------------------------
        super_admin_role = db.query(Role).filter(Role.name == RoleEnum.SUPER_ADMIN).first()
        super_admin = db.query(User).filter(User.name == "Super Admin").first()
        if not super_admin:
            super_admin = User(
                name="Super Admin",
                email="rohanchougule364@gmail.com",
                password= hash_password("SuperAdmin@123"),
                role_id=super_admin_role.id,
                parent_id=None,
                scheme_id=None,  # No scheme assigned yet
                is_active=True
            )
            db.add(super_admin)
            db.commit()

        print("✅ Roles, Services, and Super Admin seeded successfully!")

    finally:
        db.close()


# -------------------------
# Run seed
# -------------------------
if __name__ == "__main__":
    seed_core_data()
