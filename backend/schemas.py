from pydantic import BaseModel, Field
from typing import List, Optional, Dict

class Big5Trait(BaseModel):
    score: int = Field(..., description="Score from 0-100")
    level: str = Field(..., description="High, Moderate, or Low")
    description: str = Field(..., description="Qualitative analysis of this trait")

class Big5Analysis(BaseModel):
    openness: Big5Trait
    conscientiousness: Big5Trait
    extraversion: Big5Trait
    agreeableness: Big5Trait
    neuroticism: Big5Trait

class VARKProfile(BaseModel):
    primary_style: str
    scores: Dict[str, int]
    description: str

class LearningProfile(BaseModel):
    vark: VARKProfile
    growth_mindset_score: int
    grit_score: int
    resilience_level: str

class PsychologicalReport(BaseModel):
    student_id: str
    summary: str
    big5_analysis: Big5Analysis
    learning_profile: LearningProfile
    strengths: List[str]
    areas_for_growth: List[str]
    tailored_recommendations: List[str]

class ChatMessage(BaseModel):
    role: str # 'user' or 'assistant'
    content: str
    timestamp: Optional[float] = None

class SessionState(BaseModel):
    session_id: str
    history: List[ChatMessage] = []
    is_complete: bool = False
    confidence_scores: Dict[str, float] = {} # Tracking trait coverage
