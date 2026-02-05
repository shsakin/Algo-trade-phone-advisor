from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import init_db, get_db, SessionLocal, SamsungPhone
from multi_agent import MultiAgentOrchestrator
from scraper import GSMArenaScraperSamsung
from typing import Optional, List
from pathlib import Path
import logging


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Samsung Phone Advisor API",
    description="RAG + Multi-Agent System for Samsung phone recommendations",
    version="1.0.0"
)

static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


class AskRequest(BaseModel):
    question: str
    use_llm: Optional[bool] = True

class PhoneSpec(BaseModel):
    model_name: str
    display_size: Optional[str] = None
    processor: Optional[str] = None
    ram: Optional[str] = None
    rear_camera_mp: Optional[str] = None
    battery_capacity: Optional[str] = None
    price_usd: Optional[float] = None

class AskResponse(BaseModel):
    question: str
    intent: str
    phones_found: int
    specifications: List
    analysis: str


@app.on_event("startup")
def startup_event():
    init_db()
    logger.info("✓ Database initialized")
    

    db = SessionLocal()
    try:
        phone_count = db.query(SamsungPhone).count()
        
        if phone_count == 0:
            logger.info("Database is empty. Starting automatic scraping...")
            logger.info("📱 This may take 3-5 minutes. Please wait...")
            
            try:
                scraper = GSMArenaScraperSamsung()
                scraper.scrape_and_store(max_phones=30)
                

                new_count = db.query(SamsungPhone).count()
                logger.info(f"Scraping completed successfully! Added {new_count} Samsung phones to database")
                logger.info("Database ready. You can now ask questions about Samsung phones!")
                
            except Exception as e:
                logger.error(f"Scraping failed: {str(e)}")
                logger.warning("Database is empty. You can manually scrape data later using the /admin/scrape endpoint")
        else:
            logger.info(f"Database loaded with {phone_count} Samsung phones")
            logger.info("System ready to answer questions!")
    finally:
        db.close()


@app.get("/", include_in_schema=False)
async def root():
    """Serve the main chat UI"""
    return FileResponse(Path(__file__).parent / "static" / "index.html", media_type="text/html")

# Main endpoint
@app.post("/ask", response_model=AskResponse)
async def ask_question(request: AskRequest, db: Session = Depends(get_db)):
    """
    Main endpoint for natural language queries about Samsung phones.
    
    Example queries:
    - "What are the specs of Samsung Galaxy S23 Ultra?"
    - "Compare Galaxy S23 Ultra and S22 Ultra for photography"
    - "Which Samsung phone has the best battery under $1000?"
    """
    
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    
    try:
        orchestrator = MultiAgentOrchestrator(db)
        result = orchestrator.process_query(request.question)
        return AskResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")


@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Samsung Phone Advisor API is running"}

# Scraping endpoint (manual trigger)
@app.post("/admin/scrape")
async def trigger_scrape(max_phones: int = 30):
    """
    Manually trigger scraping of Samsung phones from GSMArena.
    WARNING: This can take several minutes.
    """
    try:
        scraper = GSMArenaScraperSamsung()
        scraper.scrape_and_store(max_phones=max_phones)
        return {"status": "success", "message": f"Scraped up to {max_phones} phones"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scraping failed: {str(e)}")

# Get all phones
@app.get("/phones")
async def get_all_phones(db: Session = Depends(get_db)):
    """Get list of all phones in database"""
    phones = db.query(SamsungPhone).all()
    return {"count": len(phones), "phones": phones}

# Get phone by name
@app.get("/phones/{phone_name}")
async def get_phone(phone_name: str, db: Session = Depends(get_db)):
    """Get detailed specs for a specific phone"""
    from rag_module import RAGModule
    rag = RAGModule(db)
    phone_data = rag.retrieve_phone_by_name(phone_name)
    
    if not phone_data:
        raise HTTPException(status_code=404, detail=f"Phone '{phone_name}' not found")
    
    return phone_data

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)
