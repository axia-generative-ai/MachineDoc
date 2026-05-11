import { apiClient } from '../../../shared/api/apiClient';

export type PromptItem = {
  key: string;
  content: string;
  description: string | null;
  updatedAt: string | null;
};

type BackendPrompt = {
  key: string;
  content: string;
  description: string | null;
  updated_at: string | null;
};

function mapPrompt(data: BackendPrompt): PromptItem {
  return {
    key: data.key,
    content: data.content,
    description: data.description,
    updatedAt: data.updated_at,
  };
}

export const promptApi = {
  async list() {
    const { data } = await apiClient.get<BackendPrompt[]>('/prompts');
    return data.map(mapPrompt);
  },
  async get(key: string) {
    const { data } = await apiClient.get<BackendPrompt>(`/prompts/${key}`);
    return mapPrompt(data);
  },
  async upsert(key: string, body: { content: string; description?: string }) {
    const { data } = await apiClient.put<BackendPrompt>(`/prompts/${key}`, body);
    return mapPrompt(data);
  },
};
