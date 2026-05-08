import type { User, UserRole, UserState } from '../../../entities/user/model/user.types';
import { apiClient } from '../../../shared/api/apiClient';

type BackendUser = {
  user_id: number;
  email: string;
  name: string;
  department: string;
  role: string;
  state: string;
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

function mapUser(user: BackendUser): User {
  return {
    id: String(user.user_id),
    email: user.email,
    name: user.name,
    department: user.department,
    role: normalizeRole(user.role),
    state: normalizeState(user.state),
  };
}

export const adminUserApi = {
  async getPendingUsers() {
    const { data } = await apiClient.get<BackendUser[]>('/users/pending');
    return data.map(mapUser);
  },
  async approveUser(userId: string) {
    const { data } = await apiClient.patch<BackendUser>(`/users/${userId}`, {
      state: '로그아웃',
    });
    return mapUser(data);
  },
};
