from typing import List
from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        # 활성화된 웹소켓 연결 리스트
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """이미 accept 된 WebSocket을 풀에 등록"""
        self.active_connections.append(websocket)
        print(f"[WS] New connection. Total: {len(self.active_connections)}")

    async def disconnect(self, websocket: WebSocket):
        """클라이언트 연결 해제"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        print(f"[WS] Disconnected. Total: {len(self.active_connections)}")

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """특정 클라이언트에게만 메시지 전송"""
        await websocket.send_json(message)

    async def broadcast(self, message: dict):
        """접속 중인 모든 클라이언트에게 메시지 전송 (알림용)"""
        dead = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                print(f"[WS] Broadcast failed: {e}")
                dead.append(connection)
        for connection in dead:
            if connection in self.active_connections:
                self.active_connections.remove(connection)

manager = ConnectionManager()