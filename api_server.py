from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any
import asyncio
from event_emitter import emitter
from database_manager import DatabaseManager
import os

app = FastAPI(title="Incident Handler Dashboard")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database manager instance
db_manager = DatabaseManager()

@app.on_event("startup")
async def startup_event():
    """Set event loop on startup"""
    loop = asyncio.get_event_loop()
    emitter.set_event_loop(loop)

@app.get("/")
async def read_root():
    """Serve the frontend dashboard"""
    return FileResponse("frontend/index.html")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await emitter.connect(websocket)
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        emitter.disconnect(websocket)

@app.get("/api/history")
async def get_history(limit: int = 100) -> List[Dict[str, Any]]:
    """Get incident processing history"""
    return db_manager.get_processing_history(limit)

@app.get("/api/logs")
async def get_logs(limit: int = 100) -> List[Dict[str, Any]]:
    """Get execution logs"""
    return db_manager.get_recent_executions(limit)

@app.get("/api/statistics")
async def get_statistics() -> Dict[str, Any]:
    """Get processing statistics"""
    return db_manager.get_statistics()

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "database_mode": "postgres" if not db_manager.use_memory else "memory",
        "active_connections": len(emitter.active_connections)
    }

# Mount static files
if os.path.exists("frontend"):
    app.mount("/static", StaticFiles(directory="frontend"), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
