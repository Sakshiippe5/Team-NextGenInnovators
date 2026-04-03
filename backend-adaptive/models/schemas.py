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
    speed: str
    behavior: str

class SessionSummary(BaseModel):
    final_level: float
    improvement: str
    weak_concepts: List[str]
    confidence_trend: str
    behavior_profile: str
    learning_dna: LearningDNA
    roadmap: List[str]
