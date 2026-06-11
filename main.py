#!/usr/bin/env python3
"""
Main entry point for ZJMF AI Agent
Coordinates document processing, web scraping, and funding recommendations
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, Any, List

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from agent import CharityAIAgent
from recommendations import RecommendationEngine, RecommendationFormatter
from utils import PDFProcessor, WebScraper


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ZJMFOrganizer:
    """Main orchestrator for the ZJMF funding recommendation system"""
    
    def __init__(self, config_path: str = None):
        """Initialize the organizer with configuration"""
        self.config = self._load_config(config_path)
        self.agent = CharityAIAgent(self.config)
        self.recommendation_engine = RecommendationEngine(self.agent.llm_client)
        self.formatter = RecommendationFormatter()
        
    def _load_config(self, config_path: str = None) -> Dict[str, Any]:
        """Load configuration from file or environment"""
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                import yaml
                return yaml.safe_load(f)
        return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "openai_api_key": os.getenv("OPENAI_API_KEY"),
            "model": "gpt-4",
            "temperature": 0.7,
            "max_tokens": 2000,
            "document_folder": "./documents",
            "output_folder": "./output",
            "funding_sources_file": "./data/funding_sources.json"
        }
    
    def process_charity_document(self, document_path: str) -> Dict[str, Any]:
        """Process a charity document and extract key information"""
        logger.info(f"Processing document: {document_path}")
        
        # Check if file exists
        if not os.path.exists(document_path):
            logger.error(f"Document not found: {document_path}")
            return {}
        
        # Process based on file type
        if document_path.endswith('.pdf'):
            return self._process_pdf(document_path)
        elif document_path.endswith('.txt'):
            return self._process_text(document_path)
        else:
            logger.warning(f"Unsupported file type: {document_path}")
            return {}
    
    def _process_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """Process PDF document"""
        processor = PDFProcessor()
        text = processor.extract_text(pdf_path)
        return self.agent.extract_charity_info(text)
    
    def _process_text(self, text_path: str) -> Dict[str, Any]:
        """Process text document"""
        with open(text_path, 'r') as f:
            text = f.read()
        return self.agent.extract_charity_info(text)
    
    def fetch_funding_sources(self) -> List[Dict[str, Any]]:
        """Fetch available funding sources"""
        logger.info("Fetching funding sources...")
        
        funding_sources = []
        
        # Try to load from local file first
        if os.path.exists(self.config.get("funding_sources_file", "")):
            with open(self.config["funding_sources_file"], 'r') as f:
                funding_sources = json.load(f)
        else:
            # Scrape from web sources
            scraper = WebScraper()
            funding_sources = scraper.scrape_funding_opportunities()
        
        logger.info(f"Found {len(funding_sources)} funding sources")
        return funding_sources
    
    def generate_recommendations(self, charity_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate funding recommendations for a charity"""
        logger.info(f"Generating recommendations for: {charity_data.get('name', 'Unknown')}")
        
        # Fetch available funding sources
        funding_sources = self.fetch_funding_sources()
        
        # Generate recommendations
        recommendations = self.recommendation_engine.generate_recommendations(
            charity_data, 
            funding_sources
        )
        
        return recommendations
    
    def generate_report(self, charity_name: str, charity_data: Dict[str, Any], 
                       recommendations: List[Dict[str, Any]]) -> str:
        """Generate a comprehensive report"""
        report = f"# ZJMF Funding Recommendations Report\n\n"
        report += f"**Charity:** {charity_name}\n"
        report += f"**Mission:** {charity_data.get('mission', 'N/A')}\n"
        report += f"**Focus Areas:** {', '.join(charity_data.get('focus_areas', []))}\n\n"
        
        report += self.formatter.format_for_report(recommendations)
        
        return report
    
    def save_report(self, report: str, output_file: str = None) -> str:
        """Save report to file"""
        if output_file is None:
            output_dir = self.config.get("output_folder", "./output")
            os.makedirs(output_dir, exist_ok=True)
            output_file = os.path.join(output_dir, "recommendations_report.md")
        
        with open(output_file, 'w') as f:
            f.write(report)
        
        logger.info(f"Report saved to: {output_file}")
        return output_file
    
    def run_full_pipeline(self, document_path: str) -> Dict[str, Any]:
        """Run the complete pipeline: extract -> recommend -> report"""
        logger.info("Starting full pipeline...")
        
        # 1. Process charity document
        charity_data = self.process_charity_document(document_path)
        if not charity_data:
            logger.error("Failed to extract charity information")
            return {"error": "Failed to process document"}
        
        # 2. Generate recommendations
        recommendations = self.generate_recommendations(charity_data)
        
        # 3. Generate report
        charity_name = charity_data.get("name", "Unknown")
        report = self.generate_report(charity_name, charity_data, recommendations)
        
        # 4. Save report
        report_path = self.save_report(report)
        
        result = {
            "charity_name": charity_name,
            "charity_data": charity_data,
            "recommendations": recommendations,
            "report_path": report_path,
            "status": "success"
        }
        
        logger.info("Pipeline completed successfully")
        return result


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="ZJMF AI Agent - Funding Recommendation System"
    )
    parser.add_argument(
        "document",
        help="Path to charity document (PDF or TXT)"
    )
    parser.add_argument(
        "--config",
        help="Path to configuration file",
        default="config/config.yaml"
    )
    parser.add_argument(
        "--output",
        help="Path to output report",
        default=None
    )
    
    args = parser.parse_args()
    
    # Initialize organizer
    organizer = ZJMFOrganizer(args.config)
    
    # Run pipeline
    result = organizer.run_full_pipeline(args.document)
    
    if result.get("status") == "success":
        print(f"\n✓ Successfully processed: {result['charity_name']}")
        print(f"✓ Report saved to: {result['report_path']}")
        print(f"✓ Generated {len(result['recommendations'])} recommendations")
        return 0
    else:
        print(f"\n✗ Error: {result.get('error', 'Unknown error')}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
