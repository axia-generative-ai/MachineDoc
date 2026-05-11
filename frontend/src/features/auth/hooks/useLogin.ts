import { useState } from 'react';

import { ApiError } from '../../../shared/api/apiError';
import { authSessionStorage } from '../../../shared/storage/authSession.storage';
import { authTokenStorage } from '../../../shared/storage/authToken.storage';
import { AuthPolicyError } from '../domain/authPolicy';
import { authRepositoryImpl } from '../infra/auth.repository.impl';
import type { AuthSession, LoginCommand } from '../model/auth.types';
import { loginUseCase } from '../usecase/login.usecase';

type LoginState = {
  isLoading: boolean;
  errorMessage: string | null;
};

type LoginOptions = {
  onSuccess?: (session: AuthSession) => void;
};

function getLoginErrorMessage(error: unknown) {
  if (error instanceof AuthPolicyError) {
    return error.message;
  }

  if (error instanceof ApiError) {
    if (error.status === 400) return '이메일 또는 비밀번호가 올바르지 않습니다.';
    if (error.status === 403) return '승인 대기 중이거나 이미 로그인 중인 계정입니다.';
    return error.message;
  }

  return '로그인 중 문제가 발생했습니다.';
}

export function useLogin(options: LoginOptions = {}) {
  const [state, setState] = useState<LoginState>({
    isLoading: false,
    errorMessage: null,
  });

  const login = async (command: LoginCommand) => {
    setState({ isLoading: true, errorMessage: null });

    try {
      const session = await loginUseCase(authRepositoryImpl, command);

      // 로그인 성공 후 다음 요청부터 Authorization 헤더가 붙도록 토큰과 세션을 저장한다.
      authTokenStorage.setTokens({
        accessToken: session.accessToken,
      });
      authSessionStorage.setSession(session);

      setState({ isLoading: false, errorMessage: null });
      options.onSuccess?.(session);

      return session;
    } catch (error) {
      const errorMessage = getLoginErrorMessage(error);
      setState({ isLoading: false, errorMessage });
      return null;
    }
  };

  return {
    login,
    isLoading: state.isLoading,
    errorMessage: state.errorMessage,
  };
}
