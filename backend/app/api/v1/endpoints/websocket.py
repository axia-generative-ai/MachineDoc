from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status
from jose import JWTError, jwt

from app.core.config import config
from app.core.websocket import manager

router = APIRouter()


@router.websocket("/notifications")
async def websocket_endpoint(websocket: WebSocket):
    # 클라이언트가 보낸 서브프로토콜 첫 항목으로 access_token을 받음
    subprotocols = websocket.scope.get("subprotocols", [])
    token = subprotocols[0] if subprotocols else None

    if not token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    try:
        jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
    except JWTError:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await websocket.accept(subprotocol=token)
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        await manager.disconnect(websocket)
