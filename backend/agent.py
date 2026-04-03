import openai
from typing import List, Dict, Any, Optional
from schemas import ChatMessage, PsychologicalReport, SessionState
from config import get_settings
import json
import re

settings = get_settings()

class PsychAgent:
    def __init__(self):
        self.client = openai.OpenAI(
            api_key=settings.GROK_API_KEY,
            base_url="https://api.groq.com/openai/v1"
        )
        self.system_prompt = """You are PsychAgent — a razor-sharp psychological profiler for students.

GOAL: Build a complete profile (Big Five, VARK, Grit, Growth Mindset) in 5-8 turns.

STRICT RULES:
1. Ask ONLY ONE short question per turn. MAX 2 sentences.
2. NO long preambles. NO paragraphs. NO summaries of what you've learned.
3. DO NOT repeat or paraphrase the user's answer back to them.
4. Each question must probe 2+ traits simultaneously (multi-trait probing).
5. If a trait is already clear, NEVER ask about it again — pivot immediately.
6. Use casual, relatable scenarios — NOT clinical or academic language.
7. After 5-8 exchanges, say exactly: "Thanks! I have enough to build your profile. Type 'report' whenever you're ready."

FRAMEWORKS TO COVER:
- Big Five: Openness, Conscientiousness, Extraversion, Agreeableness, Neuroticism
- VARK: Visual, Auditory, Read/Write, Kinesthetic
- Grit: Passion & Perseverance for long-term goals
- Growth Mindset: Fixed vs growth belief about intelligence
- Academic Confidence & Motivation

EXAMPLE GOOD QUESTIONS:
- "When you're stuck on something hard, do you push through or switch to something else?"
- "Group project — do you lead, follow, or work alone?"
- "New topic: watch a video, read about it, or just try it hands-on?"

EXAMPLE BAD QUESTIONS (NEVER DO THIS):
- "That's a great point! It sounds like you really value... Now, let me ask you about..." (too long)
- "On a scale of 1-5, how much do you agree with..." (boring survey)

START by asking one punchy question. No introduction needed."""

    async def get_next_question(self, history: List[ChatMessage]) -> str:
        """Determines the next best question to ask based on history."""
        messages = [{"role": "system", "content": self.system_prompt}]
        for msg in history:
            messages.append({"role": msg.role, "content": msg.content})
        
        response = self.client.chat.completions.create(
            model=settings.MODEL_NAME,
            messages=messages,
            temperature=0.7,
            max_tokens=150  # Hard cap to force brevity
        )
        return response.choices[0].message.content

    async def generate_report(self, history: List[ChatMessage]) -> dict:
        """Synthesizes the entire conversation into a structured JSON report."""
        
        transcript = "\n".join([f"{m.role}: {m.content}" for m in history])
        
        # Keep JSON schema separate from the f-string to avoid {{ }} escaping corruption
        json_schema = '''{
  "student_id": "STU-001",
  "summary": "A determined and independent learner who prefers visual content and shows strong perseverance.",
  "big5_analysis": {
    "openness": {"score": 72, "level": "High", "description": "Shows curiosity and preference for exploring new ideas independently."},
    "conscientiousness": {"score": 65, "level": "Moderate", "description": "Demonstrates goal-oriented behavior with moderate organizational skills."},
    "extraversion": {"score": 35, "level": "Low", "description": "Prefers solitary work over group settings."},
    "agreeableness": {"score": 58, "level": "Moderate", "description": "Cooperative but values independence."},
    "neuroticism": {"score": 45, "level": "Moderate", "description": "Experiences some stress but manages it effectively."}
  },
  "learning_profile": {
    "vark": {
      "primary_style": "Visual",
      "scores": {"visual": 80, "auditory": 40, "read_write": 50, "kinesthetic": 60},
      "description": "Learns best through videos and visual diagrams."
    },
    "growth_mindset_score": 75,
    "grit_score": 70,
    "resilience_level": "High"
  },
  "strengths": ["Strong perseverance", "Self-directed learner", "Growth-oriented mindset"],
  "areas_for_growth": ["Social collaboration skills", "Stress management", "Seeking help when needed"],
  "tailored_recommendations": ["Join study groups to build collaboration skills", "Use visual mind-maps for complex topics", "Practice mindfulness for exam stress"]
}'''

        system_msg = "You are a clinical psychologist who outputs psychological reports strictly as JSON. You must respond with ONLY valid JSON, no other text."
        
        user_msg = (
            "Analyze this student interview transcript and generate a psychological profile.\n\n"
            f"TRANSCRIPT:\n{transcript}\n\n"
            f"Use this exact JSON structure (replace example values with your actual analysis):\n{json_schema}\n\n"
            "RULES:\n"
            "- Replace ALL example values with real analysis based on the transcript.\n"
            "- Scores must be integers from 0 to 100.\n"
            "- Level must be exactly one of: High, Moderate, Low.\n"
            "- Return ONLY the JSON object. No markdown, no explanation."
        )

        messages = [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg}
        ]

        # Try up to 2 times
        last_error = None
        for attempt in range(2):
            try:
                response = self.client.chat.completions.create(
                    model=settings.MODEL_NAME,
                    messages=messages,
                    temperature=0.1 if attempt > 0 else 0.2,  # Lower temp on retry
                    max_tokens=2000,
                    response_format={"type": "json_object"}
                )
                
                raw = response.choices[0].message.content.strip()
                report_data = json.loads(raw)
                return report_data
                
            except openai.BadRequestError:
                # Groq JSON mode failed — fall back to free-form + manual parse
                response = self.client.chat.completions.create(
                    model=settings.MODEL_NAME,
                    messages=messages,
                    temperature=0.1,
                    max_tokens=2000
                )
                raw = response.choices[0].message.content.strip()
                report_data = self._extract_json(raw)
                return report_data
                
            except json.JSONDecodeError as e:
                last_error = e
                continue
        
        raise Exception(f"Failed to parse report after 2 attempts: {last_error}")
    
    def _extract_json(self, text: str) -> dict:
        """Robustly extract JSON from LLM output that may contain extra text."""
        # 1. Try direct parse
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
        
        # 2. Strip markdown fences
        if "```" in text:
            match = re.search(r'```(?:json)?\s*\n?(.*?)```', text, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(1).strip())
                except json.JSONDecodeError:
                    pass
        
        # 3. Find the outermost { ... } block
        start = text.find('{')
        end = text.rfind('}')
        if start != -1 and end != -1 and end > start:
            candidate = text[start:end + 1]
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                # 4. Try fixing common issues: trailing commas
                fixed = re.sub(r',\s*}', '}', candidate)
                fixed = re.sub(r',\s*]', ']', fixed)
                try:
                    return json.loads(fixed)
                except json.JSONDecodeError:
                    pass
        
        raise Exception(f"Could not extract valid JSON from LLM response. Raw output: {text[:500]}")

# Global instance for sessions
sessions: Dict[str, SessionState] = {}
agent = PsychAgent()
