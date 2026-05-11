import type { UserRole, UserState } from '../../../entities/user/model/user.types';
import { apiClient } from '../../../shared/api/apiClient';
import type { AuthSession, LoginCommand, SignupCommand } from '../model/auth.types';

type BackendAuthSession = {
  access_token: string;
  token_type: string;
  user_info: {
    user_id?: number;
    email: string;
    name: string;
    department: string;
    role: string;
    state: string;
  };
};

const backendRoleValues: Record<Exclude<UserRole, 'ADMIN'>, string> = {
  WORKER: '작업자',
  ENGINEER: '엔지니어',
};

function normalizeRole(role: string): UserRole {
  if (role === 'ADMIN' || role.includes('관리')) return 'ADMIN';
  if (role === 'ENGINEER' || role.includes('엔지니어')) return 'ENGINEER';
  return 'WORKER';
}

function normalizeState(state: string): UserState {
  if (state === 'LOGIN' || state.includes('로그인')) return 'LOGIN';
  if (state === 'PENDING' || state.includes('승인')) return 'PENDING';
  return 'LOGOUT';
}

function mapAuthSession(data: BackendAuthSession): AuthSession {
  return {
    accessToken: data.access_token,
    tokenType: data.token_type,
    user: {
      id: String(data.user_info.user_id ?? data.user_info.email),
      email: data.user_info.email,
      name: data.user_info.name,
      department: data.user_info.department,
      role: normalizeRole(data.user_info.role),
      state: normalizeState(data.user_info.state),
    },
  };
}

export const authApi = {
  async login(command: LoginCommand) {
    const formData = new URLSearchParams();
    formData.append('username', command.email);
    formData.append('password', command.password);

    const { data } = await apiClient.post<BackendAuthSession>('/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });

    return mapAuthSession(data);
  },
  async signup(command: SignupCommand) {
    await apiClient.post('/auth/register', {
      email: command.email,
      password: command.password,
      name: command.name,
      department: command.department,
      role: backendRoleValues[command.role],
    });
  },
  async logout() {
    await apiClient.post('/auth/logout');
  },
};
