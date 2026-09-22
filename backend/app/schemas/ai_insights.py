from typing import List, Optional
from pydantic import BaseModel

class InsightRecommendation(BaseModel):
    category: str        # 'time_management', 'priority_alert', 'schedule_optimization', 'motivation'
    type: str            # 'warning', 'success', 'info', 'alert'
    title: str
    message: str
    action_suggested: Optional[str] = None
    subject_id: Optional[int] = None
    subject_name: Optional[str] = None

class AIInsightsResponse(BaseModel):
    summary: str
    generated_by: str   # 'Gemini AI Engine' ou 'EduTrack Rule-Based AI Engine'
    recommendations: List[InsightRecommendation]
    critical_alerts: List[str]
    weekly_focus: List[str]
