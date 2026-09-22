from app.schemas.user import UserCreate, UserUpdate, UserLogin, UserResponse, Token, ForgotPasswordRequest
from app.schemas.subject import SubjectCreate, SubjectUpdate, SubjectResponse
from app.schemas.task import AcademicTaskCreate, AcademicTaskUpdate, AcademicTaskResponse, AddStudyTimeRequest
from app.schemas.analytics import OverallProgressMetrics, SubjectProgressMetric, TimeDistributionResponse
from app.schemas.ai_insights import AIInsightsResponse, InsightRecommendation

__all__ = [
    "UserCreate", "UserUpdate", "UserLogin", "UserResponse", "Token", "ForgotPasswordRequest",
    "SubjectCreate", "SubjectUpdate", "SubjectResponse",
    "AcademicTaskCreate", "AcademicTaskUpdate", "AcademicTaskResponse", "AddStudyTimeRequest",
    "OverallProgressMetrics", "SubjectProgressMetric", "TimeDistributionResponse",
    "AIInsightsResponse", "InsightRecommendation"
]
