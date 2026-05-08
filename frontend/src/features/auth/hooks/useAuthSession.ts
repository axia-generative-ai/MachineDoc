import { useMemo } from 'react';

import { authSessionStorage } from '../../../shared/storage/authSession.storage';

export function useAuthSession() {
  const session = useMemo(() => authSessionStorage.getSession(), []);

  return {
    session,
    user: session?.user ?? null,
    isAuthenticated: Boolean(session?.accessToken),
  };
}
