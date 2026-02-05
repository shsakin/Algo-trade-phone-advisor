from sqlalchemy.orm import Session
from database import SamsungPhone
from typing import List, Dict, Optional

class RAGModule:
    """Retrieval-Augmented Generation Module for phone specifications"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def retrieve_phone_by_name(self, phone_name: str) -> Optional[Dict]:
        """Retrieve a single phone by name"""
        phone = self.db.query(SamsungPhone).filter(
            SamsungPhone.model_name.ilike(f"%{phone_name}%")
        ).first()
        
        if phone:
            return self._phone_to_dict(phone)
        return None
    
    def retrieve_phones_by_criteria(self, criteria: Dict) -> List[Dict]:
        """Retrieve phones based on multiple criteria"""
        query = self.db.query(SamsungPhone)
        
        if 'price_max' in criteria:
            query = query.filter(SamsungPhone.price_usd <= criteria['price_max'])
        
        if 'battery_min' in criteria:
            query = query.filter(SamsungPhone.battery_capacity.ilike(f"%{criteria['battery_min']}%"))
        
        if 'processor' in criteria:
            query = query.filter(SamsungPhone.processor.ilike(f"%{criteria['processor']}%"))
        
        if 'ram_min' in criteria:
            query = query.filter(SamsungPhone.ram.ilike(f"%{criteria['ram_min']}%"))
        
        phones = query.all()
        return [self._phone_to_dict(phone) for phone in phones]
    
    def retrieve_comparison_phones(self, phone_names: List[str]) -> Dict[str, Dict]:
        """Retrieve multiple phones for comparison"""
        result = {}
        for name in phone_names:
            phone_data = self.retrieve_phone_by_name(name)
            if phone_data:
                result[name] = phone_data
        return result
    
    def search_phones(self, query: str) -> List[Dict]:
        """General search across phone specifications"""
        phones = self.db.query(SamsungPhone).filter(
            (SamsungPhone.model_name.ilike(f"%{query}%")) |
            (SamsungPhone.processor.ilike(f"%{query}%"))
        ).all()
        
        return [self._phone_to_dict(phone) for phone in phones]
    
    @staticmethod
    def _phone_to_dict(phone: SamsungPhone) -> Dict:
        """Convert phone ORM object to dictionary"""
        return {
            'model_name': phone.model_name,
            'release_date': phone.release_date,
            'display_size': phone.display_size,
            'display_type': phone.display_type,
            'resolution': phone.resolution,
            'processor': phone.processor,
            'ram': phone.ram,
            'storage': phone.storage,
            'rear_camera_mp': phone.rear_camera_mp,
            'front_camera_mp': phone.front_camera_mp,
            'battery_capacity': phone.battery_capacity,
            'connectivity': phone.connectivity,
            'price_usd': phone.price_usd,
            'price_eur': phone.price_eur,
            'os': phone.os,
            'weight': phone.weight,
            'dimensions': phone.dimensions,
            'url': phone.url,
        }
