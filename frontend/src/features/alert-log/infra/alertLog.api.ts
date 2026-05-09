import { apiClient } from '../../../shared/api/apiClient';

export type NotificationLevel = '긴급' | '경고' | '주의';
export type ReadStatus = '미확인' | '확인' | '완료';

export type AlertLogItem = {
  notificationId: number;
  logId: number;
  message: string;
  isRead: ReadStatus;
  level: NotificationLevel;
  occurredAt: string;
  equipmentId: number;
  equipmentCode: string;
  location: string;
  suggestedErrorCode: string | null;
};

type BackendNotification = {
  notification_id: number;
  log_id: number;
  message: string;
  is_read: ReadStatus;
  level: NotificationLevel;
  occurred_at: string;
  equipment_id: number;
  equipment_code: string;
  location: string;
  suggested_error_code: string | null;
};

function mapNotification(data: BackendNotification): AlertLogItem {
  return {
    notificationId: data.notification_id,
    logId: data.log_id,
    message: data.message,
    isRead: data.is_read,
    level: data.level,
    occurredAt: data.occurred_at,
    equipmentId: data.equipment_id,
    equipmentCode: data.equipment_code,
    location: data.location,
    suggestedErrorCode: data.suggested_error_code ?? null,
  };
}

export const alertLogApi = {
  async list(limit = 100): Promise<AlertLogItem[]> {
    const { data } = await apiClient.get<BackendNotification[]>('/notifications', { params: { limit } });
    return data.map(mapNotification);
  },
  async updateReadStatus(notificationId: number, isRead: ReadStatus): Promise<AlertLogItem> {
    const { data } = await apiClient.patch<BackendNotification>(`/notifications/${notificationId}`, { is_read: isRead });
    return mapNotification(data);
  },
};
