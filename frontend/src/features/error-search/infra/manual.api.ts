import { apiClient } from '../../../shared/api/apiClient';

export type ManualSummary = {
  manual_id: number;
  title: string;
  category: string;
  version: string;
  saved_at: string;
};

export const manualApi = {
  async searchManuals() {
    const { data } = await apiClient.get<ManualSummary[] | ManualSummary>('/manual/search');
    return Array.isArray(data) ? data : [data];
  },

  async getManualPdf(manualId: number) {
    const { data } = await apiClient.get<Blob>(`/manual/${manualId}`, {
      responseType: 'blob',
    });

    return data;
  },
};
