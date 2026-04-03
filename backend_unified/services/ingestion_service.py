import uuid
import json
from groq import Groq
from backend_unified.config import settings
from backend_unified.utils.parser import parse_document, clean_text
from backend_unified.utils.embeddings import generate_embedding
from backend_unified.models.schemas import SyllabusUploadResponse, TopicBreakdown
from backend_unified.services.vector_service import VectorService
from backend_unified.utils.logger import get_logger

logger = get_logger("ingestion_service")
vector_service = VectorService()

def process_syllabus(file_bytes: bytes, file_type: str) -> SyllabusUploadResponse:
    logger.info("Starting syllabus ingestion pipeline with LLM")
    
    # 1. Parse Content
    raw_text = parse_document(file_bytes, file_type)
    cleaned_text = clean_text(raw_text)
    
    # 2. Structure Output via LLM
    topics = []
    try:
        client = Groq(api_key=settings.GROQ_API_KEY)
        prompt = (
            "You are an expert curriculum extractor. Extract the top 2-5 main topics and their subtopics from the following syllabus text. "
            "Output MUST be in strict JSON format matching exactly this shape: "
            '{"topics": [{"topic": "Name", "subtopics": ["Concept 1", "Concept 2"]}]}'
        )
        # Slicing text to prevent token limit errors for free demo
        chunk = cleaned_text[:3500] 
        
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": f"Text: {chunk}"} # Groq does JSON mode best when properly prompted
            ],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"}
        )
        result_str = response.choices[0].message.content
        data = json.loads(result_str)
        for t in data.get("topics", []):
            topics.append(TopicBreakdown(**t))
            
    except Exception as e:
        logger.error(f"Failed to use LLM parsing: {e}")
        # fallback
        topics = [TopicBreakdown(topic="Fallback Topic", subtopics=["Fallback Subtopic"])]

    # 3. Embed & Store
    chunks = []
    # Arbitrary small chunk creation
    chunk_size = 500
    text_chunks = [cleaned_text[i:i+chunk_size] for i in range(0, len(cleaned_text), chunk_size)]
    
    for i, txt in enumerate(text_chunks):
        if not txt.strip(): continue
        chunk_id = str(uuid.uuid4())
        vector = generate_embedding(txt)
        # Try to map chunk to a topic naively
        mapped_topic = topics[0].topic if topics else "general"
        chunks.append({
            "id": chunk_id,
            "vector": vector,
            "payload": {
                "topic": mapped_topic,
                "text": txt
            }
        })
            
    if chunks:
        vector_service.store_chunks(chunks)
        
    logger.info("Successfully embedded syllabus")
    return SyllabusUploadResponse(topics=topics)
