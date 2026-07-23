from fastapi import Header, HTTPException
import services.supabase_service as supabase_service

async def get_current_user(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authentication token required")
    
    parts = authorization.split(" ")
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid authorization header format. Use 'Bearer <token>'")
        
    token = parts[1]
    result = supabase_service.get_user_from_token(token)
    if not result["success"]:
        raise HTTPException(status_code=401, detail=result.get("error", "Invalid or expired token"))
        
    return result["user"]
