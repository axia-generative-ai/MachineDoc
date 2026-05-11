import { useCallback, useEffect, useMemo, useRef, useState } from 'react';

import { alertLogApi, type AlertLogItem } from '../../alert-log/infra/alertLog.api';
import { authTokenStorage } from '../../../shared/storage/authToken.storage';
import { notificationRepositoryImpl } from '../infra/notification.repository.impl';
import type { NotificationSeverity, NotificationSocketStatus, RealtimeNotification } from '../model/notification.types';
import { subscribeNotificationsUseCase } from '../usecase/subscribeNotifications.usecase';

const MAX_ITEMS = 50;

function levelToSeverity(level?: string): NotificationSeverity {
  if (level === '긴급' || level === '경고' || level === '주의') return level;
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

function alertLogItemToRealtime(row: AlertLogItem): RealtimeNotification {
  return {
    id: `noti-seed-${row.notificationId}`,
    notificationId: row.notificationId,
    severity: levelToSeverity(row.level),
    title: `${row.equipmentCode ?? '설비'} 이상 감지`,
    equipment: row.equipmentCode ?? '-',
    detail: row.message,
    createdAt: formatCreatedAt(row.occurredAt),
    location: row.location,
    suggestedErrorCode: row.suggestedErrorCode ?? null,
    isUnread: row.isRead === '미확인',
  };
}

function mergeWithDedup(prev: RealtimeNotification[], next: RealtimeNotification): RealtimeNotification[] {
  // notificationId(number > 0) 우선 dedup. 없으면 id(string) fallback.
  // WS 재연결 시 같은 알림이 다시 들어와도 중복 안됨.
  const filtered = next.notificationId != null && next.notificationId > 0
    ? prev.filter((item) => item.notificationId !== next.notificationId)
    : prev.filter((item) => item.id !== next.id);
  return [next, ...filtered].slice(0, MAX_ITEMS);
}

export function useNotificationSocket() {
  const [notifications, setNotifications] = useState<RealtimeNotification[]>([]);
  const [status, setStatus] = useState<NotificationSocketStatus>('idle');
  const seededRef = useRef(false);

  const unreadCount = useMemo(() => notifications.filter((notification) => notification.isUnread).length, [notifications]);

  const markAllRead = useCallback(() => {
    setNotifications((prev) => prev.map((notification) => ({ ...notification, isUnread: false })));
  }, []);

  const dismissNotification = useCallback((id: string) => {
    setNotifications((prev) => prev.filter((notification) => notification.id !== id));
  }, []);

  const clearNotifications = useCallback(() => {
    setNotifications([]);
  }, []);

  // 마운트 시 과거 알림 시드. WS 는 미래 이벤트만 받기 때문에 페이지 새로고침 후
  // 그 전에 발생한 알림이 사라지는 것을 막는다. 401/네트워크 실패는 graceful degrade.
  useEffect(() => {
    if (seededRef.current) return;
    seededRef.current = true;
    if (!authTokenStorage.getAccessToken()) return;
    let cancelled = false;
    alertLogApi.list(MAX_ITEMS)
      .then((items) => {
        if (cancelled) return;
        const seeded = items.map(alertLogItemToRealtime);
        setNotifications((prev) => {
          // 이미 WS 로 들어온 알림은 그대로 두고 중복 없는 seed 만 합친다.
          const existingIds = new Set(
            prev
              .map((p) => p.notificationId)
              .filter((nid): nid is number => nid != null && nid > 0)
          );
          const merged = [...prev, ...seeded.filter((s) => s.notificationId == null || !existingIds.has(s.notificationId))];
          return merged.slice(0, MAX_ITEMS);
        });
      })
      .catch(() => {
        // 인증 실패/오프라인 → WS 만 의지
      });
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    return subscribeNotificationsUseCase(notificationRepositoryImpl, {
      onStatusChange: setStatus,
      onNotification: (notification) => {
        setNotifications((prev) => mergeWithDedup(prev, notification));
      },
    });
  }, []);

  return {
    notifications,
    unreadCount,
    status,
    markAllRead,
    dismissNotification,
    clearNotifications,
  };
}
