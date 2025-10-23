# Profile Search - LinkedIn & Web Intelligence Tool

A hybrid web application that combines LinkedIn profile search with general web search capabilities, powered by AI-driven chat interface for follow-up questions and analysis.

## Features

### 🔍 Multi-Source Search
- **LinkedIn Profile Search**: Find LinkedIn profiles using Google Custom Search or SerpAPI
- **Web Search Enhancement**: General web search to enrich profile information
- **News Coverage**: Discover news articles and media mentions

### 💬 AI-Powered Chat Interface
- **Conversational Follow-ups**: Ask questions about search results
- **Context-Aware Responses**: AI understands your search context
- **Source Citations**: Responses include links to relevant sources
- **Chat History**: Full conversation history maintained per session

### 📊 Comprehensive Reports
- **Structured Reports**: Well-organized markdown reports
- **Multiple Views**: Summary, LinkedIn, Web, and News tabs
- **Downloadable**: Export reports in markdown format
- **Real-time Display**: Results shown immediately after search

## Architecture

```
┌─────────────────┐
│   Next.js UI    │ (React, TypeScript, Tailwind)
│  (Port 3000)    │
└────────┬────────┘
         │
         │ HTTP/REST
         ▼
┌─────────────────┐
│  FastAPI Backend│ (Python, Async)
│  (Port 8000)    │
└────────┬────────┘
         │
         ├──► Profile Search Modules
         │    ├── LinkedIn Searcher
         │    ├── Web Searcher
         │    └── Aggregator
         │
         ├──► Chat Handler (OpenAI)
         │
         └──► SQLite Database
              ├── Search Results
              └── Chat History
```

## Installation

### Prerequisites
- Python 3.9+
- Node.js 18+ and npm
- API Keys:
  - OpenAI API Key (required)
  - Google Custom Search API Key + CSE ID (recommended) OR SerpAPI Key

### Backend Setup

1. **Install Python dependencies:**
```bash
# Install base requirements (if not already installed)
pip install -r requirements.txt

# Install profile search requirements
pip install -r requirements-profile-search.txt
```

2. **Configure environment variables:**
```bash
cp .env.profile-search.example .env

# Edit .env and add your API keys
# At minimum, you need:
# - OPENAI_API_KEY
# - Either (GOOGLE_API_KEY + GOOGLE_CSE_ID) or SERP_API_KEY
```

3. **Start the FastAPI server:**
```bash
cd api
python main.py

# Server will start on http://localhost:8000
# API docs available at http://localhost:8000/docs
```

### Frontend Setup

1. **Install Node.js dependencies:**
```bash
cd web_ui
npm install
```

2. **Configure environment:**
```bash
# Create .env.local file
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
```

3. **Start the development server:**
```bash
npm run dev

# UI will start on http://localhost:3000
```

## Usage

### Quick Start

1. Open http://localhost:3000 in your browser
2. Enter a person's name in the search form
3. Optionally add company, title, or location to refine results
4. Click "Search Profile"
5. View results in the Report panel
6. Ask follow-up questions in the Chat panel

### Search Tips

**Basic Search:**
- Name: "John Doe"

**Refined Search:**
- Name: "Jane Smith"
- Company: "Microsoft"
- Title: "Software Engineer"
- Location: "Seattle, WA"

**Chat Examples:**
- "What is this person's background?"
- "Tell me about their current role"
- "Are there any news articles about them?"
- "What are their main skills and expertise?"

## API Documentation

### Endpoints

**POST /api/search**
Search for a profile across multiple sources.

```json
{
  "name": "John Doe",
  "company": "Acme Corp",
  "title": "CEO",
  "location": "San Francisco",
  "session_id": "optional_session_id"
}
```

**POST /api/chat**
Send a chat message and get AI response.

```json
{
  "session_id": "session_123",
  "message": "Tell me about their background",
  "search_id": "search_456"
}
```

**GET /api/history/{session_id}**
Get full session history including searches and chat.

**GET /api/report/{search_id}?format=markdown**
Get a report in specified format (markdown, text, or json).

**WebSocket /ws/chat/{session_id}**
Real-time chat via WebSocket (alternative to REST).

Full API documentation: http://localhost:8000/docs

## Project Structure

```
yooka/
├── profile_search/          # Search modules
│   ├── __init__.py
│   ├── linkedin_search.py   # LinkedIn search logic
│   ├── web_search.py        # General web search
│   └── aggregator.py        # Data aggregation & reports
│
├── api/                     # FastAPI backend
│   ├── __init__.py
│   ├── main.py              # FastAPI app & routes
│   ├── chat_handler.py      # OpenAI chat integration
│   └── database.py          # SQLite database handler
│
├── web_ui/                  # Next.js frontend
│   ├── src/
│   │   ├── pages/           # Next.js pages
│   │   ├── components/      # React components
│   │   ├── lib/             # API client
│   │   └── styles/          # CSS styles
│   └── package.json
│
├── database/                # SQLite database (auto-created)
│   └── profile_search.db
│
└── requirements-profile-search.txt
```

