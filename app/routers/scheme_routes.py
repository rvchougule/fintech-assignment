from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models import Scheme, RoleEnum, User
from app.routers.auth_routes import get_current_user
from app.schema.scheme import *

router = APIRouter(prefix="/scheme", tags=["Scheme Management"])

@router.post("/", response_model=SchemeResponse)
def create_scheme(
    payload: SchemeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # -----------------------------
    # Role-based rules
    # -----------------------------
    allowed_roles = [RoleEnum.SUPER_ADMIN, RoleEnum.ADMIN, RoleEnum.WHITE_LABEL]
    if current_user.role.name not in allowed_roles:
        raise HTTPException(
            status_code=403,
            detail="You are not allowed to create schemes"
        )

    # Determine parent_scheme_id
    if current_user.role.name == RoleEnum.SUPER_ADMIN:
        parent_scheme_id = None
    else:
        # ADMIN / WHITE_LABEL: must have a scheme assigned
        if not current_user.scheme_id:
            raise HTTPException(
                status_code=400,
                detail="You are not assigned to any scheme"
            )
        parent_scheme_id = current_user.scheme_id  # Automatically assign

    # -----------------------------
    # Duplicate check
    # -----------------------------
    if db.query(Scheme).filter(Scheme.name == payload.name).first():
        raise HTTPException(
            status_code=400,
            detail="Scheme already exists"
        )

    # -----------------------------
    # Create scheme
    # -----------------------------
    scheme = Scheme(
        name=payload.name,
        parent_scheme_id=parent_scheme_id,
        created_by=current_user.id
    )

    db.add(scheme)
    db.commit()
    db.refresh(scheme)

    return scheme





# -----------------------------
# GET ALL SCHEMES
# -----------------------------
@router.get("/", response_model=List[SchemeResponse])
def get_schemes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role.name == RoleEnum.SUPER_ADMIN:
        return db.query(Scheme).all()

    # Non-superadmin sees only own tree
    return db.query(Scheme).filter(
        Scheme.created_by == current_user.id
    ).all()



# -----------------------------
# GET SCHEME BY ID
# -----------------------------
@router.get("/{scheme_id}", response_model=SchemeResponse)
def get_scheme(
    scheme_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    scheme = db.query(Scheme).filter(Scheme.id == scheme_id).first()

    if not scheme:
        raise HTTPException(status_code=404, detail="Scheme not found")

    return scheme



# -----------------------------
# UPDATE SCHEME
# -----------------------------
@router.put("/{scheme_id}", response_model=SchemeResponse)
def update_scheme(
    scheme_id: int,
    payload: SchemeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    scheme = db.query(Scheme).filter(Scheme.id == scheme_id).first()

    if not scheme:
        raise HTTPException(status_code=404, detail="Scheme not found")

    if current_user.role.name not in [
        RoleEnum.SUPER_ADMIN,
        RoleEnum.ADMIN,
        RoleEnum.WHITE_LABEL
    ]:
        raise HTTPException(
            status_code=403,
            detail="You cannot update schemes"
        )

    if payload.name is not None:
        scheme.name = payload.name

    if payload.is_active is not None:
        scheme.is_active = payload.is_active

    db.commit()
    db.refresh(scheme)

    return scheme


# -----------------------------
# DELETE SCHEME
# -----------------------------
@router.delete("/{scheme_id}")
def delete_scheme(
    scheme_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    scheme = db.query(Scheme).filter(Scheme.id == scheme_id).first()

    if not scheme:
        raise HTTPException(status_code=404, detail="Scheme not found")

    # Root scheme protection
    if scheme.parent_scheme_id is None and current_user.role.name != RoleEnum.SUPER_ADMIN:
        raise HTTPException(
            status_code=403,
            detail="Only Super Admin can delete root schemes"
        )

    # Child protection
    if db.query(Scheme).filter(
        Scheme.parent_scheme_id == scheme.id
    ).count() > 0:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete scheme with child schemes"
        )

    db.delete(scheme)
    db.commit()

    return {"message": "Scheme deleted successfully"}

