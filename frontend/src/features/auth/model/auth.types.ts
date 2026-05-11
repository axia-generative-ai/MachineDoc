import type { User } from '../../../entities/user/model/user.types';

export type LoginCommand = {
  email: string;
  password: string;
};

export type SignupCommand = {
  name: string;
  email: string;
  password: string;
  department: string;
  role: Exclude<User['role'], 'ADMIN'>;
};

export type AuthSession = {
  accessToken: string;
  tokenType: string;
  user: User;
};
