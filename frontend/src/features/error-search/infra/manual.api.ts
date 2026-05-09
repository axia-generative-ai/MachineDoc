import { apiClient } from '../../../shared/api/apiClient';
import { env } from '../../../shared/config/env';

export type ManualSummary = {
  manual_id: number;
  title: string;
  category: string;
  version: string;
  saved_at: string;
};

export type RelatedManual = {
  manualId: number;
  title: string;
  category: string;
  version: string;
  savedAt: string;
};

type BackendManual = {
  manual_id: number;
  title: string;
  category: string;
  version: string;
  saved_at: string;
};

function toRelatedManual(data: BackendManual): RelatedManual {
  return {
    manualId: data.manual_id,
    title: data.title,
    category: data.category,
    version: data.version,
    savedAt: data.saved_at,
  };
}

type UploadInput = {
  title: string;
  category: string;
  version: string;
  equipmentId: number | null;
  errorCodes: string[];
  file: File;
};

type UploadResponse = {
  manualId: number;
  title: string;
  message: string;
};

export const manualApi = {
  async searchManuals() {
    const { data } = await apiClient.get<ManualSummary[] | ManualSummary>('/manual/search');
    return Array.isArray(data) ? data : [data];
  },

  async listMine(): Promise<RelatedManual[]> {
    const { data } = await apiClient.get<BackendManual[]>('/manual/mine');
    return data.map(toRelatedManual);
  },

  async getManualPdf(manualId: number) {
    const { data } = await apiClient.get<Blob>(`/manual/${manualId}`, {
      responseType: 'blob',
    });

    return data;
  },

  async openPdf(manualId: number) {
    const url = `${env.apiBaseUrl}/manual/${manualId}`;
    window.open(url, '_blank', 'noopener,noreferrer');
  },

  async upload(input: UploadInput): Promise<UploadResponse> {
    const form = new FormData();
    form.append('title', input.title);
    form.append('category', input.category);
    form.append('version', input.version);
    if (input.equipmentId !== null && input.equipmentId !== undefined) {
      form.append('equipment_id', String(input.equipmentId));
    }
    for (const code of input.errorCodes) {
      form.append('error_codes', code);
    }
    form.append('file', input.file);

    const { data } = await apiClient.post<{ manual_id: number; title: string; message: string }>(
      '/manual/upload',
      form,
      { headers: { 'Content-Type': 'multipart/form-data' } },
    );
    return {
      manualId: data.manual_id,
      title: data.title,
      message: data.message,
    };
  },
};
