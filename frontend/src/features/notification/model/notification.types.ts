export type NotificationSeverity = '긴급' | '경고' | '주의';

export type RealtimeNotification = {
  id: string;
  notificationId: number | null;
  severity: NotificationSeverity;
  title: string;
  equipment: string;
  detail: string;
  createdAt: string;
  location?: string;
  suggestedErrorCode?: string | null;
  isUnread: boolean;
};

export type NotificationSocketStatus = 'idle' | 'connecting' | 'connected' | 'disconnected' | 'error';
