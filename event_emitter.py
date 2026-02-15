import json
import asyncio
from datetime import datetime
from typing import Dict, Any, Set
from fastapi import WebSocket

class EventEmitter:
    """Singleton event emitter for broadcasting real-time updates to connected clients"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.active_connections: Set[WebSocket] = set()
            cls._instance.loop = None
        return cls._instance
    
    def set_event_loop(self, loop):
        """Set the asyncio event loop for async operations"""
        self.loop = loop
    
    async def connect(self, websocket: WebSocket):
        """Register a new WebSocket connection"""
        await websocket.accept()
        self.active_connections.add(websocket)
        await self.emit("connection", {"message": "Connected to incident handler stream"})
    
    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection"""
        self.active_connections.discard(websocket)
    
    async def emit(self, event_type: str, data: Dict[str, Any]):
        """Broadcast an event to all connected clients"""
        if not self.active_connections:
            return
        
        message = {
            "type": event_type,
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        
        # Remove disconnected clients
        disconnected = set()
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.add(connection)
        
        self.active_connections -= disconnected
    
    def emit_sync(self, event_type: str, data: Dict[str, Any]):
        """Synchronous wrapper for emit - schedules the async emit"""
        if self.loop and self.loop.is_running():
            asyncio.run_coroutine_threadsafe(
                self.emit(event_type, data),
                self.loop
            )
    
    async def broadcast_incident_processing(self, incident_number: str, short_desc: str):
        """Broadcast that an incident is being processed"""
        await self.emit("incident_processing", {
            "incident_number": incident_number,
            "short_description": short_desc,
            "status": "processing"
        })
    
    async def broadcast_rule_matched(self, incident_number: str, rule: Dict[str, Any]):
        """Broadcast that a rule was matched for an incident"""
        await self.emit("rule_matched", {
            "incident_number": incident_number,
            "rule": rule,
            "status": "matched"
        })
    
    async def broadcast_incident_resolved(self, incident_number: str, rule_id: str):
        """Broadcast that an incident was resolved"""
        await self.emit("incident_resolved", {
            "incident_number": incident_number,
            "rule_id": rule_id,
            "status": "resolved"
        })
    
    async def broadcast_incident_skipped(self, incident_number: str, reason: str):
        """Broadcast that an incident was skipped"""
        await self.emit("incident_skipped", {
            "incident_number": incident_number,
            "reason": reason,
            "status": "skipped"
        })
    
    async def broadcast_error(self, incident_number: str, error: str):
        """Broadcast an error occurred during processing"""
        await self.emit("error_occurred", {
            "incident_number": incident_number,
            "error": error,
            "status": "error"
        })
    
    async def broadcast_execution_started(self, total_incidents: int):
        """Broadcast that execution has started"""
        await self.emit("execution_started", {
            "total_incidents": total_incidents,
            "status": "started"
        })
    
    async def broadcast_execution_completed(self, stats: Dict[str, int]):
        """Broadcast that execution has completed"""
        await self.emit("execution_completed", {
            "stats": stats,
            "status": "completed"
        })

# Global instance
emitter = EventEmitter()
