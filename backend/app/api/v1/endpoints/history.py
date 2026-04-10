from fastapi import APIRouter, Depends, Query, HTTPException
from typing import List, Any, Optional
from ....services.history_service import history_service
from ....services.report_service import report_service
from ...deps import get_current_user
from ....models.user import UserOut
from fastapi.responses import StreamingResponse
from datetime import datetime

router = APIRouter()

@router.get("/", response_model=List[Any])
async def read_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, le=100),
    input_type: Optional[str] = None,
    current_user: UserOut = Depends(get_current_user)
) -> Any:
    """
    Retrieve past emotional analyses for the current user.
    """
    return await history_service.get_user_history(
        str(current_user["_id"]), 
        skip=skip, 
        limit=limit, 
        input_type=input_type
    )

@router.get("/stats")
async def read_stats(
    current_user: UserOut = Depends(get_current_user)
) -> Any:
    """
    Get aggregated emotional statistics for the dashboard.
    """
    return await history_service.get_emotional_stats(str(current_user["_id"]))

@router.get("/{analysis_id}")
async def read_analysis_detail(
    analysis_id: str,
    current_user: UserOut = Depends(get_current_user)
) -> Any:
    """
    Get details of a specific past analysis.
    """
    result = await history_service.get_analysis_by_id(analysis_id, str(current_user["_id"]))
    if not result:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return result

@router.get("/export/pdf")
async def export_pdf_report(
    start_date: str = Query(..., description="ISO 8601 date, e.g. 2024-01-01"),
    end_date: str = Query(..., description="ISO 8601 date, e.g. 2024-01-31"),
    current_user: UserOut = Depends(get_current_user)
) -> Any:
    """
    Export emotional history as a PDF for a custom date range.
    """
    try:
        start_dt = datetime.fromisoformat(start_date)
        end_dt = datetime.fromisoformat(end_date)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
        
    pdf_buffer = await report_service.generate_pdf_report(
        str(current_user["_id"]), 
        start_dt, 
        end_dt
    )
    
    filename = f"FeelSync_Report_{start_date}_to_{end_date}.pdf"
    
    return StreamingResponse(
        pdf_buffer, 
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
