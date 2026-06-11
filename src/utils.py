"""
Utilities for web scraping and data fetching
"""

import requests
from typing import List, Dict, Any
from bs4 import BeautifulSoup
import json

class WebScraper:
    """Handles web scraping for funding opportunities"""
    
    def __init__(self, headers: Dict[str, str] = None):
        self.headers = headers or {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.timeout = 10
    
    def fetch_page(self, url: str) -> str:
        """Fetch a webpage"""
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None
    
    def extract_links(self, html: str, selector: str = "a") -> List[str]:
        """Extract links from HTML"""
        soup = BeautifulSoup(html, 'html.parser')
        links = []
        for element in soup.select(selector):
            href = element.get('href')
            if href:
                links.append(href)
        return links


class FundingSourceAggregator:
    """Aggregate funding sources from various foundations"""
    
    FUNDING_SOURCES = {
        "bank_of_america": {
            "url": "https://www.bankofamerica.com/philanthropic/",
            "name": "Bank of America Giving Fund",
            "focus_areas": ["community development", "education", "health"]
        },
        "kauffman": {
            "url": "https://www.kauffman.org/",
            "name": "Ewing Marion Kauffman Foundation",
            "focus_areas": ["entrepreneurship", "education", "community development"]
        },
        "h_r_block": {
            "url": "https://blockfoundation.org/",
            "name": "H&R Block Foundation",
            "focus_areas": ["financial literacy", "education", "community"]
        },
        "health_forward": {
            "url": "http://healthforward.org/",
            "name": "Health Forward Foundation",
            "focus_areas": ["health", "healthcare access", "community health"]
        }
    }
    
    @classmethod
    def get_relevant_sources(cls, focus_areas: List[str]) -> List[Dict[str, Any]]:
        """Get funding sources relevant to focus areas"""
        relevant = []
        
        for source_id, source_info in cls.FUNDING_SOURCES.items():
            # Check if any focus area matches
            if any(area.lower() in [fa.lower() for fa in source_info["focus_areas"]] 
                   for area in focus_areas):
                relevant.append(source_info)
        
        return relevant


class DataValidator:
    """Validate and clean extracted data"""
    
    @staticmethod
    def validate_funding_opportunity(opportunity: Dict[str, Any]) -> bool:
        """Validate a funding opportunity record"""
        required_fields = ["name", "url", "focus_areas"]
        return all(field in opportunity for field in required_fields)
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Clean extracted text"""
        # Remove extra whitespace
        text = ' '.join(text.split())
        # Remove special characters
        text = text.replace('\x00', '')
        return text.strip()
