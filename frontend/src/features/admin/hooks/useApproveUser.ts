import { useState } from 'react';

import { ApiError } from '../../../shared/api/apiError';
import { adminUserRepositoryImpl } from '../infra/adminUser.repository.impl';
import { approveUserUseCase } from '../usecase/approveUser.usecase';

function getApproveUserErrorMessage(error: unknown) {
  if (error instanceof ApiError) {
    if (error.status === 403) return '사용자를 승인할 관리자 권한이 없습니다.';
    return error.message;
  }

  return '사용자 승인 중 문제가 발생했습니다.';
}

export function useApproveUser() {
  const [approvingUserId, setApprovingUserId] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const approveUser = async (userId: string) => {
    setApprovingUserId(userId);
    setErrorMessage(null);

    try {
      await approveUserUseCase(adminUserRepositoryImpl, userId);
      setApprovingUserId(null);
      return true;
    } catch (error) {
      setApprovingUserId(null);
      setErrorMessage(getApproveUserErrorMessage(error));
      return false;
    }
  };

  return {
    approveUser,
    approvingUserId,
    errorMessage,
  };
}
