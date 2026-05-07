import type { LoginCommand, SignupCommand, AuthSession } from '../model/auth.types';
import { apiClient } from '../../../shared/api/apiClient';

type BackendAuthSession = {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user_info: {
    user_id?: number;
    email: string;
    name: string;
    department: string;
    role: AuthSession['user']['role'];
    state: NonNullable<AuthSession['user']['state']>;
  };
};

function mapAuthSession(data: BackendAuthSession): AuthSession {
  return {
    accessToken: data.access_token,
    refreshToken: data.refresh_token,
    tokenType: data.token_type,
    user: {
      id: String(data.user_info.user_id ?? data.user_info.email),
      email: data.user_info.email,
      name: data.user_info.name,
      department: data.user_info.department,
      role: data.user_info.role,
      state: data.user_info.state,
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
    await apiClient.post('/auth/register', command);
  },
  async logout() {
    await apiClient.post('/auth/logout');
  },
};
