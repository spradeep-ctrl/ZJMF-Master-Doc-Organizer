# ZJMF AI Agent - Funding Recommendations System

## Project Overview
An intelligent AI agent that analyzes the Zcharia Jose Memorial Foundation's funding document and provides tailored recommendations by combining information from the master document with real-time online research.

## Features
- Extract funding opportunities from the master PDF document
- Cross-reference with current online funding sources
- Generate personalized funding recommendations
- Track funding application deadlines and requirements
- Provide grant writing guidance

## Project Structure
```
.
├── README.md
├── requirements.txt
├── config/
│   └── config.yaml
├── data/
│   └── funding_doc.pdf
├── src/
│   ├── __init__.py
│   ├── agent.py              # Main AI agent logic
│   ├── document_processor.py # PDF parsing and analysis
│   ├── web_scraper.py        # Online research capabilities
│   ├── recommendation_engine.py # Generates recommendations
│   └── utils.py
├── tests/
│   └── test_agent.py
└── examples/
    └── sample_recommendations.json
```

## Getting Started
1. Install dependencies: `pip install -r requirements.txt`
2. Configure API keys in `config/config.yaml`
3. Run the agent: `python src/agent.py`

## Next Steps
- [ ] Set up LLM integration (OpenAI/Claude/Local LLM)
- [ ] Implement document parsing
- [ ] Build web search capabilities
- [ ] Create recommendation pipeline
- [ ] Add evaluation metrics
