import { apiClient } from '../../../shared/api/apiClient';
import type { ErrorSearchCommand, ErrorSearchResult } from '../model/errorSearch.types';

type BackendErrorSearchResponse = {
  status?: string;
  analysis?: string;
  solution?: string;
  [key: string]: unknown;
};

function toText(value: unknown, fallback: string) {
  return typeof value === 'string' && value.trim() ? value : fallback;
}

function mapErrorSearchResult(command: ErrorSearchCommand, data: BackendErrorSearchResponse): ErrorSearchResult {
  if (data.status === 'mock_success') {
    return {
      keyword: command.errorCode,
      status: 'MOCK_COMPLETED',
      analysis: 'AI 서버 연동 전 테스트 응답입니다. 오류 코드 기준으로 관련 매뉴얼을 조회했습니다.',
      solution: '설비 상태를 확인하고, 관련 매뉴얼의 조치 절차에 따라 점검을 진행하세요.',
      raw: data,
    };
  }

  return {
    keyword: command.errorCode,
    status: toText(data.status, 'COMPLETED'),
    analysis: toText(data.analysis, 'AI 분석 결과를 불러왔습니다.'),
    solution: toText(data.solution, '관련 매뉴얼을 확인한 뒤 권장 조치를 진행하세요.'),
    raw: data,
  };
}

export const errorSearchApi = {
  async searchByCode(command: ErrorSearchCommand) {
    const { data } = await apiClient.get<BackendErrorSearchResponse>('/search/code', {
      params: {
        error_code: command.errorCode,
      },
    });

    return mapErrorSearchResult(command, data);
  },
};
