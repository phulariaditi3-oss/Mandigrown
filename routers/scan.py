from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from routers.dependencies import get_current_user
import services.grading_service as grading_service
import services.supabase_service as supabase_service
from utils.weight_estimator import estimate_weight
from utils.storage_recs import get_storage_recommendation

router = APIRouter(prefix="/api", tags=["scan"])

@router.post("/grade")
async def grade_produce(
    file: UploadFile = File(...), 
    current_user: dict = Depends(get_current_user)
):
    """
    Uploads crop photo, performs computer-vision-based AI grading, 
    estimates weight/size, retrieves storage tips, stores record, and returns results.
    """
    # 1. Read file contents
    try:
        contents = await file.read()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read uploaded file: {str(e)}")
        
    # 2. Run grading engine
    grading_result = grading_service.analyze_produce(contents)
    if not grading_result["success"]:
        raise HTTPException(status_code=500, detail=grading_result.get("error", "Grading engine error"))
        
    # 3. Add Feature 2: Weight Estimation and Feature 5: Storage Recommendation
    produce_type = grading_result.get("produce_type", "Unknown")
    size_score = grading_result.get("metrics", {}).get("size_score", 50)
    
    weight_info = estimate_weight(produce_type, size_score)
    storage_info = get_storage_recommendation(produce_type)
    
    # Inject into result for DB save and frontend
    grading_result["weight_info"] = weight_info
    grading_result["storage_info"] = storage_info
        
    # 4. Save to Storage (Supabase Storage or local mock folder)
    try:
        image_url = supabase_service.upload_produce_image(contents, file.filename, current_user["id"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to store scan image: {str(e)}")
        
    # 5. Save to Database Scan History table
    try:
        db_record = supabase_service.save_scan_record(current_user["id"], grading_result, image_url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save scan record: {str(e)}")
        
    return {
        "success": True,
        "scan": db_record
    }

@router.get("/history")
def get_history(current_user: dict = Depends(get_current_user)):
    """Fetches list of previous scans for the logged-in user."""
    history = supabase_service.get_user_scan_history(current_user["id"])
    return {
        "success": True,
        "scans": history
    }
