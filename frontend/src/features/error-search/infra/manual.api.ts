import { apiClient } from '../../../shared/api/apiClient';
import { ApiError } from '../../../shared/api/apiError';
import { authTokenStorage } from '../../../shared/storage/authToken.storage';

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

function mapManual(data: BackendManual): RelatedManual {
  return {
    manualId: data.manual_id,
    title: data.title,
    category: data.category,
    version: data.version,
    savedAt: data.saved_at,
  };
}

export type ErrorCodeMapping = {
  errorCodeId: number;
  codeName: string;
  manualId: number;
  manualTitle: string;
  category: string;
  version: string;
};

type BackendErrorCodeMapping = {
  error_code_id: number;
  code_name: string;
  manual_id: number;
  manual_title: string;
  category: string;
  version: string;
};

export const manualApi = {
  async search(params: { equipmentCode?: string; category?: string } = {}) {
    const { data } = await apiClient.get<BackendManual[]>('/manual/search', {
      params: {
        equipment_code: params.equipmentCode,
        category: params.category,
      },
    });
    return data.map(mapManual);
  },

  async openPdf(manualId: number, page?: number) {
    const { data } = await apiClient.get<Blob>(`/manual/${manualId}`, {
      responseType: 'blob',
    });
    const baseUrl = URL.createObjectURL(data);
    // PDF.js / Chrome PDF viewer가 모두 #page=N fragment를 지원한다.
    const targetUrl = page && page > 0 ? `${baseUrl}#page=${page}` : baseUrl;
    const win = window.open(targetUrl, '_blank', 'noopener,noreferrer');
    setTimeout(() => URL.revokeObjectURL(baseUrl), 60_000);
    return win;
  },

  async fetchPdfUrl(manualId: number, page?: number): Promise<{ url: string; revoke: () => void }> {
    // 패널 내 iframe 임베드용. 호출자가 unmount/교체 시 revoke를 직접 호출한다.
    const { data } = await apiClient.get<Blob>(`/manual/${manualId}`, {
      responseType: 'blob',
    });
    const blobUrl = URL.createObjectURL(data);
    const targetUrl = page && page > 0 ? `${blobUrl}#page=${page}&toolbar=1&view=FitH` : blobUrl;
    return { url: targetUrl, revoke: () => URL.revokeObjectURL(blobUrl) };
  },

  async upload(input: {
    title: string;
    category: string;
    version: string;
    equipmentId?: number | null;
    errorCodes: string[];
    file: File;
  }): Promise<{ manualId: number; title: string; message: string }> {
    // axios + FormData + interceptor 조합에서 Content-Type/boundary 충돌이 잦아
    // 매뉴얼 업로드만 fetch로 직접 보낸다. baseURL/토큰은 apiClient와 동일한 소스 사용.
    const formData = new FormData();
    formData.append('title', input.title);
    formData.append('category', input.category);
    formData.append('version', input.version);
    if (input.equipmentId != null) {
      formData.append('equipment_id', String(input.equipmentId));
    }
    for (const code of input.errorCodes) {
      formData.append('error_codes', code);
    }
    formData.append('file', input.file);

    const baseURL = apiClient.defaults.baseURL ?? '';
    const url = `${baseURL.replace(/\/$/, '')}/manual/upload`;
    const accessToken = authTokenStorage.getAccessToken();

    const response = await fetch(url, {
      method: 'POST',
      body: formData,
      headers: accessToken ? { Authorization: `Bearer ${accessToken}` } : undefined,
    });

    if (!response.ok) {
      let detail = `HTTP ${response.status}`;
      try {
        const data = (await response.json()) as { detail?: string };
        if (typeof data.detail === 'string') detail = data.detail;
      } catch {
        // body가 JSON이 아니면 status만 사용
      }
      throw new ApiError(detail, response.status);
    }

    const data = (await response.json()) as { manual_id: number; title: string; message: string };
    return { manualId: data.manual_id, title: data.title, message: data.message };
  },

  async listMine(): Promise<RelatedManual[]> {
    const { data } = await apiClient.get<BackendManual[]>('/manual/mine');
    return data.map(mapManual);
  },

  async listErrorCodeMappings(): Promise<ErrorCodeMapping[]> {
    const { data } = await apiClient.get<BackendErrorCodeMapping[]>('/manual/error-codes');
    return data.map((row) => ({
      errorCodeId: row.error_code_id,
      codeName: row.code_name,
      manualId: row.manual_id,
      manualTitle: row.manual_title,
      category: row.category,
      version: row.version,
    }));
  },
};
