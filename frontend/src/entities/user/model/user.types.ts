export type UserRole = 'WORKER' | 'ENGINEER' | 'ADMIN';
export type UserState = 'PENDING' | 'LOGOUT' | 'LOGIN';

export type User = {
  id: string;
  name: string;
  email: string;
  role: UserRole;
  department: string;
  state?: UserState;
};
