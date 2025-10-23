"""
FastAPI Backend for Profile Search Application

Provides REST API endpoints for profile search, chat functionality,
and report generation.
"""

import os
import sys
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from profile_search.aggregator import ProfileAggregator, ReportGenerator
from api.chat_handler import ChatHandler
from api.database import Database

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Global instances
aggregator = None
report_generator = None
chat_handler = None
database = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global aggregator, report_generator, chat_handler, database

    logger.info("Starting Profile Search API...")

    # Initialize components
    aggregator = ProfileAggregator()
    report_generator = ReportGenerator()
    chat_handler = ChatHandler()
    database = Database()
    await database.initialize()

    logger.info("Profile Search API ready!")

    yield

    # Cleanup
    logger.info("Shutting down Profile Search API...")
    await database.close()


# Create FastAPI app
app = FastAPI(
    title="Profile Search API",
    description="API for searching and analyzing LinkedIn profiles with AI-powered chat",
    version="0.1.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models
class SearchRequest(BaseModel):
    """Profile search request model."""
    name: str = Field(..., description="Person's name")
    company: Optional[str] = Field(None, description="Company name")
    title: Optional[str] = Field(None, description="Job title")
    location: Optional[str] = Field(None, description="Location")
    session_id: Optional[str] = Field(None, description="Session ID for chat continuity")


class SearchResponse(BaseModel):
    """Profile search response model."""
    success: bool
    search_id: str
    session_id: str
    data: Dict[str, Any]
    report: str
    timestamp: str


class ChatMessage(BaseModel):
    """Chat message model."""
    session_id: str = Field(..., description="Session ID")
    message: str = Field(..., description="User message")
    search_id: Optional[str] = Field(None, description="Related search ID")


class ChatResponse(BaseModel):
    """Chat response model."""
    session_id: str
    message: str
    timestamp: str
    sources: Optional[List[Dict[str, str]]] = None


# API Endpoints

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Profile Search API",
        "version": "0.1.0",
        "endpoints": {
            "search": "/api/search",
            "chat": "/api/chat",
            "history": "/api/history/{session_id}",
            "report": "/api/report/{search_id}"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/api/search", response_model=SearchResponse)
async def search_profile(request: SearchRequest):
    """
    Search for a person's profile across LinkedIn and web sources.

    This endpoint performs a comprehensive search and returns aggregated results.
    """
    try:
        logger.info(f"Search request for: {request.name}")

        # Perform search
        profile_data = await aggregator.search_and_aggregate(
            name=request.name,
            company=request.company,
            title=request.title,
            location=request.location
        )

        # Generate report
        report = report_generator.generate_markdown_report(profile_data)

        # Generate IDs
        search_id = f"search_{datetime.utcnow().timestamp()}"
        session_id = request.session_id or f"session_{datetime.utcnow().timestamp()}"

        # Save to database
        await database.save_search(
            search_id=search_id,
            session_id=session_id,
            search_query=request.dict(),
            results=profile_data
        )

        return SearchResponse(
            success=True,
            search_id=search_id,
            session_id=session_id,
            data=profile_data,
            report=report,
            timestamp=datetime.utcnow().isoformat()
        )

    except Exception as e:
        logger.error(f"Search error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/chat", response_model=ChatResponse)
async def chat(message: ChatMessage):
    """
    Handle chat messages and provide AI-powered responses.

    This endpoint allows users to ask follow-up questions about search results.
    """
    try:
        logger.info(f"Chat message from session {message.session_id}")

        # Get search context if search_id provided
        search_context = None
        if message.search_id:
            search_context = await database.get_search(message.search_id)

        # Get chat history
        chat_history = await database.get_chat_history(message.session_id)

        # Generate response
        response = await chat_handler.handle_message(
            message=message.message,
            search_context=search_context,
            chat_history=chat_history
        )

        # Save to database
        await database.save_chat_message(
            session_id=message.session_id,
            user_message=message.message,
            assistant_message=response["message"],
            search_id=message.search_id
        )

        return ChatResponse(
            session_id=message.session_id,
            message=response["message"],
            timestamp=datetime.utcnow().isoformat(),
            sources=response.get("sources")
        )

    except Exception as e:
        logger.error(f"Chat error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/history/{session_id}")
async def get_history(session_id: str):
    """
    Get chat history for a session.
    """
    try:
        history = await database.get_full_session(session_id)
        return {
            "session_id": session_id,
            "history": history,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"History retrieval error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/report/{search_id}")
async def get_report(search_id: str, format: str = "markdown"):
    """
    Get a report for a specific search.

    Args:
        search_id: The search ID
        format: Report format (markdown, text, json)
    """
    try:
        search_data = await database.get_search(search_id)

        if not search_data:
            raise HTTPException(status_code=404, detail="Search not found")

        profile_data = search_data["results"]

        if format == "text":
            report = report_generator.generate_text_report(profile_data)
        elif format == "json":
            report = report_generator.generate_json_report(profile_data)
        else:  # markdown
            report = report_generator.generate_markdown_report(profile_data)

        return {
            "search_id": search_id,
            "format": format,
            "report": report,
            "timestamp": datetime.utcnow().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Report generation error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.websocket("/ws/chat/{session_id}")
async def websocket_chat(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for real-time chat.
    """
    await websocket.accept()
    logger.info(f"WebSocket connection established for session {session_id}")

    try:
        while True:
            # Receive message
            data = await websocket.receive_json()
            message = data.get("message", "")
            search_id = data.get("search_id")

            # Get context
            search_context = None
            if search_id:
                search_context = await database.get_search(search_id)

            chat_history = await database.get_chat_history(session_id)

            # Generate response
            response = await chat_handler.handle_message(
                message=message,
                search_context=search_context,
                chat_history=chat_history
            )

            # Save to database
            await database.save_chat_message(
                session_id=session_id,
                user_message=message,
                assistant_message=response["message"],
                search_id=search_id
            )

            # Send response
            await websocket.send_json({
                "type": "message",
                "message": response["message"],
                "sources": response.get("sources"),
                "timestamp": datetime.utcnow().isoformat()
            })

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for session {session_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}", exc_info=True)
        await websocket.close()


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
