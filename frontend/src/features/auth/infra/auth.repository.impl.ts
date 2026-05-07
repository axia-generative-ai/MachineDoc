import type { AuthRepository } from '../domain/auth.repository';
import { authApi } from './auth.api';

export const authRepositoryImpl: AuthRepository = {
  login: authApi.login,
  signup: authApi.signup,
  logout: authApi.logout,
};
