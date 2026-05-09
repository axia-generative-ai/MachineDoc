import type { AuthSession } from '../../features/auth/model/auth.types';

const AUTH_SESSION_KEY = 'factoryguard.authSession';
// 같은 탭 내에서 storage 이벤트가 발생하지 않으므로 custom event로 보강.
// useAuthSession 훅이 이걸 구독해서 로그인/로그아웃 직후 즉시 재렌더한다.
export const AUTH_SESSION_CHANGE_EVENT = 'factoryguard:auth-session-change';

function emitChange() {
  if (typeof window === 'undefined') return;
  window.dispatchEvent(new Event(AUTH_SESSION_CHANGE_EVENT));
}

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
    emitChange();
  },
  clear() {
    window.localStorage.removeItem(AUTH_SESSION_KEY);
    emitChange();
  },
};
