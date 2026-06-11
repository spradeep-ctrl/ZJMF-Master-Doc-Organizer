"""
Recommendation engine for funding opportunities
"""

from typing import List, Dict, Any
import json
from datetime import datetime


class RecommendationEngine:
    """Generate recommendations based on charity data and funding sources"""
    
    def __init__(self, llm_client):
        self.llm_client = llm_client
    
    def generate_recommendations(self, charity_data: Dict[str, Any], 
                                funding_sources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate funding recommendations for a charity"""
        
        recommendations = []
        
        # Extract key information from charity data
        charity_name = charity_data.get("name", "Unknown Organization")
        charity_mission = charity_data.get("mission", "")
        charity_focus = charity_data.get("focus_areas", [])
        
        # Create a prompt for the LLM
        prompt = self._create_recommendation_prompt(
            charity_name, 
            charity_mission, 
            charity_focus, 
            funding_sources
        )
        
        # Get LLM recommendations
        llm_response = self.llm_client.generate(prompt)
        
        # Parse and structure recommendations
        recommendations = self._parse_llm_response(llm_response, funding_sources)
        
        return recommendations
    
    def _create_recommendation_prompt(self, charity_name: str, mission: str, 
                                      focus_areas: List[str], 
                                      funding_sources: List[Dict[str, Any]]) -> str:
        """Create a prompt for the LLM to generate recommendations"""
        
        funding_list = "\n".join([
            f"- {source['name']}: Focus areas: {', '.join(source['focus_areas'])}"
            for source in funding_sources
        ])
        
        prompt = f"""
        Analyze the following charity and recommend the best funding opportunities for them.
        
        Charity Name: {charity_name}
        Mission: {mission}
        Focus Areas: {', '.join(focus_areas)}
        
        Available Funding Sources:
        {funding_list}
        
        Please provide:
        1. Top 3 funding sources that align with this charity's mission
        2. Reasoning for each recommendation
        3. Specific alignment points between the charity and each funder
        4. Estimated probability of successful grant application (0-100%)
        5. Next steps for each opportunity
        
        Format your response as JSON with the following structure:
        {{
            "recommendations": [
                {{
                    "funder_name": "...",
                    "alignment_score": 0-100,
                    "reasoning": "...",
                    "alignment_points": ["..."],
                    "next_steps": ["..."]
                }}
            ]
        }}
        """
        
        return prompt
    
    def _parse_llm_response(self, response: str, 
                           funding_sources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Parse LLM response and structure recommendations"""
        
        recommendations = []
        
        try:
            # Try to extract JSON from response
            import re
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                parsed = json.loads(json_match.group())
                recommendations = parsed.get("recommendations", [])
        except (json.JSONDecodeError, AttributeError):
            # If parsing fails, return empty recommendations
            pass
        
        return recommendations
    
    def score_alignment(self, charity_focus: List[str], 
                       funder_focus: List[str]) -> float:
        """Calculate alignment score between charity and funder"""
        
        if not charity_focus or not funder_focus:
            return 0.0
        
        matches = sum(1 for cf in charity_focus 
                     if any(ff.lower() in cf.lower() or cf.lower() in ff.lower() 
                           for ff in funder_focus))
        
        alignment_score = (matches / max(len(charity_focus), len(funder_focus))) * 100
        
        return min(alignment_score, 100)


class RecommendationFormatter:
    """Format recommendations for output"""
    
    @staticmethod
    def format_for_report(recommendations: List[Dict[str, Any]]) -> str:
        """Format recommendations as a readable report"""
        
        report = "# Funding Recommendations Report\n\n"
        report += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        for i, rec in enumerate(recommendations, 1):
            report += f"## Recommendation {i}: {rec.get('funder_name', 'Unknown')}\n\n"
            report += f"**Alignment Score:** {rec.get('alignment_score', 'N/A')}%\n\n"
            report += f"**Reasoning:** {rec.get('reasoning', 'N/A')}\n\n"
            
            if rec.get('alignment_points'):
                report += "**Alignment Points:**\n"
                for point in rec['alignment_points']:
                    report += f"- {point}\n"
                report += "\n"
            
            if rec.get('next_steps'):
                report += "**Next Steps:**\n"
                for step in rec['next_steps']:
                    report += f"1. {step}\n"
                report += "\n"
        
        return report
    
    @staticmethod
    def format_for_json(recommendations: List[Dict[str, Any]]) -> str:
        """Format recommendations as JSON"""
        return json.dumps(recommendations, indent=2)
