from backend.models.adaptive_context import AdaptiveContext
from backend.models.schemas import SubmissionRequest, AnswerEvaluationResponse, Question
from backend.services.learning_state_service import LearningStateService
from backend.services.question_strategy import QuestionStrategy
from backend.services.explainability_service import ExplainabilityService
from backend.services.question_service import generate_question
from backend.utils.logger import get_logger

logger = get_logger("session_service")

# In-memory store for contexts in lieu of DB
session_store = {}

class SessionService:
    @staticmethod
    def initialize_session(user_id: str, topic: str, concept: str) -> AdaptiveContext:
        context = AdaptiveContext(user_id=user_id, current_topic=topic, current_concept=concept)
        session_store[user_id] = context
        return context

    @staticmethod
    def get_context(user_id: str) -> AdaptiveContext:
        if user_id not in session_store:
            # Fallback mock setup
            return SessionService.initialize_session(user_id, "Probability", "Conditional Probability")
        return session_store[user_id]

    @staticmethod
    def submit_answer(submission: SubmissionRequest) -> AnswerEvaluationResponse:
        """
        Discrete endpoint logic for evaluating user answer strictly independent of generation
        """
        logger.info(f"Assessing answer for user {submission.user_id}")
        context = SessionService.get_context(submission.user_id)
        
        # 1. Evaluate previous question
        is_correct = False
        if context.current_question_answer:
            is_correct = submission.user_answer.strip().lower() == context.current_question_answer.strip().lower()
            logger.info(f"Evaluation: '{submission.user_answer}' vs '{context.current_question_answer}' -> Correct: {is_correct}")
        
        # 2. Update Continuous State Loop
        LearningStateService.update_state_after_attempt(context, is_correct, submission.time_taken, "conceptual")
        
        # 3. Formulate insight based on internal engine traces
        strategy_params = QuestionStrategy.determine_next_question_params(context)
        explanation = ExplainabilityService.generate_explanation(strategy_params["decision_dict"], strategy_params["trace"])
        insight = explanation.reason_trace[-1] # Grabs final human readable trace line
        
        resp = AnswerEvaluationResponse(
            is_correct=is_correct,
            correct_answer=context.current_question_answer or "No previous answer stored",
            explanation=context.current_question_explanation or "No explanation stored",
            insight=insight
        )
        
        # Write back to mocked DB Dict
        session_store[submission.user_id] = context
        return resp

    @staticmethod
    def get_next_question(user_id: str) -> Question:
        """
        Discrete logic for pulling strategy params off the current user context and generating standard structure
        """
        logger.info(f"Generating next algorithm question for {user_id}")
        context = SessionService.get_context(user_id)
        
        strategy_params = QuestionStrategy.determine_next_question_params(context)
        
        question = generate_question(
            topic=strategy_params["topic"],
            concept=strategy_params["concept"],
            difficulty=strategy_params["difficulty"],
            q_type=strategy_params["type"]
        )
        
        # Store structural evaluation pieces onto the context state so /answer can catch it
        context.current_question_answer = question.correct_answer
        context.current_question_explanation = question.explanation
        context.current_topic = question.topic
        context.current_concept = strategy_params["concept"]
        
        session_store[user_id] = context
        return question
