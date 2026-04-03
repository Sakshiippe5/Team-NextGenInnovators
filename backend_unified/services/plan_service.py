from backend_unified.models.schemas import TestPlanRequest, TestPlanResponse, TestPlanItem
from backend_unified.services.exam_context_service import get_exam_config
from backend_unified.services.trait_adapter_service import map_traits
from backend_unified.utils.logger import get_logger

logger = get_logger("plan_service")

def generate_test_plan(request: TestPlanRequest) -> TestPlanResponse:
    """
    Generates an adaptive test plan bounded by Exam Config and Trait Bias.
    """
    logger.info(f"Generating test plan for Exam: {request.exam_type}")
    plan_items = []
    
    # 1. Fetch Constraints
    exam_config = get_exam_config(request.exam_type or "STANDARD")
    bloom_dist = exam_config.get("bloom_distribution", {})
    
    # 2. Map Traits
    trait_bias = {}
    if request.trait_profile:
        trait_bias = map_traits(request.trait_profile)
    
    for breakdown in request.topics:
        base_questions = request.marking_scheme.get("default_questions", 5)
        
        # Determine question types locally based on traits
        q_types = ["mcq", "conceptual", "application"]
        learning_style = trait_bias.get("learning_style", "standard")
        if learning_style == "auditory":
            q_types.append("explanation-heavy")
        elif learning_style == "visual":
            q_types.append("scenario-visual")
            
        # Flatten trait_bias to Dict[str, str] for schema compliance
        flat_bias = {k: ", ".join(v) if isinstance(v, list) else str(v) for k, v in trait_bias.items()}
        
        plan_items.append(
            TestPlanItem(
                topic=breakdown.topic,
                num_questions=base_questions,
                types=q_types,
                bloom_distribution=bloom_dist,
                trait_bias=flat_bias
            )
        )
        
    return TestPlanResponse(test_plan=plan_items)
