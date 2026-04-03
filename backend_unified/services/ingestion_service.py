import uuid
import json
import re
from typing import List
from groq import Groq
from backend_unified.config import settings
from backend_unified.utils.parser import parse_document, clean_text
from backend_unified.utils.embeddings import generate_embedding
from backend_unified.models.schemas import SyllabusUploadResponse, TopicBreakdown
from backend_unified.services.vector_service import VectorService
from backend_unified.utils.logger import get_logger

logger = get_logger("ingestion_service")
vector_service = VectorService()

def should_enhance(text: str) -> bool:
    """Determine if syllabus text is too sparse and requires LLM expansion."""
    words = text.split()
    return len(words) < 80 or "unit" in text.lower() or "module" in text.lower()

def extract_links(text: str) -> List[str]:
    """Scrape explicit URLs from raw text."""
    return re.findall(r'https?://\S+', text)

def parse_input(input_type: str, file_bytes: bytes = None, text: str = None) -> str:
    """Unified Input Interface for multi-modality."""
    if input_type in ["application/pdf", "pdf"]:
        return parse_document(file_bytes, input_type)
    elif input_type in ["image/png", "image/jpeg"]:
        # Mock OCR extraction
        return "OCR extracted text..."
    elif text:
        return text
    return ""

def process_syllabus(file_bytes: bytes, file_type: str, raw_text_input: str = None) -> SyllabusUploadResponse:
    logger.info("Starting Multi-Input Syllabus pipeline")
    
    # 1. Parse Content
    input_format = "text" if raw_text_input else file_type
    raw_text = parse_input(input_format, file_bytes, raw_text_input)
    cleaned_text = clean_text(raw_text)
    
    # 2. Extract Resources
    resources = extract_links(cleaned_text)
    
    # 3. Enhancement Decision
    is_enhanced = should_enhance(cleaned_text)
    
    # 4. Structure Output via LLM
    topics = []
    try:
        client = Groq(api_key=settings.GROQ_API_KEY)
        if is_enhanced:
            prompt = (
                "You are an expert curriculum extractor. Extract the main topics from the syllabus text. "
                "Because the text is brief, ENHANCE it by inferring the likely subtopics and structuring a deeper hierarchy. "
                "Ensure standard academic normalization. "
                "Output MUST be in strict JSON format matching exactly this shape: "
                '{"topics": [{"topic": "Name", "subtopics": ["Concept 1", "Concept 2", "Concept 3"]}]}'
            )
        else:
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
        
    logger.info(f"Successfully embedded syllabus. Enhanced: {is_enhanced}, Resources: {len(resources)}")
    return SyllabusUploadResponse(topics=topics, resources=resources, enhanced=is_enhanced)
