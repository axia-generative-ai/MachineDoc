import type { AuthSession } from '../../features/auth/model/auth.types';

const AUTH_SESSION_KEY = 'factoryguard.authSession';

export const authSessionStorage = {
  getSession() {
    const session = window.localStorage.getItem(AUTH_SESSION_KEY);

    if (!session) return null;

    try {
      return JSON.parse(session) as AuthSession;
    } catch {
      window.localStorage.removeItem(AUTH_SESSION_KEY);
      return null;
    }
  },
  setSession(session: AuthSession) {
    window.localStorage.setItem(AUTH_SESSION_KEY, JSON.stringify(session));
  },
  clear() {
    window.localStorage.removeItem(AUTH_SESSION_KEY);
  },
};
