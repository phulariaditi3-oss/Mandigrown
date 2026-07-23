from fastapi import APIRouter, HTTPException, Depends
from routers.dependencies import get_current_user
import services.supabase_service as supabase_service

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/signup")
def signup(payload: dict):
    """Register a new user (farmer or buyer)."""
    email = payload.get("email")
    password = payload.get("password")
    full_name = payload.get("full_name")
    role = payload.get("role", "farmer")
    
    if not email or not password or not full_name:
        raise HTTPException(status_code=400, detail="Email, password, and full name are required")
        
    if role not in ("farmer", "buyer", "mandi_operator"):
        raise HTTPException(status_code=400, detail="Invalid role. Must be 'farmer', 'buyer', or 'mandi_operator'")
        
    result = supabase_service.sign_up_user(email, password, full_name, role)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result.get("error", "Sign up failed"))
        
    return result

@router.post("/login")
def login(payload: dict):
    """Authenticate existing user."""
    email = payload.get("email")
    password = payload.get("password")
    
    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password are required")
        
    result = supabase_service.sign_in_user(email, password)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result.get("error", "Invalid credentials"))
        
    return result

@router.get("/me")
def get_me(current_user: dict = Depends(get_current_user)):
    """Retrieve details of the currently logged-in user."""
    return {"success": True, "user": current_user}
