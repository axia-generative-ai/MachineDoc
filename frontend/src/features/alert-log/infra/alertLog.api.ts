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
  /** @deprecated suggestedErrorCodes[0]과 동일. 하위호환 위해 유지. */
  suggestedErrorCode: string | null;
  suggestedErrorCodes: string[];
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
  suggested_error_codes?: string[];
};

function mapNotification(data: BackendNotification): AlertLogItem {
  const codes = data.suggested_error_codes && data.suggested_error_codes.length > 0
    ? data.suggested_error_codes
    : data.suggested_error_code
      ? [data.suggested_error_code]
      : [];

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
    suggestedErrorCode: codes[0] ?? null,
    suggestedErrorCodes: codes,
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
