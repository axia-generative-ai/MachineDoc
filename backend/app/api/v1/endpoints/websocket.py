from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status
from app.core.websocket import manager
from app.service.auth_service import auth_service

router = APIRouter()

@router.websocket("/notifications")
async def websocket_endpoint(websocket: WebSocket):
    # 클라이언트가 보낸 서브프로토콜 리스트 확인
    subprotocols = websocket.scope.get("subprotocols", [])
    
    # 관례적으로 첫 번째 프로토콜 자리에 토큰을 실어 보냅니다.
    token = subprotocols[0] if subprotocols else None
    
    if not token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    try:
        auth_service.verify_token(token)
        # 클라이언트와 협의된 프로토콜명을 응답 헤더에 포함하여 연결 수락
        await websocket.accept(subprotocol=token) 
        await manager.connect(websocket)
        try:
            while True:
                # 클라이언트로부터의 메시지를 수신 대기 (연결 유지)
                await websocket.receive_text() 
        except WebSocketDisconnect:
            await manager.disconnect(websocket)
    except Exception:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        
