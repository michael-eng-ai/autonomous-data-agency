from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any
import json
import asyncio
import sys
import os
import logging

# Carregar variáveis de ambiente do .env
from dotenv import load_dotenv
load_dotenv()

# Configuração de Logging Centralizado
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("agency_api")

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.routes import router as api_router
from core.agency_orchestrator import get_agency_orchestrator

app = FastAPI(title="Autonomous Data Agency API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket Manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: Dict[str, Any]):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                pass

manager = ConnectionManager()

# Middleware/Dependency to inject manager into orchestrator (conceptually)
# In reality, we will patch the orchestrator to call our manager.broadcast

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    await manager.connect(websocket)
    logger.info(f"WebSocket Client connected. Total: {len(manager.active_connections)}")
    try:
        while True:
            # Simple echo or command processing
            data = await websocket.receive_text()
            # For now, just keep alive - client messages are handled via HTTP
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info(f"WebSocket Client disconnected. Total: {len(manager.active_connections)}")

# Test endpoint to check WebSocket connections
@app.get("/ws-status")
async def ws_status():
    """Returns the current number of WebSocket connections."""
    return {
        "connections": len(manager.active_connections),
        "message": "WebSocket status"
    }

# Test endpoint to trigger a test event
@app.post("/test-event")
async def test_event():
    """Sends a test event through WebSocket to all connected clients."""
    await manager.broadcast({
        "type": "test_event",
        "data": {"message": "This is a test event", "timestamp": "now"}
    })
    return {
        "sent": True,
        "connections": len(manager.active_connections)
    }

# Include Routes
app.include_router(api_router)

# Startup event to initialize orchestrator hook
@app.on_event("startup")
async def startup_event():
    orchestrator = get_agency_orchestrator()

    # Configure WebSocket event broadcasting
    if hasattr(orchestrator, "set_event_callback"):
        async def broadcast_event(event_type: str, data: Any):
            if manager.active_connections:
                await manager.broadcast({"type": event_type, "data": data})

        # IMPORTANT: Set the main loop BEFORE setting the callback
        loop = asyncio.get_running_loop()
        if hasattr(orchestrator, "set_main_loop"):
            orchestrator.set_main_loop(loop)

        orchestrator.set_event_callback(broadcast_event)
        logger.info("WebSocket event broadcasting configured")
