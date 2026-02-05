import os
from dotenv import load_dotenv

load_dotenv()

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/samsung_advisor")

# LLM Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
LLM_MODEL = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")

# Scraper Configuration
GSMAREA_BASE_URL = "https://www.gsmarena.com"
GSMAREA_SAMSUNG_URL = "https://www.gsmarena.com/samsung-phones-9.php"

# Agent Configuration
ENABLE_REVIEW_GENERATION = True
MAX_RETRIES = 3
