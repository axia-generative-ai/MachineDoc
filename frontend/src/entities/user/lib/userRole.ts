import type { UserRole } from '../model/user.types';

export function isAdminRole(role: UserRole) {
  return role === 'ADMIN';
}
