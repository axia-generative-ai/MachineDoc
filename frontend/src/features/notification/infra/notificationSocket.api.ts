import { env } from '../../../shared/config/env';
import { authTokenStorage } from '../../../shared/storage/authToken.storage';
import type { NotificationSubscriptionHandlers } from '../domain/notification.repository';
import type { NotificationSeverity, RealtimeNotification } from '../model/notification.types';

type BackendNotificationPayload = {
  notification_id?: number | string;
  equipment_code?: string;
  location?: string;
  message?: string;
  level?: string;
  occured_at?: string;
  occurred_at?: string;
  suggested_error_code?: string | null;
  suggested_error_codes?: string[];
};

type BackendNotificationMessage = {
  event?: string;
  data?: BackendNotificationPayload;
};

function getWebSocketUrl() {
  if (env.wsUrl) {
    return `${env.wsUrl.replace(/\/$/, '')}/notifications`;
  }

  return `${env.apiBaseUrl.replace(/^http/, 'ws').replace(/\/api\/v1\/?$/, '')}/ws/v1/notifications`;
}

function mapSeverity(level?: string): NotificationSeverity {
  const normalized = (level ?? '').toUpperCase();

  if (normalized.includes('URGENT') || level?.includes('긴급')) return '긴급';
  if (normalized.includes('WARNING') || normalized.includes('WARN') || level?.includes('경고')) return '경고';
  return '주의';
}

function formatCreatedAt(value?: string) {
  if (!value) return new Date().toLocaleString('ko-KR');

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;

  return date.toLocaleString('ko-KR', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  });
}

function mapNotification(payload: BackendNotificationPayload): RealtimeNotification {
  const equipment = payload.equipment_code ?? 'UNKNOWN';
  const notificationId = payload.notification_id == null ? null : Number(payload.notification_id);

  // 다중 코드 우선, 없으면 단일 필드를 1원소 리스트로. 둘 다 없으면 빈 리스트.
  const codes = payload.suggested_error_codes && payload.suggested_error_codes.length > 0
    ? payload.suggested_error_codes
    : payload.suggested_error_code
      ? [payload.suggested_error_code]
      : [];

  return {
    id: String(payload.notification_id ?? `${Date.now()}-${Math.random()}`),
    notificationId: Number.isNaN(notificationId) ? null : notificationId,
    severity: mapSeverity(payload.level),
    title: `${equipment} 이상 감지`,
    equipment,
    detail: payload.message ?? '이상 징후가 감지되었습니다.',
    createdAt: formatCreatedAt(payload.occured_at ?? payload.occurred_at),
    location: payload.location,
    suggestedErrorCode: codes[0] ?? null,
    suggestedErrorCodes: codes,
    isUnread: true,
  };
}

function parseNotificationMessage(data: string) {
  const message = JSON.parse(data) as BackendNotificationMessage;

  if (message.event !== 'ANOMALY_DETECTED' || !message.data) {
    return null;
  }

  return mapNotification(message.data);
}

export const notificationSocketApi = {
  subscribe(handlers: NotificationSubscriptionHandlers) {
    let reconnectTimer: number | null = null;
    let shouldReconnect = true;
    let socket: WebSocket | undefined;

    const connect = () => {
      const accessToken = authTokenStorage.getAccessToken();

      if (!accessToken) {
        handlers.onStatusChange('idle');
        return;
      }

      handlers.onStatusChange('connecting');
      socket = new WebSocket(getWebSocketUrl(), accessToken);

      socket.onopen = () => {
        handlers.onStatusChange('connected');
      };

      socket.onmessage = (event) => {
        try {
          const notification = parseNotificationMessage(event.data);

          if (notification) {
            handlers.onNotification(notification);
          }
        } catch {
          handlers.onStatusChange('error');
        }
      };

      socket.onerror = () => {
        handlers.onStatusChange('error');
      };

      socket.onclose = (event) => {
        handlers.onStatusChange(event.code === 1000 ? 'disconnected' : 'error');

        if (shouldReconnect && event.code !== 1000 && event.code !== 1008) {
          reconnectTimer = window.setTimeout(connect, 3000);
        }
      };
    };

    connect();

    return () => {
      shouldReconnect = false;

      if (reconnectTimer) {
        window.clearTimeout(reconnectTimer);
      }

      socket?.close(1000);
    };
  },
};
