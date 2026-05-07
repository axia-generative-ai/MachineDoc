const ACCESS_TOKEN_KEY = 'factoryguard.accessToken';

export const authTokenStorage = {
  getAccessToken() {
    return window.localStorage.getItem(ACCESS_TOKEN_KEY);
  },
  setAccessToken(token: string) {
    window.localStorage.setItem(ACCESS_TOKEN_KEY, token);
  },
  clear() {
    window.localStorage.removeItem(ACCESS_TOKEN_KEY);
  },
};
