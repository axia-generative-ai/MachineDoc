import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

import { authSessionStorage } from '../../../shared/storage/authSession.storage';
import { authTokenStorage } from '../../../shared/storage/authToken.storage';
import { authRepositoryImpl } from '../infra/auth.repository.impl';
import { logoutUseCase } from '../usecase/logout.usecase';

export function useLogout() {
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);

  const logout = async () => {
    if (isLoading) return;

    setIsLoading(true);

    try {
      await logoutUseCase(authRepositoryImpl);
    } finally {
      // 로그아웃 API가 실패해도 프론트 세션은 정리해서 잠긴 화면에 남지 않게 한다.
      authTokenStorage.clear();
      authSessionStorage.clear();
      setIsLoading(false);
      navigate('/login', { replace: true });
    }
  };

  return {
    logout,
    isLoading,
  };
}
