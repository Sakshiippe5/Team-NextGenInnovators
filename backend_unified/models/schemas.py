from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class Question(BaseModel):
    id: str
    topic: str
    difficulty: str
    type: str # mcq, conceptual, applied
    question_text: str
    options: Optional[List[str]] = None
    correct_answer: str
    explanation: str

class TopicBreakdown(BaseModel):
    topic: str
    subtopics: List[str]

class SyllabusUploadResponse(BaseModel):
    topics: List[TopicBreakdown]
    
class TestPlanItem(BaseModel):
    topic: str
    num_questions: int
    types: List[str]

class TestPlanRequest(BaseModel):
    topics: List[TopicBreakdown]
    marking_scheme: dict

class TestPlanResponse(BaseModel):
    test_plan: List[TestPlanItem]

class SessionStartRequest(BaseModel):
    user_id: str
    test_plan: List[TestPlanItem]

class SubmissionRequest(BaseModel):
    user_id: str
    question_id: str
    user_answer: str
    time_taken: float # seconds

class AnswerEvaluationResponse(BaseModel):
    is_correct: bool
    correct_answer: str
    explanation: str
    insight: Dict[str, str]

class SessionNextRequest(BaseModel):
    user_id: str

class DecisionTrace(BaseModel):
    decision: Dict[str, str]
    reason_trace: List[str]
    structured_insight: Dict[str, str]

class LearningDNA(BaseModel):
    accuracy: int
    topics: Dict[str, float]
    # future behavior vectors

# ---- PSYCHOLOGICAL PROFILING SCHEMAS ---- #

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

class ProfileSessionState(BaseModel):
    session_id: str
    history: List[ChatMessage] = []
    is_complete: bool = False
    confidence_scores: Dict[str, float] = {}

class SessionSummary(BaseModel):
    final_level: float
    improvement: str
    weak_concepts: List[str]
    confidence_trend: str
    behavior_profile: str
    learning_dna: LearningDNA
    roadmap: List[str]
