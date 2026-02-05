from sqlalchemy import create_engine, Column, String, Float, Integer, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from config import DATABASE_URL

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class SamsungPhone(Base):
    __tablename__ = "samsung_phones"
    
    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String(255), unique=True, index=True)
    release_date = Column(String(100))
    
  
    display_size = Column(String(100))
    display_type = Column(String(100))
    resolution = Column(String(100))
    

    processor = Column(String(255))
    ram = Column(String(100))
    storage = Column(String(100))
    

    rear_camera_mp = Column(String(100))
    front_camera_mp = Column(String(100))
    

    battery_capacity = Column(String(100))
    

    connectivity = Column(Text)
    
    price_usd = Column(Float, nullable=True)
    price_eur = Column(Float, nullable=True)
    

    os = Column(String(100))
    weight = Column(String(100))
    dimensions = Column(String(100))
    

    scraped_at = Column(DateTime, default=datetime.utcnow)
    url = Column(String(500), unique=True)

def init_db():
    """Create all tables"""
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
