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
  /** @deprecated suggestedErrorCodes[0]과 동일. 하위호환 위해 유지. */
  suggestedErrorCode?: string | null;
  suggestedErrorCodes: string[];
  isUnread: boolean;
};

export type NotificationSocketStatus = 'idle' | 'connecting' | 'connected' | 'disconnected' | 'error';
