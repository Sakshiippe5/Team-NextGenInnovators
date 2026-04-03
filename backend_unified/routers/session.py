from fastapi import APIRouter
from backend_unified.models.schemas import SubmissionRequest, AnswerEvaluationResponse, Question, SessionStartRequest, SessionNextRequest
from backend_unified.services.session_service import SessionService

router = APIRouter()

@router.post("/start", status_code=200)
def start_session(request: SessionStartRequest):
    """
    Initializes standard state context inside the Session Service.
    """
    first_topic = request.test_plan[0].topic if request.test_plan else "Default"
    SessionService.initialize_session(
        user_id=request.user_id,
        topic=first_topic,
        concept="Foundations"
    )
    return {"message": "Session tracking established", "user_id": request.user_id}

@router.post("/answer", response_model=AnswerEvaluationResponse)
def submit_answer(submission: SubmissionRequest):
    """
    Evaluates users latest question against the context, provides insight and updates memory graph.
    """
    return SessionService.submit_answer(submission)

@router.post("/next", response_model=Question)
def next_question(request: SessionNextRequest):
    """
    Rides off the back of the newly updated context from /answer to generate the next difficulty payload.
    """
    return SessionService.get_next_question(request.user_id)
