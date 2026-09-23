"""
Authentication and Role-Based Access Control API Endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, get_current_user
from app.core.security import verify_password, get_password_hash, create_access_token
from app.models.user import User, UserRole
from app.schemas.auth import UserRead, UserCreate, LoginRequest, TokenResponse, DemoRoleSwitchRequest

router = APIRouter(prefix="/auth", tags=["Authentication & RBAC"])

DEMO_PROFILES = {
    UserRole.PROCUREMENT_OFFICER: {
        "username": "procurement_officer",
        "full_name": "Er. Rajesh Kumar",
        "email": "rajesh.kumar@ntpc.co.in",
        "department": "Tender & Contracts Division, NTPC Ltd.",
        "designation": "Executive Engineer (Procurement)",
    },
    UserRole.STANDARDS_AUDITOR: {
        "username": "standards_auditor",
        "full_name": "Dr. S. K. Roy",
        "email": "sk.roy@bis.gov.in",
        "department": "Electrotechnical Standards Department (ETD), BIS",
        "designation": "Scientist E / Senior Standards Officer",
    },
    UserRole.ADMIN: {
        "username": "vigilance_admin",
        "full_name": "Shri A. K. Verma",
        "email": "ak.verma@cvc.gov.in",
        "department": "Central Vigilance Commission (CVC)",
        "designation": "Chief Vigilance & Compliance Officer",
    },
}


@router.post("/login", response_model=TokenResponse, summary="Authenticate officer and issue JWT token")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == request.username).first()
    if not user or not verify_password(request.password, user.hashed_password):
        # Allow instant demo login if testing demo accounts
        role_match = next((r for r, p in DEMO_PROFILES.items() if p["username"] == request.username), None)
        if role_match and request.password in ("normvault123", "password"):
            profile = DEMO_PROFILES[role_match]
            token = create_access_token({
                "sub": profile["username"],
                "role": role_match.value,
                "full_name": profile["full_name"],
                "department": profile["department"],
            })
            return TokenResponse(
                access_token=token,
                user=UserRead(
                    id=1,
                    username=profile["username"],
                    email=profile["email"],
                    full_name=profile["full_name"],
                    role=role_match,
                    department=profile["department"],
                    designation=profile["designation"],
                    is_active=True,
                )
            )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials. Use demo switcher or registered credentials.",
        )

    token = create_access_token({
        "sub": user.username,
        "role": user.role.value,
        "full_name": user.full_name,
        "department": user.department,
    })
    return TokenResponse(access_token=token, user=user)


@router.post("/register", response_model=UserRead, summary="Register a new officer")
def register(request: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter((User.username == request.username) | (User.email == request.email)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username or email already registered.")

    new_user = User(
        username=request.username,
        email=request.email,
        full_name=request.full_name,
        hashed_password=get_password_hash(request.password),
        role=request.role,
        department=request.department,
        designation=request.designation,
        is_active=True,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.get("/me", response_model=UserRead, summary="Retrieve active officer profile")
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/demo-switch", response_model=TokenResponse, summary="Switch active officer persona for live evaluation")
def demo_switch(request: DemoRoleSwitchRequest, db: Session = Depends(get_db)):
    profile = DEMO_PROFILES.get(request.role, DEMO_PROFILES[UserRole.PROCUREMENT_OFFICER])

    # Find or upsert demo user
    user = db.query(User).filter(User.username == profile["username"]).first()
    if not user:
        user = User(
            username=profile["username"],
            email=profile["email"],
            full_name=profile["full_name"],
            hashed_password=get_password_hash("normvault123"),
            role=request.role,
            department=profile["department"],
            designation=profile["designation"],
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    token = create_access_token({
        "sub": user.username,
        "role": user.role.value,
        "full_name": user.full_name,
        "department": user.department,
    })
    return TokenResponse(access_token=token, user=user)
