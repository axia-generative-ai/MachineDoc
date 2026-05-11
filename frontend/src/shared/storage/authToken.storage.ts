const ACCESS_TOKEN_KEY = 'MachineDoc.accessToken';
// Refresh token은 httpOnly 쿠키로 이전. localStorage 키는 legacy 잔여물 제거용으로만 유지.
const LEGACY_REFRESH_TOKEN_KEY = 'MachineDoc.refreshToken';

export const authTokenStorage = {
  getAccessToken() {
    return window.localStorage.getItem(ACCESS_TOKEN_KEY);
  },
  setAccessToken(token: string) {
    window.localStorage.setItem(ACCESS_TOKEN_KEY, token);
  },
  setTokens(tokens: { accessToken: string }) {
    window.localStorage.setItem(ACCESS_TOKEN_KEY, tokens.accessToken);
  },
  clear() {
    window.localStorage.removeItem(ACCESS_TOKEN_KEY);
    window.localStorage.removeItem(LEGACY_REFRESH_TOKEN_KEY);
  },
};
