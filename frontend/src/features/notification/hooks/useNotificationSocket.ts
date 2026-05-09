import { useCallback, useEffect, useMemo, useState } from 'react';

import { notificationRepositoryImpl } from '../infra/notification.repository.impl';
import type { NotificationSocketStatus, RealtimeNotification } from '../model/notification.types';
import { subscribeNotificationsUseCase } from '../usecase/subscribeNotifications.usecase';

export function useNotificationSocket() {
  const [notifications, setNotifications] = useState<RealtimeNotification[]>([]);
  const [status, setStatus] = useState<NotificationSocketStatus>('idle');

  const unreadCount = useMemo(() => notifications.filter((notification) => notification.isUnread).length, [notifications]);

  const markAllRead = useCallback(() => {
    setNotifications((prev) => prev.map((notification) => ({ ...notification, isUnread: false })));
  }, []);

  const dismissNotification = useCallback((id: string) => {
    setNotifications((prev) => prev.filter((notification) => notification.id !== id));
  }, []);

  useEffect(() => {
    return subscribeNotificationsUseCase(notificationRepositoryImpl, {
      onStatusChange: setStatus,
      onNotification: (notification) => {
        setNotifications((prev) => [notification, ...prev.filter((item) => item.id !== notification.id)].slice(0, 30));
      },
    });
  }, []);

  return {
    notifications,
    unreadCount,
    status,
    markAllRead,
    dismissNotification,
  };
}
