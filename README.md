# Research & News Intelligence Center (RNIC)

AI-powered intelligence platform for real-time news aggregation, academic research discovery, trend analysis, and strategic insights.

---

## Overview

Research & News Intelligence Center (RNIC) is a modern intelligence platform that combines real-time global news monitoring with academic research discovery in a single unified dashboard.

The platform leverages Artificial Intelligence to transform large volumes of information into actionable insights, enabling analysts, researchers, students, investors, and decision-makers to stay informed and identify emerging trends faster.

---

## Key Features

### Real-Time News Intelligence

* Multi-source RSS aggregation
* Topic categorization
* Entity extraction
* Trending topic monitoring

### Research Discovery

* Academic paper aggregation
* Research metadata analysis
* Cross-source information linking

### AI-Powered Insights

* Google Gemini integration
* Automated summarization
* Key point extraction
* Strategic intelligence generation

### Analytics Dashboard

* Trend visualization
* Topic analytics
* Source performance monitoring
* Intelligence metrics

### User Experience

* Responsive design
* Modern dashboard interface
* Bookmark management
* Fast navigation and filtering

---

## Technology Stack

| Category        | Technology                           |
| --------------- | ------------------------------------ |
| Backend         | Python 3.13, Flask                   |
| Database        | SQLAlchemy, MySQL                    |
| Frontend        | HTML5, CSS3, JavaScript, Bootstrap 5 |
| Charts          | Chart.js                             |
| AI              | Google Gemini API                    |
| Version Control | Git, GitHub                          |

---

## System Architecture

RNIC follows a modular MVC-inspired architecture designed for scalability and maintainability.

```text
Client Layer
    ↓
Flask Routes (Controllers)
    ↓
Business Services
    ↓
Database & External Sources
    ↓
AI Intelligence Engine
```

---

## Project Structure

```text
RNIC/
├── ai/
├── database/
├── models/
├── routes/
├── scraper/
├── services/
├── static/
├── templates/
├── tests/
├── utils/
├── app.py
├── config.py
└── requirements.txt
```

---

## Installation

```bash
git clone https://github.com/budikusumafauzi-sketch/Research-News-Intelligence-Center.git

cd Research-News-Intelligence-Center

python -m venv venv

venv\Scripts\activate

pip install -r requirements.txt

python app.py
```

---

## Environment Variables

Create a `.env` file:

```env
DATABASE_URI=your_database_uri
GEMINI_API_KEY=your_api_key
SECRET_KEY=your_secret_key
```

---

## Future Development

* Knowledge Graph Engine
* Advanced AI Research Assistant
* Predictive Trend Detection
* Multi-Language Intelligence Analysis
* Enterprise User Management
* REST API Platform

---

## Author

Fauzi Budikusuma

Developer of Research & News Intelligence Center (RNIC)

---

## License

MIT License
