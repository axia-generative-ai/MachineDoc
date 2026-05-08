import type { AuthSession, LoginCommand, SignupCommand } from '../model/auth.types';

export interface AuthRepository {
  login(command: LoginCommand): Promise<AuthSession>;
  signup(command: SignupCommand): Promise<void>;
  logout(): Promise<void>;
}
