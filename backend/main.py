from fastapi import FastAPI, HTTPException, Body
from typing import List, Dict, Optional
import uuid
import time
from schemas import ChatMessage, SessionState, PsychologicalReport, Big5Analysis, Big5Trait, VARKProfile, LearningProfile
from agent import agent, sessions # Global instances from agent.py
from config import get_settings

app = FastAPI(title="Psychological Profiling Agent")
settings = get_settings()

@app.get("/")
async def root():
    """Root endpoint — redirects to API docs."""
    return {
        "app": "🧠 PsychProfileAgent",
        "status": "running",
        "docs": "Visit /docs for interactive Swagger UI",
        "endpoints": {
            "POST /session/start": "Begin a new profiling session",
            "POST /session/chat": "Send a message and get AI response",
            "PATCH /session/edit": "Edit a previous answer",
            "POST /session/rewind": "Rewind to a specific turn",
            "GET /session/report": "Generate final psychological report"
        }
    }

@app.post("/session/start", response_model=SessionState)
async def start_session():
    """Initializes a new session and sends the first question."""
    session_id = str(uuid.uuid4())
    first_msg = await agent.get_next_question([])
    
    new_session = SessionState(
        session_id=session_id,
        history=[ChatMessage(role="assistant", content=first_msg, timestamp=time.time())]
    )
    sessions[session_id] = new_session
    return new_session

@app.post("/session/chat", response_model=SessionState)
async def chat(session_id: str, message: str = Body(..., embed=True)):
    """Sends a user message and gets a dynamic follow-up."""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    
    # 1. Add user message
    session.history.append(ChatMessage(role="user", content=message, timestamp=time.time()))
    
    # 2. Get AI response
    ai_response_text = await agent.get_next_question(session.history)
    
    # 3. Add AI message
    session.history.append(ChatMessage(role="assistant", content=ai_response_text, timestamp=time.time()))
    
    return session

@app.patch("/session/edit", response_model=SessionState)
async def edit_message(session_id: str, index: int, new_content: str = Body(..., embed=True)):
    """Updates a previous USER message by index and re-triggers the next AI turn."""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    
    # Safety Check: only edit user messages
    if index >= len(session.history) or session.history[index].role != "user":
        raise HTTPException(status_code=400, detail="Invalid message index for edit")

    # Update content
    session.history[index].content = new_content
    
    # Truncate conversation from the point of edit to keep flow logical
    # Actually, user said 're-read context', but usually in chat, you want to redo the turns following the edit.
    # To keep it efficient, we'll keep the full history but the next AI turn will reflect the change.
    
    # Regenerate follow-up from that point onwards (logic varies, but for MVP we'll just re-prompt based on full history)
    ai_response_text = await agent.get_next_question(session.history)
    session.history.append(ChatMessage(role="assistant", content=ai_response_text, timestamp=time.time()))
    
    return session

@app.post("/session/rewind", response_model=SessionState)
async def rewind(session_id: str, index: int):
    """Truncates conversation history back to a specific index."""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    if index < 0 or index >= len(session.history):
        raise HTTPException(status_code=400, detail="Invalid index")
    
    session.history = session.history[:index + 1]
    return session

@app.get("/session/report")
async def get_report(session_id: str):
    """Synthesizes the entire history into a final JSON report."""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    if len(session.history) < 2:
        raise HTTPException(status_code=400, detail="Not enough data for a report. Chat more first.")
    
    try:
        report = await agent.generate_report(session.history)
        session.is_complete = True
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
