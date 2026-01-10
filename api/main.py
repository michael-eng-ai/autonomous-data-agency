from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any
import json
import asyncio
import sys
import os

# Carregar variáveis de ambiente do .env
from dotenv import load_dotenv
load_dotenv()

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
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Simple echo or command processing
            data = await websocket.receive_text()
            # For now, just keep alive
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Include Routes
app.include_router(api_router)

# Startup event to initialize orchestrator hook
@app.on_event("startup")
async def startup_event():
    orchestrator = get_agency_orchestrator()
    
    # Monkey patch or set a callback on the orchestrator to broadcast events
    # This assumes we will add a 'set_event_callback' method to AgencyOrchestrator
    if hasattr(orchestrator, "set_event_callback"):
        async def broadcast_event(event_type: str, data: Any):
            await manager.broadcast({"type": event_type, "data": data})
        
        orchestrator.set_event_callback(broadcast_event)
        
        # Set main loop for thread-safe execution
        loop = asyncio.get_running_loop()
        if hasattr(orchestrator, "set_main_loop"):
            orchestrator.set_main_loop(loop)
            
        print("Orchestrator event callback set")
