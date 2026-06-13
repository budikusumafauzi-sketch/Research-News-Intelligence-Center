# Research & News Intelligence Center (RNIC)

## Project Overview
RNIC is a premium, AI-powered intelligence platform that unifies global news aggregation and academic research. It provides professionals, academics, and investors with a high-density, centralized dashboard for real-time intelligence, trend monitoring, and AI-driven summarization utilizing the Google Gemini API.

## Architecture
The platform follows an enterprise-grade Model-View-Controller (MVC) architecture adapted for Flask:
- **Backend**: Python 3.13, Flask (App Factory Pattern).
- **Database**: SQLAlchemy ORM for MySQL.
- **Frontend**: Custom HTML5/CSS3/JS, Bootstrap 5 (with overrides), Chart.js.
- **AI**: Google Gemini API.

## Folder Structure
```text
RNIC/
├── ai/               # AI integrations and prompt engineering services
├── database/         # Database migrations and initialization scripts
├── logs/             # Application logs
├── models/           # SQLAlchemy database models
├── routes/           # Blueprint controllers for application routing
├── scraper/          # Custom RSS, arXiv, and Crossref data ingestors
├── services/         # Core business logic (separated from routes)
├── static/           # Static assets
│   ├── css/          # Custom stylesheets (Red/White/Black aesthetic)
│   ├── icons/        # SVG icons and web fonts
│   ├── images/       # Image assets
│   └── js/           # Custom JavaScript and UI logic
├── templates/        # Jinja2 HTML templates
├── tests/            # Automated test suites
├── utils/            # Helper functions and shared utilities
├── .env.example      # Environment variable template
├── .gitignore        # Git ignore configurations
├── app.py            # Application entry point
├── config.py         # Environment-specific configuration classes
└── requirements.txt  # Python dependencies
```

## Installation Guide
1. **Clone the repository:**
   ```bash
   git clone <repository_url>
   cd "Research & News Intelligence Center"
   ```
2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # macOS/Linux:
   source venv/bin/activate
   ```
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Environment Setup
1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
2. Update `.env` with your secure credentials (e.g., Database URI, Gemini API Key).

## Development Workflow
To run the application locally in development mode:
```bash
python app.py
```
The server will start on `http://127.0.0.0:5000` with hot-reloading enabled.

## Future Phases Roadmap
- **Phase 1**: Project Foundation (Completed)
- **Phase 2**: Database Architecture
- **Phase 3**: News Aggregation Engine
- **Phase 4**: Research Aggregation Engine
- **Phase 5**: Gemini AI Engine
- **Phase 6**: Dashboard UI
- **Phase 7**: Analytics
- **Phase 8**: Optimization
- **Phase 9**: Deployment Preparation
