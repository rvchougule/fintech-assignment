from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import User, RoleEnum, Scheme
from app.routers.auth_routes import get_current_user
from passlib.context import CryptContext
from app.schema.member import UserCreate, UserResponse, UserUpdateStatus

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter(prefix="/users", tags=["User Management"])


# ---------------------------
# HELPER FUNCTION TO CHECK HIERARCHY
# ---------------------------
def can_onboard(parent_role: str, child_role: str) -> bool:
    """Check if a parent_role can onboard child_role"""
    hierarchy = {
        RoleEnum.SUPER_ADMIN: [
            RoleEnum.ADMIN, 
            RoleEnum.WHITE_LABEL, 
            RoleEnum.MASTER_DISTRIBUTOR,
            RoleEnum.DISTRIBUTOR, 
            RoleEnum.RETAILER, 
            RoleEnum.CUSTOMER ],
        RoleEnum.ADMIN: [RoleEnum.WHITE_LABEL, 
            RoleEnum.MASTER_DISTRIBUTOR,
            RoleEnum.DISTRIBUTOR, 
            RoleEnum.RETAILER, 
            RoleEnum.CUSTOMER ],
        RoleEnum.WHITE_LABEL: [ 
            RoleEnum.MASTER_DISTRIBUTOR,
            RoleEnum.DISTRIBUTOR, 
            RoleEnum.RETAILER, 
            RoleEnum.CUSTOMER ],
        RoleEnum.MASTER_DISTRIBUTOR: [
            RoleEnum.DISTRIBUTOR, 
            RoleEnum.RETAILER, 
            RoleEnum.CUSTOMER ],
        RoleEnum.DISTRIBUTOR: [RoleEnum.RETAILER, RoleEnum.CUSTOMER ],
        RoleEnum.RETAILER: [RoleEnum.CUSTOMER], 
    }
    return child_role in hierarchy.get(parent_role, [])

ROLE_LEVEL_MAP = {
    1:RoleEnum.SUPER_ADMIN,
    2:RoleEnum.ADMIN,
    3:RoleEnum.WHITE_LABEL,
    4:RoleEnum.MASTER_DISTRIBUTOR,
    5:RoleEnum.DISTRIBUTOR,
    6:RoleEnum.RETAILER,
    7:RoleEnum.CUSTOMER 
}

# ---------------------------
# CREATE / ONBOARD USER
# ---------------------------
@router.post("/onboard", response_model=UserResponse)
def onboard_user(payload: UserCreate,
                 db: Session = Depends(get_db),
                 current_user: User = Depends(get_current_user)):

    # Prevent multiple SUPER_ADMINs
    if payload.role_id == RoleEnum.SUPER_ADMIN:
        existing_superadmin = db.query(User).filter(User.role_id == RoleEnum.SUPER_ADMIN).first()
        if existing_superadmin:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="SUPER_ADMIN already exists")

    # Check hierarchy: only parent can onboard child
    child_role = payload.role_id
    parent_role = current_user.role.name
    if not can_onboard(parent_role,ROLE_LEVEL_MAP[child_role]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"{parent_role} cannot onboard a user with role {child_role}"
        )

    # Check if email exists
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")

    # Check scheme if provided
    if payload.scheme_id:
        scheme = db.query(Scheme).filter(Scheme.id == payload.scheme_id).first()
        if not scheme:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scheme not found")

    # Hash password
    hashed_password = pwd_context.hash(payload.password)

    user = User(
        name=payload.name,
        email=payload.email,
        password=hashed_password,
        role_id=payload.role_id,
        scheme_id=payload.scheme_id,
        parent_id=current_user.id,  # set parent as the current user
        created_by=current_user.id
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# ---------------------------
# DELETE USER
# ---------------------------
@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user)):

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Only the creator or SUPER_ADMIN can delete
    if current_user.role.name != RoleEnum.SUPER_ADMIN and user.created_by != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authorized to delete this user")

    db.delete(user)
    db.commit()
    return {"message": f"User {user.name} deleted successfully"}


# ---------------------------
# ACTIVATE / DEACTIVATE USER
# ---------------------------
@router.put("/status/{user_id}", response_model=UserResponse)
def update_user_status(user_id: int, payload: UserUpdateStatus,
                       db: Session = Depends(get_db),
                       current_user: User = Depends(get_current_user)):

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Only the creator or SUPER_ADMIN can update status
    if current_user.role.name != RoleEnum.SUPER_ADMIN and user.created_by != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authorized to change status of this user")

    user.is_active = payload.is_active
    db.commit()
    db.refresh(user)
    return user
