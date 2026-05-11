import type { User } from '../../../entities/user/model/user.types';

export interface AdminUserRepository {
  getPendingUsers(): Promise<User[]>;
  approveUser(userId: string): Promise<User>;
}
