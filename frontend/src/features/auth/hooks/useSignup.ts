import { useState } from 'react';

import { ApiError } from '../../../shared/api/apiError';
import { AuthPolicyError } from '../domain/authPolicy';
import { authRepositoryImpl } from '../infra/auth.repository.impl';
import type { SignupCommand } from '../model/auth.types';
import { signupUseCase } from '../usecase/signup.usecase';

type SignupState = {
  isLoading: boolean;
  errorMessage: string | null;
  successMessage: string | null;
};

type SignupOptions = {
  onSuccess?: () => void;
};

function getSignupErrorMessage(error: unknown) {
  if (error instanceof AuthPolicyError) {
    return error.message;
  }

  if (error instanceof ApiError) {
    if (error.status === 400) return '이미 사용 중인 이메일입니다.';
    if (error.status === 422) return '입력한 회원가입 정보를 다시 확인해주세요.';
    return error.message;
  }

  return '회원가입 중 문제가 발생했습니다.';
}

export function useSignup(options: SignupOptions = {}) {
  const [state, setState] = useState<SignupState>({
    isLoading: false,
    errorMessage: null,
    successMessage: null,
  });

  const signup = async (command: SignupCommand) => {
    setState({ isLoading: true, errorMessage: null, successMessage: null });

    try {
      await signupUseCase(authRepositoryImpl, command);
      setState({
        isLoading: false,
        errorMessage: null,
        successMessage: '회원가입 요청이 완료되었습니다. 관리자 승인 후 로그인할 수 있습니다.',
      });
      options.onSuccess?.();
      return true;
    } catch (error) {
      setState({
        isLoading: false,
        errorMessage: getSignupErrorMessage(error),
        successMessage: null,
      });
      return false;
    }
  };

  return {
    signup,
    isLoading: state.isLoading,
    errorMessage: state.errorMessage,
    successMessage: state.successMessage,
  };
}
