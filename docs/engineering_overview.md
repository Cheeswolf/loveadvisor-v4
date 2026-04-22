# LoveAdvisor V4

AI-powered emotional analysis and relationship decision assistant.

## Overview

LoveAdvisor V4 is a comprehensive system for analyzing interpersonal communication,
extracting emotional signals, and generating relationship advice using advanced
AI models.

### Key Features

- **Multi-modal input support**: Text chat analysis and image-to-text conversion
- **Multi-provider LLM integration**: Support for DeepSeek, OpenAI, Anthropic, and mock providers
- **Rule-based analysis engine**: Relationship stage and interest level inference
- **Dual frontend interface**: Next.js production frontend and Streamlit debug interface
- **Comprehensive testing system**: Automated test suites and debugging tools

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
├── scripts/               # Utility scripts and tools
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

#### Required Environment Variables

- `DEEPSEEK_API_KEY`: API key for DeepSeek LLM provider
- `DASHSCOPE_API_KEY`: API key for Aliyun DashScope (Qwen-OCR)

#### Optional Environment Variables

- `OPENAI_API_KEY`: API key for OpenAI models
- `ANTHROPIC_API_KEY`: API key for Anthropic models  
- `COZE_API_TOKEN`: Legacy Coze API token for V2.5 compatibility
- `I1_VISION_API_KEY`: OCR.space API key for image-to-text

See `.env.example` for all available configuration options.

### Testing

Run the test suite:
```bash
pytest test_system/
```

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please open an issue first to discuss proposed changes.