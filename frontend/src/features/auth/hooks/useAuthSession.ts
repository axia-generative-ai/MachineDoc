import { useEffect, useState } from 'react';

import {
  authSessionStorage,
  AUTH_SESSION_CHANGE_EVENT,
} from '../../../shared/storage/authSession.storage';

export function useAuthSession() {
  const [session, setSession] = useState(() => authSessionStorage.getSession());

  useEffect(() => {
    const sync = () => setSession(authSessionStorage.getSession());

    // 같은 탭에서의 변경 (로그인/로그아웃 직후) — custom event.
    window.addEventListener(AUTH_SESSION_CHANGE_EVENT, sync);
    // 다른 탭에서의 변경 — 표준 storage 이벤트.
    window.addEventListener('storage', sync);

    return () => {
      window.removeEventListener(AUTH_SESSION_CHANGE_EVENT, sync);
      window.removeEventListener('storage', sync);
    };
  }, []);

  return {
    session,
    user: session?.user ?? null,
    isAuthenticated: Boolean(session?.accessToken),
  };
}
