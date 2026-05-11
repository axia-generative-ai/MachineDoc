import type { NotificationSocketStatus, RealtimeNotification } from '../model/notification.types';

export type NotificationSubscriptionHandlers = {
  onStatusChange: (status: NotificationSocketStatus) => void;
  onNotification: (notification: RealtimeNotification) => void;
};

export type NotificationRepository = {
  subscribe(handlers: NotificationSubscriptionHandlers): () => void;
};
