import { apiClient } from '../../../shared/api/apiClient';

export type LogStatus = '정상' | '위험' | '오류';
export type DetectionDataType = 'TEMPERATURE' | 'VIBRATION';
export type EquipmentLocation = 'LINE_A' | 'LINE_B' | 'LINE_C';
export type EquipmentState = 'RUNNING' | 'STOPPED' | 'ERROR';

export type Equipment = {
  equipmentId: number;
  equipmentCode: string;
  location: EquipmentLocation;
  state: EquipmentState;
};

export type EquipmentLogResult = {
  logId: number;
  equipmentId: number;
  dataType: DetectionDataType;
  value: number;
  status: LogStatus;
  occurredAt: string;
};

type BackendEquipment = {
  equipment_id: number;
  equipment_code: string;
  location: EquipmentLocation;
  state: EquipmentState;
};

type BackendEquipmentLog = {
  log_id: number;
  equipment_id: number;
  data_type: DetectionDataType;
  value: number;
  status: LogStatus;
  occurred_at: string;
};

export const detectionApi = {
  async listEquipments(): Promise<Equipment[]> {
    const { data } = await apiClient.get<BackendEquipment[]>('/equipment');
    return data.map((row) => ({
      equipmentId: row.equipment_id,
      equipmentCode: row.equipment_code,
      location: row.location,
      state: row.state,
    }));
  },
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
