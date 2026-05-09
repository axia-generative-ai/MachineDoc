import { apiClient } from '../../../shared/api/apiClient';

export type ActionStatusValue = '완료' | '부분 완료' | '추가 점검 필요' | '조치 불가';

export const ACTION_STATUS_OPTIONS: ActionStatusValue[] = ['완료', '부분 완료', '추가 점검 필요', '조치 불가'];

export type ActionLogItem = {
  actionLogId: number;
  historyId: number;
  actionStatus: ActionStatusValue;
  comment: string | null;
  duration: number | null;
  createdAt: string;
  query: string;
  searchStatus: string;
  searchCreatedAt: string | null;
};

type BackendActionLogWithHistory = {
  action_log_id: number;
  history_id: number;
  action_sta: ActionStatusValue;
  comment: string | null;
  duration: number | null;
  created_at: string | null;
  query: string;
  search_status: string;
  search_created_at: string | null;
};

type BackendActionLog = {
  action_log_id: number;
  history_id: number;
  action_sta: ActionStatusValue;
  comment: string | null;
  duration: number | null;
  created_at: string | null;
};

export const actionLogApi = {
  async listMine(limit = 50): Promise<ActionLogItem[]> {
    const { data } = await apiClient.get<BackendActionLogWithHistory[]>('/search/actions', { params: { limit } });
    return data.map((row) => ({
      actionLogId: row.action_log_id,
      historyId: row.history_id,
      actionStatus: row.action_sta,
      comment: row.comment,
      duration: row.duration,
      createdAt: row.created_at ?? '',
      query: row.query,
      searchStatus: row.search_status,
      searchCreatedAt: row.search_created_at,
    }));
  },

  async upsert(historyId: number, body: { actionStatus: ActionStatusValue; comment?: string; duration?: number }) {
    const { data } = await apiClient.post<BackendActionLog>(`/search/history/${historyId}/action`, {
      action_sta: body.actionStatus,
      comment: body.comment ?? null,
      duration: body.duration ?? null,
    });
    return {
      actionLogId: data.action_log_id,
      historyId: data.history_id,
      actionStatus: data.action_sta,
      comment: data.comment,
      duration: data.duration,
      createdAt: data.created_at ?? '',
    };
  },
};
