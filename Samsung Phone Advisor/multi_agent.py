from typing import Dict
from rag_module import RAGModule
from sqlalchemy.orm import Session
import re

try:
    from groq import Groq
except ImportError:
    Groq = None

class DataExtractorAgent:
    """Agent 1: Extracts and structures data from user queries"""
    
    def __init__(self, rag_module: RAGModule):
        self.rag = rag_module
    
    def extract_intent(self, query: str) -> Dict:
        query_lower = query.lower()
        
        result = {
            'intent': 'search',
            'phones': [],
            'criteria': {},
            'is_comparison': False
        }
        
        
        if 'compare' in query_lower or 'vs' in query_lower or 'versus' in query_lower:
            result['intent'] = 'comparison'
            result['is_comparison'] = True
        
    
        elif 'best' in query_lower or 'recommend' in query_lower or 'suggest' in query_lower:
            result['intent'] = 'recommendation'
        
        elif 'spec' in query_lower or 'specs' in query_lower:
            result['intent'] = 'specs'
        
        # Extract phone names from query
        samsung_models = [
            'S24', 'S24+', 'S24 Ultra', 'S23', 'S23+', 'S23 Ultra', 
            'S22', 'S22+', 'S22 Ultra', 'A54', 'A53', 'A52', 'Z Fold', 'Z Flip',
            'Note 20', 'A71', 'A72', 'A73'
        ]
        
        for model in samsung_models:
            if model.lower() in query_lower:
                result['phones'].append(f"Samsung Galaxy {model}")
        
        # Extract price criteria
        price_match = re.search(r'\$?(\d+)\s*(?:usd|dollars?)?', query_lower)
        if price_match:
            result['criteria']['price_max'] = int(price_match.group(1))
        
        # Extract battery criteria
        battery_match = re.search(r'(\d+)\s*(?:mah|mAh)', query_lower)
        if battery_match:
            result['criteria']['battery_min'] = battery_match.group(1)
        
        return result
    
    def execute_query(self, query: str) -> Dict:

        intent = self.extract_intent(query)
        data = {
            'intent': intent['intent'],
            'phones': [],
            'all_phones': []
        }
        
        if intent['phones']:

            comparison_data = self.rag.retrieve_comparison_phones(intent['phones'])
            data['phones'] = comparison_data
        elif intent['criteria']:
            
            matching_phones = self.rag.retrieve_phones_by_criteria(intent['criteria'])
            data['phones'] = matching_phones
        else:
    
            matching_phones = self.rag.search_phones(query)
            data['phones'] = matching_phones
        
        return data

