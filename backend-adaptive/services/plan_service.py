from backend.models.schemas import TestPlanRequest, TestPlanResponse, TestPlanItem
from backend.utils.logger import get_logger

logger = get_logger("plan_service")

def generate_test_plan(request: TestPlanRequest) -> TestPlanResponse:
    """
    Non-Adaptive Test Plan Engine
    Acts as the control layer for maximum session bounds.
    """
    logger.info("Generating non-adaptive test plan")
    plan_items = []
    
    for breakdown in request.topics:
        # Logic influenced by marking scheme
        base_questions = request.marking_scheme.get("default_questions", 5)
        
        plan_items.append(
            TestPlanItem(
                topic=breakdown.topic,
                num_questions=base_questions,
                types=["mcq", "conceptual", "application"]
            )
        )
        
    return TestPlanResponse(test_plan=plan_items)
