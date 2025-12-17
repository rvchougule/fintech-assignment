from app.core.database import SessionLocal
from app.models import User
from app.utils.auth import hash_password


SUPERADMIN_EMAIL = "rohanchougule364@gmail.com"
NEW_PASSWORD = "SuperAdmin@123"   


def fix_password():
    db = SessionLocal()

    try:
        user = db.query(User).filter(User.email == SUPERADMIN_EMAIL).first()

        if not user:
            print("❌ SuperAdmin user not found")
            return

        # Hash password
        user.password = hash_password(NEW_PASSWORD)

        db.commit()
        print("✅ SuperAdmin password updated successfully")

    except Exception as e:
        db.rollback()
        print("❌ Error:", str(e))

    finally:
        db.close()


if __name__ == "__main__":
    fix_password()
