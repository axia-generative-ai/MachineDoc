import { useEffect, useState } from 'react';

import type { User } from '../../../entities/user/model/user.types';
import { ApiError } from '../../../shared/api/apiError';
import { adminUserRepositoryImpl } from '../infra/adminUser.repository.impl';
import { getPendingUsersUseCase } from '../usecase/getPendingUsers.usecase';

type PendingUsersState = {
  users: User[];
  isLoading: boolean;
  errorMessage: string | null;
};

function getPendingUsersErrorMessage(error: unknown) {
  if (error instanceof ApiError) {
    if (error.status === 403) return '사용자 승인 목록을 조회할 관리자 권한이 없습니다.';
    return error.message;
  }

  return '승인 대기 사용자 목록을 불러오지 못했습니다.';
}

export function usePendingUsers() {
  const [state, setState] = useState<PendingUsersState>({
    users: [],
    isLoading: true,
    errorMessage: null,
  });

  const fetchPendingUsers = async () => {
    setState((prev) => ({ ...prev, isLoading: true, errorMessage: null }));

    try {
      const users = await getPendingUsersUseCase(adminUserRepositoryImpl);
      setState({ users, isLoading: false, errorMessage: null });
    } catch (error) {
      setState({
        users: [],
        isLoading: false,
        errorMessage: getPendingUsersErrorMessage(error),
      });
    }
  };

  const removePendingUser = (userId: string) => {
    setState((prev) => ({
      ...prev,
      users: prev.users.filter((user) => user.id !== userId),
    }));
  };

  useEffect(() => {
    void fetchPendingUsers();
  }, []);

  return {
    ...state,
    refetch: fetchPendingUsers,
    removePendingUser,
  };
}