class ReviewGeneratorAgent:
    """Agent 2: Generates natural language reviews and comparisons"""
    
    def __init__(self, use_llm: bool = True):
        self.use_llm = use_llm and Groq is not None
        if self.use_llm:
            try:
                from config import GROQ_API_KEY
                self.client = Groq(api_key=GROQ_API_KEY)
            except Exception as e:
                print(f"Warning: Failed to initialize Groq client: {e}")
                self.use_llm = False
    
    def generate_spec_review(self, phone_data: Dict) -> str:
        specs_text = self._format_specs(phone_data)
        
        if self.use_llm:
            return self._generate_with_llm(f"Write a concise review of this Samsung phone based on specs:\n{specs_text}")
        else:
            return self._generate_rule_based_review(phone_data)
    
    def generate_comparison(self, phones_data: Dict[str, Dict]) -> str:
        if len(phones_data) < 2:
            return "Need at least 2 phones for comparison"
        
        comparison_text = "Comparing:\n"
        for name, specs in phones_data.items():
            comparison_text += f"\n{name}:\n{self._format_specs(specs)}\n"
        
        if self.use_llm:
            prompt = f"{comparison_text}\nProvide a detailed comparison highlighting key differences and which phone is better for different use cases."
            return self._generate_with_llm(prompt)
        else:
            return self._generate_rule_based_comparison(phones_data)
    
    def generate_recommendation(self, phones_data: Dict[str, Dict], criteria: str) -> str:
        comparison_text = "Available phones:\n"
        for name, specs in phones_data.items():
            comparison_text += f"\n{name}:\n{self._format_specs(specs)}\n"
        
        if self.use_llm:
            prompt = f"{comparison_text}\nBased on these phones, which would be best for {criteria}? Provide reasoning."
            return self._generate_with_llm(prompt)
        else:
            return self._generate_rule_based_recommendation(phones_data, criteria)
    
    def _format_specs(self, phone_data: Dict) -> str:
        lines = [
            f"Model: {phone_data.get('model_name', 'N/A')}",
            f"Display: {phone_data.get('display_size', 'N/A')} {phone_data.get('display_type', '')}",
            f"Resolution: {phone_data.get('resolution', 'N/A')}",
            f"Processor: {phone_data.get('processor', 'N/A')}",
            f"RAM: {phone_data.get('ram', 'N/A')}",
            f"Storage: {phone_data.get('storage', 'N/A')}",
            f"Camera (Rear): {phone_data.get('rear_camera_mp', 'N/A')}",
            f"Camera (Front): {phone_data.get('front_camera_mp', 'N/A')}",
            f"Battery: {phone_data.get('battery_capacity', 'N/A')}",
            f"Price: ${phone_data.get('price_usd', 'N/A')}",
        ]
        return "\n".join(lines)
    
    def _generate_with_llm(self, prompt: str) -> str:
        """Generate text using Groq LLM"""
        try:
            from config import LLM_MODEL
            message = self.client.chat.completions.create(
                model=LLM_MODEL,
                max_tokens=1024,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return message.choices[0].message.content
        except Exception as e:
            return f"Error generating review: {e}"
    
    def _generate_rule_based_review(self, phone_data: Dict) -> str:
        """Fallback rule-based review generation"""
        name = phone_data.get('model_name', 'This Samsung phone')
        display = phone_data.get('display_size', 'unknown')
        camera = phone_data.get('rear_camera_mp', 'unknown')
        battery = phone_data.get('battery_capacity', 'unknown')
        processor = phone_data.get('processor', 'unknown')
        price = phone_data.get('price_usd', 'unknown')
        
        return f"""
{name} Review:

The {name} features a {display} display with quality viewing experience. The {camera} rear camera system delivers excellent photo and video capabilities. Battery performance is solid with {battery} capacity for all-day use.

With {processor} processing power and impressive performance, it handles demanding tasks smoothly. At ${price}, it offers great value for a premium Samsung device.

Key Strengths:
- Excellent camera performance
- Solid battery life
- Premium build quality
- Smooth performance

Recommended for: Photography enthusiasts, power users, and those seeking a flagship Android experience.
"""
    
    def _generate_rule_based_comparison(self, phones_data: Dict[str, Dict]) -> str:
        """Fallback rule-based comparison"""
        if len(phones_data) != 2:
            return "Comparison works best with exactly 2 phones"
        
        names = list(phones_data.keys())
        phone1_name, phone2_name = names[0], names[1]
        phone1, phone2 = phones_data[phone1_name], phones_data[phone2_name]
        
        result = f"Comparison: {phone1_name} vs {phone2_name}\n\n"
        
        # Display comparison
        result += f"Display: {phone1['display_size']} vs {phone2['display_size']}\n"
        result += f"Camera: {phone1['rear_camera_mp']} vs {phone2['rear_camera_mp']}\n"
        result += f"Battery: {phone1['battery_capacity']} vs {phone2['battery_capacity']}\n"
        result += f"Processor: {phone1['processor']} vs {phone2['processor']}\n"
        
        return result
    
    def _generate_rule_based_recommendation(self, phones_data: Dict[str, Dict], criteria: str) -> str:
        """Fallback rule-based recommendation"""
        result = f"Based on {criteria}:\n\n"
        
        if 'photo' in criteria.lower() or 'camera' in criteria.lower():
            phones_sorted = sorted(phones_data.items(), 
                                   key=lambda x: x[1].get('rear_camera_mp', '0'))
            result += f"Best for photography: {phones_sorted[-1][0]}\n"
        
        if 'battery' in criteria.lower():
            phones_sorted = sorted(phones_data.items(),
                                   key=lambda x: x[1].get('battery_capacity', '0'))
            result += f"Best battery life: {phones_sorted[-1][0]}\n"
        
        if 'price' in criteria.lower() or 'budget' in criteria.lower():
            phones_sorted = sorted(phones_data.items(),
                                   key=lambda x: x[1].get('price_usd', 9999))
            result += f"Best value: {phones_sorted[0][0]}\n"
        
        return result if result != f"Based on {criteria}:\n\n" else "Cannot determine recommendation with available data"

class MultiAgentOrchestrator:
    """Orchestrates Data Extractor and Review Generator agents"""
    
    def __init__(self, db: Session):
        self.rag = RAGModule(db)
        self.extractor = DataExtractorAgent(self.rag)
        self.reviewer = ReviewGeneratorAgent(use_llm=True)
    
    def process_query(self, user_query: str) -> Dict:
        """Process user query and generate unified response"""
        # Step 1: Extract data
        extracted_data = self.extractor.execute_query(user_query)
        
        # Step 2: Generate reviews/comparisons based on intent
        response = {
            'question': user_query,
            'intent': extracted_data['intent'],
            'specifications': [],
            'analysis': '',
            'phones_found': len(extracted_data['phones'])
        }
        
        if not extracted_data['phones']:
            response['analysis'] = "No matching phones found. Please try a different search."
            return response
        
        # Generate response based on intent
        if extracted_data['intent'] == 'comparison' and len(extracted_data['phones']) >= 2:
            response['specifications'] = list(extracted_data['phones'].values())
            response['analysis'] = self.reviewer.generate_comparison(extracted_data['phones'])
        
        elif extracted_data['intent'] == 'recommendation':
            response['specifications'] = list(extracted_data['phones'].values())
            criteria = self._extract_criteria(user_query)
            response['analysis'] = self.reviewer.generate_recommendation(
                extracted_data['phones'], criteria
            )
        
        elif extracted_data['intent'] == 'specs' and extracted_data['phones']:
            for phone_name, phone_specs in extracted_data['phones'].items():
                response['specifications'].append(phone_specs)
                if not response['analysis']:
                    response['analysis'] = self.reviewer.generate_spec_review(phone_specs)
                else:
                    response['analysis'] += f"\n\n{self.reviewer.generate_spec_review(phone_specs)}"
        
        else:
            # General search
            response['specifications'] = extracted_data['phones']
            if len(extracted_data['phones']) == 1:
                response['analysis'] = self.reviewer.generate_spec_review(extracted_data['phones'][0])
            else:
                response['analysis'] = f"Found {len(extracted_data['phones'])} phones matching your query."
        
        return response
    
    def _extract_criteria(self, query: str) -> str:
        """Extract criteria from query string"""
        query_lower = query.lower()
        
        if 'photo' in query_lower or 'camera' in query_lower:
            return 'photography'
        elif 'battery' in query_lower or 'long' in query_lower:
            return 'long battery life'
        elif 'budget' in query_lower or 'cheap' in query_lower or 'affordable' in query_lower:
            return 'budget constraints'
        elif 'gaming' in query_lower:
            return 'gaming performance'
        else:
            return 'general use'
