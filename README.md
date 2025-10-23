# LinkedIn Profile Search Intelligence Tool

A powerful, AI-enhanced web application for searching and analyzing professional profiles across LinkedIn and the web. Built with FastAPI, Next.js, and OpenAI.

![Status](https://img.shields.io/badge/status-active-success.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## 🚀 Features

### Multi-Source Profile Search
- **LinkedIn Profile Discovery**: Search LinkedIn profiles via Google Custom Search or SerpAPI
- **Web Presence Analysis**: Comprehensive web search to find additional information
- **News Coverage**: Discover news articles and media mentions
- **Intelligent Aggregation**: Combines all sources into coherent reports

### AI-Powered Chat Interface
- **Conversational Q&A**: Ask follow-up questions about search results in natural language
- **Context-Aware Responses**: AI understands your search context and provides relevant insights
- **Source Citations**: All responses include links to original sources
- **Session History**: Full conversation history maintained for each session

### Professional Reports
- **Multiple Views**: Summary, LinkedIn, Web, and News sections
- **Markdown Export**: Download reports for documentation
- **Real-Time Display**: Results appear immediately after search
- **Clean Organization**: Structured data presentation

## 📸 Interface

The application features a three-column layout:
- **Left**: Search form with filters (name, company, title, location)
- **Middle**: Report display with tabbed views
- **Right**: AI chat interface for questions and analysis

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│         Next.js Frontend (Port 3000)            │
│    React + TypeScript + Tailwind CSS            │
└─────────────────┬───────────────────────────────┘
                  │ HTTP/REST + WebSocket
┌─────────────────▼───────────────────────────────┐
│        FastAPI Backend (Port 8000)              │
│         Python + Async + Pydantic               │
└─────────────────┬───────────────────────────────┘
                  │
         ┌────────┴────────┐
         │                 │
┌────────▼────────┐ ┌─────▼──────┐
│  Search Engine  │ │  AI Chat   │
│   - LinkedIn    │ │  - OpenAI  │
│   - Web         │ │  - Context │
│   - News        │ │  - History │
└────────┬────────┘ └─────┬──────┘
         │                 │
         └────────┬────────┘
                  │
         ┌────────▼────────┐
         │ SQLite Database │
         │  - Searches     │
         │  - Chat History │
         └─────────────────┘
```

## 📋 Prerequisites

- **Python 3.9+**
- **Node.js 18+** and npm
- **API Keys** (see Setup section)

## 🛠️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/danielfae/yooka.git
cd yooka
```

### 2. Backend Setup

```bash
# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your API keys
```

### 3. Frontend Setup

```bash
cd web_ui

# Install dependencies
npm install

# Configure environment
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
```

### 4. Get API Keys

You need the following API keys:

#### OpenAI API Key (Required)
1. Visit https://platform.openai.com/
2. Create an account or sign in
3. Go to API Keys section
4. Create a new API key
5. Add to `.env`: `OPENAI_API_KEY=sk-...`

#### Search API (Choose One)

**Option A: Google Custom Search (Recommended)**
1. Create project at https://console.cloud.google.com/
2. Enable Custom Search API
3. Create credentials (API Key)
4. Create Custom Search Engine at https://programmablesearchengine.google.com/
5. Add to `.env`:
   ```
   GOOGLE_API_KEY=your_api_key
   GOOGLE_CSE_ID=your_cse_id
   ```

**Option B: SerpAPI (Alternative)**
1. Sign up at https://serpapi.com/
2. Get API key from dashboard
3. Add to `.env`: `SERP_API_KEY=your_api_key`

## 🚀 Running the Application

### Start Backend Server

```bash
# From project root
cd api
python main.py
```

Backend runs at: http://localhost:8000
API docs at: http://localhost:8000/docs

### Start Frontend

```bash
# In a new terminal
cd web_ui
npm run dev
```

Frontend runs at: http://localhost:3000

## 💡 Usage

### Basic Search

1. Open http://localhost:3000 in your browser
2. Enter a person's name in the search form
3. Click "Search Profile"
4. View results in the Report panel

### Advanced Search

Add optional filters for better results:
- **Company**: e.g., "Microsoft"
- **Title**: e.g., "Software Engineer"
- **Location**: e.g., "Seattle, WA"

### Using the AI Chat

After searching, ask questions like:
- "What is this person's background?"
- "Tell me about their current role"
- "What companies have they worked for?"
- "Are there any news articles about them?"
- "What are their main areas of expertise?"

### Exporting Reports

Click the "Download" button in the Report panel to export as Markdown.

## 📁 Project Structure

```
yooka/
├── api/                        # FastAPI backend
│   ├── main.py                # API routes & server
│   ├── chat_handler.py        # OpenAI integration
│   └── database.py            # SQLite handler
│
├── profile_search/            # Search modules
│   ├── linkedin_search.py    # LinkedIn search
│   ├── web_search.py         # Web & news search
│   └── aggregator.py         # Report generation
│
├── web_ui/                    # Next.js frontend
│   ├── src/
│   │   ├── pages/            # Next.js pages
│   │   │   └── index.tsx     # Main app page
│   │   ├── components/       # React components
│   │   │   ├── SearchForm.tsx
│   │   │   ├── ChatInterface.tsx
│   │   │   └── ReportDisplay.tsx
│   │   ├── lib/
│   │   │   └── api.ts        # API client
│   │   └── styles/
│   │       └── globals.css   # Global styles
│   └── package.json
│
├── database/                  # SQLite database (auto-created)
│   └── profile_search.db
│
├── .env.example              # Environment template
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## 🔌 API Endpoints

### Search Profile
```http
POST /api/search
Content-Type: application/json

{
  "name": "John Doe",
  "company": "Acme Corp",
  "title": "CEO",
  "location": "San Francisco"
}
```

### Chat
```http
POST /api/chat
Content-Type: application/json

{
  "session_id": "session_123",
  "message": "Tell me about their background",
  "search_id": "search_456"
}
```

### Get History
```http
GET /api/history/{session_id}
```

### Get Report
```http
GET /api/report/{search_id}?format=markdown
```

Full API documentation: http://localhost:8000/docs

## ⚙️ Configuration

### Environment Variables

```bash
# OpenAI (Required)
OPENAI_API_KEY=sk-...

# Google Custom Search (Option 1)
GOOGLE_API_KEY=...
GOOGLE_CSE_ID=...

# SerpAPI (Option 2)
SERP_API_KEY=...
```

### Database

By default, uses SQLite (`database/profile_search.db`). To use PostgreSQL:

1. Install: `pip install asyncpg`
2. Update `api/database.py`
3. Set `DATABASE_URL` in `.env`

## 🔒 Privacy & Ethics

### ⚠️ Important Guidelines

**Intended Use:**
- Professional networking and recruiting
- Journalism and research with proper attribution
- Due diligence for legitimate business purposes
- Personal branding analysis

**DO NOT Use For:**
- Harassment, stalking, or surveillance
- Identity theft or fraud
- Unauthorized data collection
- Any illegal activities

**Best Practices:**
- Comply with data protection laws (GDPR, CCPA, etc.)
- Use only for legitimate purposes
- Verify information from multiple sources
- Respect privacy boundaries
- Be transparent about data usage

## 🧪 Testing

### Test Backend Modules

```bash
# Test LinkedIn search
python profile_search/linkedin_search.py

# Test web search
python profile_search/web_search.py

# Test aggregator
python profile_search/aggregator.py
```

### Test API

```bash
# Health check
curl http://localhost:8000/health

# Test search
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{"name": "Satya Nadella", "company": "Microsoft"}'
```

## 🐛 Troubleshooting

### API Key Issues

**"Google API error: 403"**
- Enable Custom Search API in Google Cloud Console
- Verify API key is correct
- Check quotas

**"OpenAI API error"**
- Verify API key is valid
- Check account has credits
- Review rate limits

### No Search Results

- Try different search terms
- Verify API services are working
- Check network connectivity
- Review API quotas/limits

### Frontend Issues

**"Cannot connect to API"**
- Ensure backend is running on port 8000
- Check `NEXT_PUBLIC_API_URL` in `.env.local`
- Verify CORS settings

## 📊 Performance

- **Search Speed**: 2-5 seconds (depending on API)
- **Chat Response**: 1-3 seconds
- **Database**: Handles 1000+ searches efficiently
- **Concurrent Users**: Supports multiple simultaneous searches

## 🚀 Deployment

### Backend (Production)

```bash
# Use production WSGI server
pip install gunicorn
gunicorn api.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker
```

### Frontend (Production)

```bash
cd web_ui
npm run build
npm start
```

Or deploy to:
- **Vercel** (recommended for Next.js)
- **Netlify**
- **AWS Amplify**

### Production Checklist

- [ ] Update CORS settings
- [ ] Add authentication
- [ ] Enable rate limiting
- [ ] Use HTTPS only
- [ ] Set up monitoring
- [ ] Configure logging
- [ ] Regular backups

## 📚 Additional Documentation

For more detailed documentation, see [PROFILE_SEARCH_README.md](PROFILE_SEARCH_README.md)

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📝 License

This project is provided for educational and research purposes. Users are responsible for complying with all applicable laws and API terms of service.

## 🙏 Acknowledgments

Built with:
- [FastAPI](https://fastapi.tiangolo.com/) - Backend framework
- [Next.js](https://nextjs.org/) - Frontend framework
- [OpenAI](https://openai.com/) - AI chat capabilities
- [Tailwind CSS](https://tailwindcss.com/) - Styling

## 📧 Support

For issues or questions:
- Open an issue on GitHub
- Check the troubleshooting section
- Review API documentation at `/docs`

---

**⚡ Quick Start Command:**

```bash
# Terminal 1 - Backend
cd api && python main.py

# Terminal 2 - Frontend
cd web_ui && npm run dev

# Open http://localhost:3000
```
