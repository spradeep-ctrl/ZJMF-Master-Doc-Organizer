"""
AI Agent for ZJMF Funding Recommendations
Pulls information from documents and online sources to provide charity funding insights
"""

import os
import json
from typing import List, Dict, Any
from datetime import datetime
import PyPDF2
import requests
from openai import OpenAI

class ZJMFAgentConfig:
    """Configuration for the ZJMF Agent"""
    def __init__(self, config_path: str = "config/config.yaml"):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.web_search_enabled = True
        self.model_name = "gpt-4"
        
class DocumentProcessor:
    """Process PDF documents to extract funding information"""
    
    def __init__(self):
        self.extracted_data = {}
    
    def extract_pdf_content(self, pdf_path: str) -> Dict[str, Any]:
        """Extract text and structured data from PDF"""
        content = {
            "text": [],
            "metadata": {},
            "extraction_time": datetime.now().isoformat()
        }
        
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                content["metadata"]["num_pages"] = len(pdf_reader.pages)
                
                for page_num, page in enumerate(pdf_reader.pages):
                    text = page.extract_text()
                    content["text"].append({
                        "page": page_num + 1,
                        "content": text
                    })
            
            return content
        except Exception as e:
            print(f"Error processing PDF {pdf_path}: {str(e)}")
            return {"error": str(e)}
    
    def parse_funding_opportunities(self, text: str) -> List[Dict[str, Any]]:
        """Parse funding opportunities from extracted text"""
        opportunities = []
        # This will be enhanced with LLM processing
        return opportunities


class FundingRecommendationAgent:
    """Main AI Agent for providing funding recommendations"""
    
    def __init__(self, config: ZJMFAgentConfig):
        self.config = config
        self.client = OpenAI(api_key=config.openai_api_key)
        self.doc_processor = DocumentProcessor()
        self.funding_database = {}
        
    def process_master_document(self, pdf_path: str) -> Dict[str, Any]:
        """Process the ZJMF Master Doc to extract current funding information"""
        print(f"Processing document: {pdf_path}")
        
        # Extract content from PDF
        doc_content = self.doc_processor.extract_pdf_content(pdf_path)
        
        if "error" in doc_content:
            return {"error": f"Failed to process document: {doc_content['error']}"}
        
        # Use LLM to analyze and structure the data
        analysis = self._analyze_with_llm(doc_content, "Extract and summarize all funding opportunities")
        
        return analysis
    
    def search_online_funding(self, query: str, charity_focus: str = None) -> List[Dict[str, Any]]:
        """Search online for additional funding opportunities"""
        opportunities = []
        
        if not self.config.web_search_enabled:
            return opportunities
        
        # Construct search query
        search_query = f"charity funding opportunities {query}"
        if charity_focus:
            search_query += f" {charity_focus}"
        
        print(f"Searching for: {search_query}")
        # TODO: Integrate with web search API (Serper, DuckDuckGo, etc.)
        
        return opportunities
    
    def _analyze_with_llm(self, content: Dict, task: str) -> Dict[str, Any]:
        """Use LLM to analyze content"""
        try:
            text_content = "\n".join([
                page["content"] for page in content.get("text", [])
            ])
            
            response = self.client.chat.completions.create(
                model=self.config.model_name,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert in charity funding and grants. Analyze documents to identify funding opportunities, requirements, and provide strategic recommendations."
                    },
                    {
                        "role": "user",
                        "content": f"{task}\n\nDocument content:\n{text_content[:3000]}"  # Limit tokens
                    }
                ],
                temperature=0.7,
                max_tokens=1500
            )
            
            return {
                "analysis": response.choices[0].message.content,
                "model": self.config.model_name,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {"error": f"LLM analysis failed: {str(e)}"}
    
    def generate_recommendations(self, funding_info: Dict, charity_info: Dict) -> Dict[str, Any]:
        """Generate personalized funding recommendations"""
        try:
            prompt = f"""
            Based on the following information about Zcharia Jose Memorial Foundation and available funding opportunities,
            generate strategic recommendations:
            
            Charity Information: {json.dumps(charity_info, indent=2)}
            Funding Opportunities: {json.dumps(funding_info, indent=2)}
            
            Provide:
            1. Top 5 most suitable funding opportunities
            2. Key strengths to emphasize in applications
            3. Timeline and application strategy
            4. Risk factors and mitigation
            5. Expected outcomes
            """
            
            response = self.client.chat.completions.create(
                model=self.config.model_name,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a funding strategist for nonprofits. Provide actionable, data-driven recommendations."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.8,
                max_tokens=2000
            )
            
            return {
                "recommendations": response.choices[0].message.content,
                "generated_at": datetime.now().isoformat(),
                "status": "success"
            }
        except Exception as e:
            return {"error": f"Failed to generate recommendations: {str(e)}", "status": "failed"}
    
    def save_results(self, results: Dict, output_path: str = "results/recommendations.json"):
        """Save recommendations to file"""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"Results saved to {output_path}")
        return output_path


def main():
    """Main entry point for the agent"""
    
    # Initialize configuration
    config = ZJMFAgentConfig()
    
    # Create agent
    agent = FundingRecommendationAgent(config)
    
    # Process master document
    pdf_path = "documents/ZJMF Funding Master Doc.pdf"
    if os.path.exists(pdf_path):
        master_doc_analysis = agent.process_master_document(pdf_path)
        print("Master Document Analysis:", master_doc_analysis)
    
    # Search for online funding opportunities
    online_opportunities = agent.search_online_funding(
        query="health education",
        charity_focus="Kansas City"
    )
    
    # Generate recommendations
    charity_info = {
        "name": "Zcharia Jose Memorial Foundation",
        "focus_areas": ["health", "education", "community development"],
        "location": "Kansas City, Kansas",
        "mission": "Support underserved communities"
    }
    
    recommendations = agent.generate_recommendations(
        funding_info=online_opportunities,
        charity_info=charity_info
    )
    
    # Save results
    agent.save_results(recommendations)
    
    print("\n=== ZJMF Funding Recommendations Agent ===")
    print("Recommendations generated successfully!")
    print(recommendations)


if __name__ == "__main__":
    main()
