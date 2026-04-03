from typing import List
from backend_unified.models.adaptive_context import AdaptiveContext
from backend_unified.models.schemas import SessionSummary, LearningDNA
from backend_unified.services.exam_context_service import get_marks_for_bloom
from backend_unified.utils.logger import get_logger

logger = get_logger("report_service")

def generate_session_summary(context: AdaptiveContext) -> SessionSummary:
    """
    Produce the final wrap up and 'Session Summary'.
    """
    logger.info(f"Generating session summary for user {context.user_id}")
    
    accuracy_pct = int(context.rolling_accuracy * 100)
    
    # Extract behavioral profile
    profile = "balanced"
    if "guessing" in context.detected_behaviors:
        profile = "guess-prone"
    if "concept_gap" in context.detected_behaviors:
        profile = "needs foundational review"

    # Identify weak areas based on concept accuracy < 0.5
    weak_concepts = [
        concept for concept, acc in context.concept_accuracies.items() if acc < 0.5
    ]
    
    estimated_score = get_marks_for_bloom(context.current_bloom) * context.streak
    
    dna = LearningDNA(
        accuracy=accuracy_pct,
        speed="fast" if getattr(context, 'average_time_taken', 10) < 15 else "steady",
        behavior=profile,
        estimated_marks=estimated_score
    )
    
    roadmap = [f"Review foundations of {c}" for c in weak_concepts]
    if not roadmap:
        roadmap = ["Ready for next level application concepts!"]
        
    bloom_tracker = {context.current_bloom: float(accuracy_pct)}
    traits = {
        "learning_style": context.traits.get("learning_style", "unknown"),
        "interaction": context.traits.get("interaction_preference", "balanced")
    }
    
    resources = []
    if context.exam_config.get("time_pressure") == "high":
        resources.append("Time Management Drill Set")
    
    summary = SessionSummary(
        final_level=context.current_level,
        improvement="+10%" if context.current_level > 0.5 else "Maintained",
        weak_concepts=weak_concepts,
        confidence_trend="increasing" if context.confidence_score > 0.5 else "fluctuating",
        behavior_profile=profile,
        learning_dna=dna,
        roadmap=roadmap,
        bloom_progress=bloom_tracker,
        trait_alignment=traits,
        resources=resources
    )
    
    return summary
