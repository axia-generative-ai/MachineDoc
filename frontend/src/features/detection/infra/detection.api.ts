import { apiClient } from '../../../shared/api/apiClient';

export type LogStatus = '정상' | '위험' | '오류';
export type DetectionDataType = 'TEMPERATURE' | 'VIBRATION';

export type EquipmentLogResult = {
  logId: number;
  equipmentId: number;
  dataType: DetectionDataType;
  value: number;
  status: LogStatus;
  occurredAt: string;
};

type BackendEquipmentLog = {
  log_id: number;
  equipment_id: number;
  data_type: DetectionDataType;
  value: number;
  status: LogStatus;
  occurred_at: string;
};

export const equipmentList = [
  { code: 'EQ-MOTOR-001', label: '정밀 모터 (Line A)' },
  { code: 'EQ-CONVEYOR-002', label: '표준 컨베이어 (Line A)' },
  { code: 'EQ-PRESS-003', label: '고온 프레스 (Line B)' },
  { code: 'EQ-ROBOT-004', label: '정밀 로봇 (Line B)' },
  { code: 'EQ-WELDING-005', label: '용접기 (Line C)' },
] as const;

export const detectionApi = {
  async createVirtualLog(equipmentCode: string) {
    const { data } = await apiClient.post<BackendEquipmentLog>(`/log/virtual/${equipmentCode}`);
    return {
      logId: data.log_id,
      equipmentId: data.equipment_id,
      dataType: data.data_type,
      value: data.value,
      status: data.status,
      occurredAt: data.occurred_at,
    } satisfies EquipmentLogResult;
  },
};
