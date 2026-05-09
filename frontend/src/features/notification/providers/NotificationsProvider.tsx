import { createContext, useCallback, useContext, useEffect, useMemo, useRef, useState, type ReactNode } from 'react';

import { env } from '../../../shared/config/env';
import { authTokenStorage } from '../../../shared/storage/authToken.storage';

export type LiveNotification = {
  id: string;
  notificationId: number;
  level: '긴급' | '경고' | '주의';
  title: string;
  equipment: string;
  detail: string;
  createdAt: string;
  isUnread: boolean;
  suggestedErrorCode: string | null;
};

type Ctx = {
  notifications: LiveNotification[];
  unreadCount: number;
  isConnected: boolean;
  markAsRead: (id: string) => void;
  remove: (id: string) => void;
  clear: () => void;
};

const NotificationsContext = createContext<Ctx | null>(null);

type AnomalyPayload = {
  event?: string;
  data?: {
    notification_id?: number;
    log_id?: number;
    message?: string;
    is_read?: string;
    level?: string;
    occurred_at?: string;
    equipment_id?: number;
    equipment_code?: string;
    location?: string;
    suggested_error_code?: string | null;
  };
};

function levelToSeverity(level?: string): LiveNotification['level'] {
  if (level === '긴급' || level === '경고' || level === '주의') return level;
  return '주의';
}

function formatTimestamp(occurredAt?: string): string {
  if (!occurredAt) return new Date().toLocaleString('ko-KR');
  const date = new Date(occurredAt);
  if (Number.isNaN(date.getTime())) return occurredAt;
  return date.toLocaleString('ko-KR');
}

export function NotificationsProvider({ children }: { children: ReactNode }) {
  const [notifications, setNotifications] = useState<LiveNotification[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimerRef = useRef<number | null>(null);

  const handleAnomaly = useCallback((payload: AnomalyPayload) => {
    const data = payload.data;
    if (!data) return;
    const notification: LiveNotification = {
      id: `noti-${data.notification_id ?? Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
      notificationId: data.notification_id ?? 0,
      level: levelToSeverity(data.level),
      title: `${data.equipment_code ?? '설비'} 이상 감지`,
      equipment: data.equipment_code ?? '-',
      detail: data.message ?? '이상 감지 알림',
      createdAt: formatTimestamp(data.occurred_at),
      isUnread: true,
      suggestedErrorCode: data.suggested_error_code ?? null,
    };
    setNotifications((prev) => [notification, ...prev].slice(0, 50));
  }, []);

  const isCancelledRef = useRef(false);

  const connect = useCallback(() => {
    if (isCancelledRef.current) return;
    const token = authTokenStorage.getAccessToken();
    if (!token) return;
    if (!env.wsUrl) return;
    if (wsRef.current) return; // 이미 연결/연결 중이면 새로 만들지 않음 (StrictMode 이중 호출 가드)

    const url = `${env.wsUrl.replace(/\/$/, '')}/notifications`;
    let ws: WebSocket;
    try {
      ws = new WebSocket(url, token);
    } catch {
      return;
    }
    wsRef.current = ws;

    ws.onopen = () => {
      if (isCancelledRef.current) {
        ws.close();
        return;
      }
      setIsConnected(true);
    };
    ws.onmessage = (event) => {
      if (isCancelledRef.current) return;
      try {
        const payload = JSON.parse(event.data) as AnomalyPayload;
        if (payload.event === 'ANOMALY_DETECTED') handleAnomaly(payload);
      } catch {
        // ignore non-json
      }
    };
    ws.onclose = () => {
      setIsConnected(false);
      if (wsRef.current === ws) wsRef.current = null;
      if (isCancelledRef.current) return;
      if (reconnectTimerRef.current) window.clearTimeout(reconnectTimerRef.current);
      reconnectTimerRef.current = window.setTimeout(connect, 5000);
    };
    ws.onerror = () => {
      ws.close();
    };
  }, [handleAnomaly]);

  useEffect(() => {
    isCancelledRef.current = false;
    connect();
    return () => {
      isCancelledRef.current = true;
      if (reconnectTimerRef.current) {
        window.clearTimeout(reconnectTimerRef.current);
        reconnectTimerRef.current = null;
      }
      const ws = wsRef.current;
      wsRef.current = null;
      if (ws) {
        ws.onopen = null;
        ws.onmessage = null;
        ws.onclose = null;
        ws.onerror = null;
        if (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING) ws.close();
      }
    };
  }, [connect]);

  const markAsRead = useCallback((id: string) => {
    setNotifications((prev) => prev.map((item) => (item.id === id ? { ...item, isUnread: false } : item)));
  }, []);

  const remove = useCallback((id: string) => {
    setNotifications((prev) => prev.filter((item) => item.id !== id));
  }, []);

  const clear = useCallback(() => setNotifications([]), []);

  const value = useMemo<Ctx>(() => ({
    notifications,
    unreadCount: notifications.filter((item) => item.isUnread).length,
    isConnected,
    markAsRead,
    remove,
    clear,
  }), [notifications, isConnected, markAsRead, remove, clear]);

  return <NotificationsContext.Provider value={value}>{children}</NotificationsContext.Provider>;
}

export function useNotifications() {
  const ctx = useContext(NotificationsContext);
  if (!ctx) throw new Error('useNotifications must be used within NotificationsProvider');
  return ctx;
}
