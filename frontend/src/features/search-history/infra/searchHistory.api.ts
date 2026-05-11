import { apiClient } from '../../../shared/api/apiClient';

export type SearchHistoryStatus = 'COMPLETED' | 'INVALID_CODE' | 'AI_ERROR' | string;

export type SearchHistoryItem = {
  historyId: number;
  userId: number;
  query: string;
  resultSummary: string;
  status: SearchHistoryStatus;
  createdAt: string;
};

type BackendSearchHistory = {
  history_id: number;
  user_id: number;
  query: string;
  result_content: string;
  status: string;
  created_at: string | null;
};

function summarizeResult(raw: string, status: string): string {
  if (status === 'INVALID_CODE') return '등록되지 않은 코드';
  if (status === 'AI_ERROR') return 'AI 분석 실패';
  try {
    const parsed = JSON.parse(raw) as { analysis?: string; solution?: string };
    if (typeof parsed.analysis === 'string' && parsed.analysis.trim()) {
      return parsed.analysis.replace(/[#*`\n\r]+/g, ' ').slice(0, 80) + (parsed.analysis.length > 80 ? '...' : '');
    }
    if (typeof parsed.solution === 'string' && parsed.solution.trim()) {
      return parsed.solution.split('\n')[0].slice(0, 80);
    }
  } catch {
    /* not JSON */
  }
  return raw.slice(0, 80);
}

export const searchHistoryApi = {
  async listMine(params: { limit?: number; status?: SearchHistoryStatus } = {}): Promise<SearchHistoryItem[]> {
    const { data } = await apiClient.get<BackendSearchHistory[]>('/search/history', {
      params: { limit: params.limit, status: params.status },
    });
    return data.map((row) => ({
      historyId: row.history_id,
      userId: row.user_id,
      query: row.query,
      resultSummary: summarizeResult(row.result_content, row.status),
      status: row.status,
      createdAt: row.created_at ?? '',
    }));
  },
};