## Configuration

### Search Providers

**Google Custom Search (Recommended):**
- Free tier: 100 queries/day
- Setup: https://programmablesearchengine.google.com/
- More reliable results

**SerpAPI (Alternative):**
- Free tier: 100 searches/month
- Setup: https://serpapi.com/
- Easier setup, no CSE required

### Database

Uses SQLite by default. To use PostgreSQL:

1. Install: `pip install asyncpg`
2. Update `api/database.py` to use PostgreSQL connection
3. Set `DATABASE_URL` in `.env`

## Privacy & Ethics

⚠️ **Important Considerations:**

1. **Intended Use Cases:**
   - Professional networking and recruiting
   - Journalism and research
   - Personal branding analysis
   - Due diligence (legitimate purposes)

2. **Do NOT use for:**
   - Harassment or stalking
   - Unauthorized surveillance
   - Identity theft or fraud
   - Any illegal activities

3. **Best Practices:**
   - Respect privacy and data protection laws (GDPR, CCPA, etc.)
   - Only search for legitimate business purposes
   - Verify information from multiple sources
   - Don't store sensitive personal data long-term
   - Be transparent about how you use the information

4. **Data Handling:**
   - Search results are cached locally
   - Chat history is stored per session
   - Implement data retention policies
   - Provide opt-out mechanisms where required

## Testing

### Test Backend

```bash
# Test LinkedIn search
cd profile_search
python linkedin_search.py

# Test web search
python web_search.py

# Test aggregator
python aggregator.py

# Test database
cd ../api
python database.py

# Test chat handler
python chat_handler.py
```

### Test API

```bash
# Run FastAPI server
cd api
python main.py

# In another terminal, test endpoints
curl http://localhost:8000/health

# Test search (requires API keys)
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{"name": "Satya Nadella", "company": "Microsoft"}'
```

### Test Frontend

```bash
cd web_ui
npm run dev

# Open http://localhost:3000 in browser
# Perform a test search
```

## Troubleshooting

### API Key Issues

**Error: "Google API error: 403"**
- Check if Custom Search API is enabled
- Verify API key is correct
- Check if you've exceeded quota

**Error: "SerpAPI error: 401"**
- Verify API key is correct
- Check account status and credits

### Search Returns No Results

1. Try different search terms
2. Check if API services are working
3. Verify network connectivity
4. Check API quotas/limits

### Chat Not Working

1. Verify OPENAI_API_KEY is set
2. Check OpenAI account has credits
3. Check API rate limits
4. Review error logs in terminal

### Database Errors

1. Check write permissions in `database/` directory
2. Delete and recreate: `rm database/profile_search.db`
3. Restart backend server

## Development

### Adding New Search Sources

1. Create a new searcher in `profile_search/`
2. Implement async search methods
3. Add to aggregator in `aggregator.py`
4. Update UI to display new source

### Customizing AI Responses

Edit the system prompt in `api/chat_handler.py`:

```python
def _build_system_prompt(self, search_context):
    base_prompt = """Your custom instructions here..."""
    # ...
```

### Styling

Frontend uses Tailwind CSS. Edit styles in:
- `web_ui/src/styles/globals.css` - Global styles
- `web_ui/tailwind.config.js` - Tailwind configuration
- Components use inline Tailwind classes

## Production Deployment

### Backend

1. Use production WSGI server (Gunicorn + Uvicorn)
2. Set up proper environment variables
3. Use PostgreSQL instead of SQLite
4. Implement rate limiting
5. Add authentication/authorization
6. Set up HTTPS

### Frontend

1. Build for production: `npm run build`
2. Deploy to Vercel, Netlify, or similar
3. Update API_URL to production backend
4. Enable environment variable management

### Security Checklist

- [ ] Change CORS settings in production
- [ ] Implement API authentication
- [ ] Add rate limiting
- [ ] Enable HTTPS only
- [ ] Sanitize user inputs
- [ ] Implement CSP headers
- [ ] Set up monitoring and logging
- [ ] Regular security audits

## License

This project is provided for educational and research purposes. Users are responsible for complying with all applicable laws and terms of service of third-party APIs.

## Support

For issues, questions, or contributions, please refer to the main project README.

---

**Built with:**
- FastAPI (Backend)
- Next.js + React (Frontend)
- OpenAI GPT-4 (AI Chat)
- Google Custom Search / SerpAPI (Search)
- SQLite (Database)
- Tailwind CSS (Styling)
