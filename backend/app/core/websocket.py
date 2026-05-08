from typing import List
from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        # 활성화된 웹소켓 연결 리스트
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """새로운 클라이언트 연결 수락"""
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"📡 New WebSocket connection. Total: {len(self.active_connections)}")

    async def disconnect(self, websocket: WebSocket):
        """클라이언트 연결 해제"""
        self.active_connections.remove(websocket)
        print(f"🔌 WebSocket disconnected. Total: {len(self.active_connections)}")

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """특정 클라이언트에게만 메시지 전송"""
        await websocket.send_json(message)

    async def broadcast(self, message: dict):
        """접속 중인 모든 클라이언트에게 메시지 전송 (알림용)"""
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                # 연결이 끊긴 세션이 남아있을 경우 예외 처리
                print(f"❌ Broadcast failed for a connection: {e}")
                # 필요 시 여기서 리스트에서 제거하는 로직 추가

manager = ConnectionManager()