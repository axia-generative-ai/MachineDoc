import { useEffect, useRef, useState } from 'react';

import { ApiError } from '../../../shared/api/apiError';
import { errorSearchRepositoryImpl } from '../infra/errorSearch.repository.impl';
import type { ErrorSearchResult } from '../model/errorSearch.types';
import { ErrorSearchPolicyError, searchErrorCodeUseCase } from '../usecase/searchErrorCode.usecase';

type ErrorCodeSearchState = {
  result: ErrorSearchResult | null;
  isLoading: boolean;
  errorMessage: string | null;
};

function getSearchErrorMessage(error: unknown) {
  if (error instanceof ErrorSearchPolicyError) {
    return error.message;
  }

  if (error instanceof ApiError) {
    if (error.status === 401) return '로그인 정보가 만료되었습니다. 다시 로그인해주세요.';
    if (error.status === 404) return '등록되지 않은 오류 코드입니다.';
    if (error.status === 503) return 'AI 분석 서버 응답이 지연되고 있습니다.';
    return error.message;
  }

  return '오류 검색 중 문제가 발생했습니다.';
}

export function useErrorCodeSearch(errorCode: string) {
  const [state, setState] = useState<ErrorCodeSearchState>({
    result: null,
    isLoading: true,
    errorMessage: null,
  });
  // StrictMode dev 이중 effect로 backend search_history가 2건 INSERT 되는 걸 막는다.
  const lastFetchedRef = useRef<string | null>(null);

  const search = async () => {
    setState({ result: null, isLoading: true, errorMessage: null });

    try {
      const result = await searchErrorCodeUseCase(errorSearchRepositoryImpl, { errorCode });
      setState({ result, isLoading: false, errorMessage: null });
    } catch (error) {
      setState({
        result: null,
        isLoading: false,
        errorMessage: getSearchErrorMessage(error),
      });
    }
  };

  useEffect(() => {
    if (lastFetchedRef.current === errorCode) return;
    lastFetchedRef.current = errorCode;
    void search();
  }, [errorCode]);

  const refetch = () => {
    lastFetchedRef.current = errorCode;
    return search();
  };

  return {
    ...state,
    refetch,
  };
}
