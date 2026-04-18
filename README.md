# LoveAdvisor V4

AI-powered emotional analysis and relationship decision assistant.

## Overview

LoveAdvisor V3 is a comprehensive system for analyzing interpersonal communication,
extracting emotional signals, and generating relationship advice using advanced
AI models.

## Project Structure

```
LoveAdvisorV4/
├── app/                    # Core application code
│   ├── api/               # API endpoints and routing
│   ├── core/              # Core application logic
│   ├── services/          # Business service layer
│   ├── llm/               # LLM integration and model management
│   ├── prompts/           # Prompt templates and management
│   ├── parsers/           # Data parsing and transformation
│   ├── schemas/           # Data models and validation schemas
│   └── utils/             # Helper functions and utilities
├── configs/               # Configuration files
├── frontend/              # Streamlit frontend application
├── web/                   # Next.js/React正式用户端前端 (V4新前端)
├── test_system/           # Testing infrastructure
│   ├── data/              # Test data and fixtures
│   ├── scripts/           # Test automation scripts
│   └── output/            # Test results and outputs
├── data/                  # Application data storage
│   ├── history/           # Historical data
│   ├── cache/             # Cached data
│   └── snapshots/         # Data snapshots
└── docs/                  # Documentation
    ├── architecture/      # Architecture documentation
    ├── dev_logs/          # Development logs
    ├── test_reports/      # Test reports
    └── product_notes/     # Product requirements
```

## Getting Started

### Prerequisites

- Python 3.8+
- Node.js 18+ (for Next.js frontend)
- Virtual environment (recommended)

### Installation

1. Clone the repository
2. Create and activate virtual environment
3. Install dependencies: `pip install -r requirements.txt`

### Running the Application

1. Start the backend API server:
   ```bash
   python run.py
   ```

2. Start the Streamlit frontend:
   ```bash
   streamlit run frontend/streamlit_app.py
   ```

3. Start the Next.js/React frontend (V4正式用户端):
   ```bash
   cd web
   npm install
   npm run dev
   ```

4. Access the application:
   - API: http://localhost:8000/docs
   - Streamlit Frontend: http://localhost:8501
   - Next.js Frontend (V4): http://localhost:3000

## Development

### Environment Setup

Copy `.env.example` to `.env` and configure your environment variables.

### Testing

Run the test suite:
```bash
pytest test_system/
```

## License

[License information to be added]

## Contributing

[Contribution guidelines to be added]