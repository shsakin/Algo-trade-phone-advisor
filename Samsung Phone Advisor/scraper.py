import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
from database import SessionLocal, SamsungPhone

class GSMArenaScraperError(Exception):
    pass

class GSMArenaScraperSamsung:
    def __init__(self):
        self.base_url = "https://www.gsmarena.com"
        self.samsung_url = "https://www.gsmarena.com/?sXmlhttp=1&xhtml=1&curpage=1&sorting=newest&order=1&brand=6"
        self.driver = None
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def init_driver(self):
        """Initialize Selenium Chrome driver"""
        try:
            chrome_options = Options()
            chrome_options.add_argument("--start-maximized")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            self.driver = webdriver.Chrome(options=chrome_options)
            print("Chrome driver initialized")
        except Exception as e:
            print(f"Warning: Chrome driver failed, trying Edge: {e}")
            try:
                edge_options = Options()
                edge_options.add_argument("--start-maximized")
                self.driver = webdriver.Edge(options=edge_options)
                print("Edge driver initialized")
            except Exception as e2:
                raise GSMArenaScraperError(f"Failed to initialize any browser driver: {e2}")
    
    def close_driver(self):
        """Close Selenium driver"""
        if self.driver:
            self.driver.quit()
            self.driver = None
    
    def get_samsung_phones(self, max_phones=30):
        """Scrape Samsung phones list using Selenium"""
        try:
            print("Loading GSMArena with Selenium...")
            self.driver.get(self.samsung_url)
            
            # Wait for content to load (max 20 seconds)
            wait = WebDriverWait(self.driver, 20)
            wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "a")))
            
            # Give it extra time for JavaScript to fully render
            time.sleep(3)
            
            phones = []
            
            # Get all links from the page
            links = self.driver.find_elements(By.TAG_NAME, "a")
            print(f"Found {len(links)} total links on page")
            
            for link in links:
                if len(phones) >= max_phones:
                    break
                try:
                    href = link.get_attribute('href')
                    text = link.text.strip()
                    
                    if href and text and len(text) > 3:
                        href_lower = href.lower()
                        text_lower = text.lower()
                        
                        is_phone_link = (
                            ('samsung' in href_lower or 'samsung' in text_lower) and
                            ('galaxy' in href_lower or 'galaxy' in text_lower or 'fold' in text_lower or 'flip' in text_lower or 'note' in text_lower) and
                            ('.php' in href_lower or '/phones/' in href_lower) and
                            'html=1' not in href_lower  # Skip navigation links
                        )
                        
                        if is_phone_link:
                            # Ensure full URL
                            full_url = href if href.startswith('http') else self.base_url + href
                            
                            # Avoid duplicates
                            if not any(p['url'] == full_url for p in phones):
                                phones.append({
                                    'name': text,
                                    'url': full_url
                                })
                                print(f"  Found: {text}")
                except Exception as e:
                    continue
            
            print(f"Total phones found: {len(phones)}")
            return phones
        except Exception as e:
            raise GSMArenaScraperError(f"Failed to scrape Samsung phones list: {e}")
    
    def scrape_phone_details(self, phone_url):
        """Scrape detailed specs for a single phone using Selenium"""
        try:
            print(f"  Scraping: {phone_url[:80]}...")
            self.driver.get(phone_url)
            
            # Wait for page to load
            wait = WebDriverWait(self.driver, 15)
            wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "td")))
            
            time.sleep(2)  # Extra wait for dynamic content
            
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            details = {
                'url': phone_url,
                'model_name': '',
                'release_date': '',
                'display_size': '',
                'display_type': '',
                'resolution': '',
                'processor': '',
                'ram': '',
                'storage': '',
                'rear_camera_mp': '',
                'front_camera_mp': '',
                'battery_capacity': '',
                'connectivity': '',
                'os': '',
                'weight': '',
                'dimensions': '',
                'price_usd': None,
            }
            
            # Title
            title = soup.find('h1', class_='specs-phone-name-title')
            if title:
                details['model_name'] = title.text.strip()
            
            # Extract specifications from tables
            spec_tables = soup.find_all('table', class_='table table-specs')
            for table in spec_tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) == 2:
                        key = cells[0].text.strip().lower()
                        value = cells[1].text.strip()
                        
                        if 'release date' in key:
                            details['release_date'] = value
                        elif 'screen' in key or 'display' in key:
                            if 'size' in key:
                                details['display_size'] = value
                            elif 'type' in key:
                                details['display_type'] = value
                            elif 'resolution' in key:
                                details['resolution'] = value
                        elif 'processor' in key or 'chipset' in key:
                            details['processor'] = value
                        elif 'ram' in key:
                            details['ram'] = value
                        elif 'storage' in key or 'memory' in key:
                            details['storage'] = value
                        elif 'rear camera' in key or 'back camera' in key:
                            details['rear_camera_mp'] = value
                        elif 'front camera' in key or 'selfie' in key:
                            details['front_camera_mp'] = value
                        elif 'battery' in key:
                            details['battery_capacity'] = value
                        elif 'connectivity' in key or 'network' in key:
                            details['connectivity'] = value
                        elif 'os' in key or 'operating system' in key:
                            details['os'] = value
                        elif 'weight' in key:
                            details['weight'] = value
                        elif 'dimension' in key:
                            details['dimensions'] = value
            
            return details
        except Exception as e:
            print(f"Error scraping {phone_url}: {e}")
            return None
    
    def scrape_and_store(self, max_phones=30):
        """Main method: scrape phones and store in database"""
        db = SessionLocal()
        try:
            self.init_driver()
            
            print(f"Fetching Samsung phones list...")
            phones = self.get_samsung_phones(max_phones)
            print(f"Found {len(phones)} phones. Scraping details...")
            
            for idx, phone in enumerate(phones):
                print(f"\n[{idx+1}/{len(phones)}] Scraping: {phone['name']}")
                details = self.scrape_phone_details(phone['url'])
                
                if details and details['model_name']:
                    # Check if already exists
                    existing = db.query(SamsungPhone).filter_by(
                        model_name=details['model_name']
                    ).first()
                    
                    if not existing:
                        phone_record = SamsungPhone(**details)
                        db.add(phone_record)
                        db.commit()
                        print(f"Stored: {details['model_name']}")
                    else:
                        print(f"Already exists: {details['model_name']}")
                
                time.sleep(1)  # Be respectful to the server
            
            print(f"\n✓ Scraping complete!")
        except Exception as e:
            db.rollback()
            print(f"Error during scraping: {e}")
        finally:
            db.close()
            self.close_driver()

if __name__ == "__main__":
    scraper = GSMArenaScraperSamsung()
    scraper.scrape_and_store(max_phones=30)
